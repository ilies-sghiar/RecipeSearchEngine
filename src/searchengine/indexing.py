"""
Ce module permet de :
- Charger des documents JSON de recettes.
- Normaliser et concaténer les différents champs textuels.
- Générer des embeddings à l'aide d'un modèle SentenceTransformer.
- Indexer les documents et leurs embeddings dans Elasticsearch.
"""

import json
import logging
import os

from sentence_transformers import SentenceTransformer

from elasticsearch import Elasticsearch

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s - %(asctime)s - %(message)s",
    datefmt="%d-%m %H:%M:%S",
    handlers=[
        logging.FileHandler("index.log"),  # Log dans un fichier
        logging.StreamHandler(),  # Log dans la console
    ],
)


def generate_embedding(text: str, model: SentenceTransformer) -> list[float]:
    """
    Génère un vecteur d'embedding normalisé pour un texte donné.

    Args:
        text (str) : Le texte à encoder.
        model (SentenceTransformer) : Modèle SentenceTransformer préchargé.

    Returns:
        list[float] : Vecteur normalisé représentant l'embedding du texte.
                      Retourne un vecteur nul si le texte est vide.
    """
    text = text.strip() if text else ""

    if not text:
        return [0.0] * model.get_sentence_embedding_dimension()

    embedding = model.encode(text, normalize_embeddings=True)
    return embedding.tolist()


def initialize_es() -> Elasticsearch:
    """
    Initialise le client Elasticsearch avec la vérification SSL désactivée (pour tests locaux).

    Returns:
        Elasticsearch : Instance du client Elasticsearch.

    Raises:
        SystemExit : Si la connexion à Elasticsearch échoue.
    """
    try:
        es = Elasticsearch(
            ["http://localhost:9200"],  # URL du noeud
            verify_certs=False,  # Pas de vérification SSL pour tests locaux
        )
    except Exception as e:
        logging.critical(f"Exception lors de la connexion à Elasticsearch : {e}")
        exit()

    return es


def index_combined_documents(
    es: Elasticsearch,
    index_name: str,
    documents: list[dict],
    model: SentenceTransformer,
):
    """
    Indexe des documents de recettes dans Elasticsearch en normalisant les champs
    texte et en générant leurs embeddings.

    Args:
        es (Elasticsearch) : Instance du client Elasticsearch.
        index_name (str) : Nom de l'index Elasticsearch.
        documents (list[dict]) : Liste de documents de recettes à indexer.
        model (SentenceTransformer) : Modèle SentenceTransformer pour générer les embeddings.

    Returns:
        None

    Notes:
        - Tous les champs texte sont convertis en chaînes de caractères.
        - Les instructions de recette sont concaténées si elles sont en liste.
        - Chaque document est indexé individuellement avec son embedding.
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

            # Gestion spécifique de recipeInstructions
            instructions_text = ""
            recipe_instructions = doc.get("recipeInstructions", [])
            if isinstance(recipe_instructions, list):
                instructions_text = " ".join(
                    step.get("text", str(step)) if isinstance(step, dict) else str(step)
                    for step in recipe_instructions
                )
            else:
                instructions_text = to_text(recipe_instructions)

            # Normalisation de tous les champs
            name_text = to_text(doc.get("name"))
            description_text = to_text(doc.get("description"))
            ingredients_text = to_text(doc.get("recipeIngredient"))
            prep_time_text = to_text(doc.get("prepTime"))
            cook_time_text = to_text(doc.get("cookTime"))
            total_time_text = to_text(doc.get("totalTime"))
            category_text = to_text(doc.get("recipeCategory"))
            method_text = to_text(doc.get("cookingMethod"))
            cuisine_text = to_text(doc.get("recipeCuisine"))

            # Texte complet à transformer en embedding
            text_to_embed = " ".join(
                [
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
                ]
            )

            # Génération de l'embedding
            embedding = generate_embedding(text_to_embed, model)

            # Document à indexer
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

            # Indexation
            response = es.index(index=index_name, body=doc_to_index)
            logging.info(f"Document {i} indexé avec succès : {response['result']}")

        except Exception as e:
            logging.error(f"Erreur lors de l'indexation du document {i} : {e}")


def main():
    """
    Fonction principale d'indexation.

    - Initialise Elasticsearch.
    - Charge les documents depuis le fichier JSON.
    - Charge le modèle SentenceTransformer.
    - Vérifie la disponibilité du cluster Elasticsearch.
    - Indexe les documents avec leurs embeddings.
    """
    es = initialize_es()

    file_path = os.path.join(os.path.dirname(__file__), "recipes.json")
    with open(file_path, "r", encoding="utf-8") as f:
        documents = json.load(f)

    logging.info(f"{len(documents)} documents chargés.")

    model = SentenceTransformer("all-MiniLM-L6-v2")

    if not es.info():
        logging.critical("Cluster Elasticsearch indisponible.")
        exit()
    else:
        logging.info("Connexion au cluster Elasticsearch réussie.")

    index_combined_documents(
        es=es, index_name="index_with_schema_combined", documents=documents, model=model
    )


if __name__ == "__main__":
    main()
