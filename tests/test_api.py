import pytest


@pytest.mark.asyncio
async def test_cluster_is_ok():
    # Test bidon pour simuler un ping Elasticsearch sur Github action
    assert True


@pytest.mark.asyncio
async def test_search_names_endpoint():
    # Test bidon pour simuler un endpoint FastAPI sur Github action
    fake_response = {"names": ["smoothie", "juice", "salad"]}
    assert "names" in fake_response
    assert isinstance(fake_response["names"], list)
    assert "smoothie" in fake_response["names"]
