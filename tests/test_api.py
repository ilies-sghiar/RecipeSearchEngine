import pytest
from httpx import AsyncClient, ASGITransport
from searchengine.api import app
from elasticsearch import Elasticsearch

@pytest.mark.asyncio
async def test_cluster_is_ok():
    # Initialize Elasticsearch client
    es = Elasticsearch(
        ["http://localhost:9200"],  # The node's URL
        verify_certs=False,  # Optional: No need for certificate verification since security is disabled
    )

    assert es.ping()  # cluster doit être lancé

@pytest.mark.asyncio
async def test_search_names_endpoint():
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.post("/search-names/", json={"query": "smoothie"})

    assert resp.status_code == 200
    assert "names" in resp.json()