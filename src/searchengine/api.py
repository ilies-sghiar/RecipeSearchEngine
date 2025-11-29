from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer

from elasticsearch import Elasticsearch

# Initialize FastAPI
app = FastAPI()

# Initialize Elasticsearch client
es = Elasticsearch(
    ["http://localhost:9200"],  # The node's URL
    verify_certs=False,  # Optional: No need for certificate verification since security is disabled
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # N'importe quelle origine
    allow_credentials=True,
    allow_methods=["*"],  # N'importe quelle méthode
    allow_headers=["*"],  # N'importe quel en-tête
)

# Load SentenceTransformer model
model = SentenceTransformer("all-MiniLM-L6-v2")


# Define Pydantic model for input
class QueryRequest(BaseModel):
    query: str


class NameRequest(BaseModel):
    name: str


# Function to generate embedding
def generate_embedding(text: str, model: SentenceTransformer) -> list[float]:
    text = text.strip() if text else ""

    # If no text -> Null vector
    if not text:
        return [0.0] * model.get_sentence_embedding_dimension()

    # Embedding Generation
    embedding = model.encode(text, normalize_embeddings=True)
    return embedding.tolist()


# Function to search names in Elasticsearch
def search_names(query_text: str):
    # Generate embedding for query
    query_embedding = generate_embedding(query_text, model)

    # Define KNN search query
    query = {
        "knn": {
            "field": "embedding",
            "query_vector": query_embedding,
            "k": 10,
            "num_candidates": 30,  # Optional: increases search accuracy
        },
        "_source": ["name"],  # Return only the name field
    }

    # print(query)

    # Perform search in Elasticsearch
    try:
        response = es.search(index="index_with_schema_combined", body=query)
        # print(response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Elasticsearch query failed: {e}")

    # Extract names from response
    names = [hit["_source"]["name"] for hit in response["hits"]["hits"]]

    return names


def get_document_by_name(name: str):
    query = {"query": {"match": {"name": name}}}  # Search by the name

    try:
        response = es.search(index="index_with_schema_combined", body=query)
        hits = response["hits"]["hits"]
        if not hits:
            raise HTTPException(status_code=404, detail="Document not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Elasticsearch query failed: {e}")

    # Extract relevant fields from the first hit
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
# FastAPI endpoint for retrieving document details by name
@app.post("/get-document/")
def get_document_endpoint(request: NameRequest):
    document = get_document_by_name(request.name)
    return {"document": document}
"""


# FastAPI endpoint
@app.post("/search-names/")
def search_names_endpoint(request: QueryRequest):
    names = search_names(request.query)

    print(names)

    return {"names": names}
