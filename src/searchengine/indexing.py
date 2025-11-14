from elasticsearch import Elasticsearch
import logging
import json
import os
from sentence_transformers import SentenceTransformer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s - %(asctime)s - %(message)s",
    datefmt="%d-%m %H:%M:%S",
    handlers=[
        logging.FileHandler("index.log"),  # Log to a file
        logging.StreamHandler(),  # Log to console
    ],
)


def generate_embedding(text: str, model: SentenceTransformer) -> list[float]:
    text = text.strip() if text else ""

    # No text -> Null vector
    if not text:
        return [0.0] * model.get_sentence_embedding_dimension()

    # Embedding generation
    embedding = model.encode(text, normalize_embeddings=True)
    return embedding.tolist()

def initialize_es() -> Elasticsearch:
    """
    Initialize Elasticsearch client with SSL verification disabled (for local testing)
    """
    try:
        es = Elasticsearch(
            ["http://localhost:9200"],  # The node's URL
            verify_certs=False,  # Optional: No need for certificate verification since security is disabled
        )
    except Exception as e:
        logging.critical(f"Exception connecting to ES: {e}")
        exit()

    return es

def index_combined_documents(
    es: Elasticsearch,
    index_name: str,
    documents: list[dict],
    model: SentenceTransformer,
):
    """
    Indexe des documents avec leurs champs texte normalisés et embeddings.
    """
    for i, doc in enumerate(documents):
        try:
            # Fonction helper pour convertir n'importe quel champ en string
            def to_text(value):
                if value is None:
                    return ""
                if isinstance(value, list):
                    return ", ".join(str(item) for item in value)
                return str(value)
            
            # Gérer recipeInstructions spécifiquement
            instructions_text = ""
            recipe_instructions = doc.get("recipeInstructions", [])
            if isinstance(recipe_instructions, list):
                instructions_text = " ".join(
                    step.get("text", str(step)) if isinstance(step, dict) else str(step)
                    for step in recipe_instructions
                )
            else:
                instructions_text = to_text(recipe_instructions)
            
            # Normaliser tous les champs en texte
            name_text = to_text(doc.get("name"))
            description_text = to_text(doc.get("description"))
            ingredients_text = to_text(doc.get("recipeIngredient"))
            prep_time_text = to_text(doc.get("prepTime"))
            cook_time_text = to_text(doc.get("cookTime"))
            total_time_text = to_text(doc.get("totalTime"))
            category_text = to_text(doc.get("recipeCategory"))
            method_text = to_text(doc.get("cookingMethod"))
            cuisine_text = to_text(doc.get("recipeCuisine"))
            
            # Construire le texte à embedder
            text_to_embed = " ".join([
                name_text,
                description_text,
                ingredients_text,
                instructions_text,
                prep_time_text,
                cook_time_text,
                total_time_text,
                category_text,
                method_text,
                cuisine_text,
            ])
            
            # Générer l'embedding
            embedding = generate_embedding(text_to_embed, model)
            
            # Indexer UNIQUEMENT les champs normalisés + embedding
            doc_to_index = {
                "name": name_text,
                "description": description_text,
                "recipeIngredient": ingredients_text,
                "recipeInstructions": instructions_text,
                "prepTime": prep_time_text,
                "cookTime": cook_time_text,
                "totalTime": total_time_text,
                "recipeCategory": category_text,
                "cookingMethod": method_text,
                "recipeCuisine": cuisine_text,
                "embedding": embedding,
            }
            
            # Document indexing
            response = es.index(index=index_name, body=doc_to_index)
            logging.info(f"Document {i} indexé avec succès : {response['result']}")
            
        except Exception as e:
            logging.error(f"Erreur lors de l'indexation du document {i}: {e}")
            
def main():
    es = initialize_es()

    file_path = os.path.join(os.path.dirname(__file__), "recipes.json")
    print(file_path)
    with open(file_path, "r", encoding="utf-8") as f:
        print("hello")
        documents = json.load(f)

    logging.info(f"Loaded {len(documents)} documents.")

    model = SentenceTransformer("all-MiniLM-L6-v2")

    if not es.info():
        logging.critical("Elasticsearch cluster is not available.")
        exit()
    else:
        logging.info("Connected to Elasticsearch cluster.")

    index_combined_documents(
        es=es, index_name="index_with_schema_combined", documents=documents, model=model
    )