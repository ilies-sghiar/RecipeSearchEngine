"""
API principale de recherche et récupération de recettes de cuisine.

Ce module fournit des endpoints FastAPI pour :
- Rechercher des noms de recettes à partir d'une requête texte en utilisant des embeddings sémantiques.
- Connecter à Elasticsearch pour effectuer les recherches KNN et récupérer les recettes.
- Générer des embeddings de texte via le modèle SentenceTransformer "all-MiniLM-L6-v2".

Endpoints principaux :
- POST /search-names/ : Rechercher des noms de recettes correspondant à une requête.
- POST /get-document/ : (optionnel) Récupérer la recette complète par son nom.

Note :
- Le module utilise Elasticsearch local sans vérification SSL pour les tests.
- Les embeddings sont normalisés avant la recherche KNN.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer

from elasticsearch import Elasticsearch

# Initialisation de FastAPI
app = FastAPI()

# Initialisation du client Elasticsearch
es = Elasticsearch(
    ["http://localhost:9200"],  # URL du noeud
    verify_certs=False,  # Optionnel : pas de vérification de certificat
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # N'importe quelle origine
    allow_credentials=True,
    allow_methods=["*"],  # N'importe quelle méthode
    allow_headers=["*"],  # N'importe quel en-tête
)

# Chargement du modèle SentenceTransformer
model = SentenceTransformer("all-MiniLM-L6-v2")


class QueryRequest(BaseModel):
    """
    Corps de requête pour une recherche sémantique.

    Attributs :
        query (str) : Le texte de la requête pour la recherche sémantique.
    """

    query: str


class NameRequest(BaseModel):
    """
    Corps de requête pour récupérer un document par son nom.

    Attributs :
        name (str) : Le nom du document à récupérer.
    """

    name: str


def generate_embedding(text: str, model: SentenceTransformer) -> list[float]:
    """
    Génère un vecteur d'embedding normalisé pour un texte donné.

    Utilise un modèle SentenceTransformer pour encoder le texte en un vecteur
    normalisé. Retourne un vecteur nul si le texte est vide.

    Args:
        text (str) : Le texte à encoder.
        model (SentenceTransformer) : Modèle SentenceTransformer préchargé.

    Returns:
        list[float] : Vecteur normalisé représentant l'embedding du texte.
    """
    text = text.strip() if text else ""

    if not text:
        return [0.0] * model.get_sentence_embedding_dimension()

    embedding = model.encode(text, normalize_embeddings=True)
    return embedding.tolist()


def search_names(query_text: str) -> list[str]:
    """
    Effectue une recherche sémantique KNN dans Elasticsearch pour trouver
    les noms de recettes les plus proches d'une requête donnée.

    Génère un embedding pour la requête et utilise Elasticsearch pour
    retrouver les noms de recettes les plus similaires.

    Args:
        query_text (str) : Texte de la requête pour la recherche sémantique.

    Returns:
        list[str] : Liste des noms de recettesles plus pertinents dans l'index Elasticsearch.

    Raises:
        HTTPException : Si la requête Elasticsearch échoue.
    """
    query_embedding = generate_embedding(query_text, model)

    query = {
        "knn": {
            "field": "embedding",
            "query_vector": query_embedding,
            "k": 10,
            "num_candidates": 30,
        },
        "_source": ["name"],
    }

    try:
        response = es.search(index="index_with_schema_combined", body=query)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Échec de la requête Elasticsearch : {e}"
        )

    names = [hit["_source"]["name"] for hit in response["hits"]["hits"]]
    return names


@app.post("/search-names/")
def search_names_endpoint(request: QueryRequest) -> dict[str, list[str]]:
    """
    Endpoint FastAPI pour effectuer une recherche sémantique de recette à partir d'une requête.

    Args:
        request (QueryRequest) : Corps de requête contenant le texte de recherche.

    Returns:
        dict[str, list[str]] : Réponse JSON contenant la liste des noms de recettes correspondants.
    """
    names = search_names(request.query)
    print(names)
    return {"names": names}


# Endpoint optionnel pour récupérer un document complet par nom
"""
@app.post("/get-document/")
def get_document_endpoint(request: NameRequest) -> dict[str, dict[str, str]]:
    \"\"\"
    Endpoint FastAPI pour récupérer un document par nom.

    Args:
        request (NameRequest) : Corps de requête contenant le nom du document.

    Returns:
        dict[str, dict[str, str]] : Réponse JSON contenant les champs du document.
    \"\"\"
    document = get_document_by_name(request.name)
    return {"document": document}


def get_document_by_name(name: str) -> dict[str, str]:
    \"\"\"
    Récupère une recette complète depuis Elasticsearch par son nom.

    Args:
        name (str) : Nom de la recette à récupérer.

    Returns:
        dict[str, str] : Champs du document (introduction, informations supplémentaires,
                         précautions, effets secondaires, instructions d'utilisation,
                         instructions de stockage).

    Raises:
        HTTPException : Si le document n'est pas trouvé ou si la requête Elasticsearch échoue.
    \"\"\"
    query = {"query": {"match": {"name": name}}}

    try:
        response = es.search(index="index_with_schema_combined", body=query)
        hits = response["hits"]["hits"]
        if not hits:
            raise HTTPException(status_code=404, detail="Document non trouvé")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Échec de la requête Elasticsearch : {e}")

    source = hits[0]["_source"]
    document = {
        "introduction": source.get("introduction", ""),
        "additional_info": source.get("additional_info", ""),
        "precautions": source.get("precautions", ""),
        "side_effects": source.get("side_effects", ""),
        "usage_instruction": source.get("usage_instruction", ""),
        "storage_instruction": source.get("storage_instruction", ""),
    }
    return document
"""
