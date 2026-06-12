from fastapi.testclient import TestClient
from ..main import app
from fastapi import status
from ..routers import todos


client = TestClient(app)

def test_api_endppt ():
    response = client.get('/test_pytest')
    assert response.status_code == status.HTTP_200_OK
    