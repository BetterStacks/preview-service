import io
import unittest.mock

from starlette.testclient import TestClient
import httpx

from app import app


def test_health_endpoint_succeeds():
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200


def test_preview_endpoint_succeeds():
    client = TestClient(app)
    file = io.StringIO("plain text file data")
    response = client.post("/preview/100x100", files={"file": file})
    assert response.status_code == 200


def test_preview_endpoint_fails_on_missing_parameters():
    client = TestClient(app)
    response = client.post("/preview/100x100")
    assert response.status_code == 400
    assert "file" in response.json()["error"].lower() or "url" in response.json()["error"].lower()


def test_preview_endpoint_fails_on_undetected_mimetype():
    client = TestClient(app)
    file = io.BytesIO()
    response = client.post("/preview/100x100", files={"file": file})
    assert response.status_code == 500


@unittest.mock.patch('httpx.AsyncClient.get')
def test_preview_endpoint_with_file_url(mock_get):
    # Mock the HTTP response
    mock_response = unittest.mock.MagicMock()
    mock_response.raise_for_status = unittest.mock.MagicMock()
    mock_response.content = b'test file content'
    mock_get.return_value = mock_response

    client = TestClient(app)
    response = client.post(
        "/preview/100x100", 
        data={"file_url": "https://example.com/test.pdf"}
    )
    
    # Check that the httpx client was called with the right URL
    mock_get.assert_called_once_with("https://example.com/test.pdf")
    assert response.status_code == 200


@unittest.mock.patch('httpx.AsyncClient.get')
def test_preview_endpoint_with_file_url_http_error(mock_get):
    # Make the HTTP request raise an exception
    mock_get.side_effect = httpx.HTTPError("Connection error")

    client = TestClient(app)
    response = client.post(
        "/preview/100x100", 
        data={"file_url": "https://example.com/test.pdf"}
    )
    
    assert response.status_code == 400
    assert "error downloading file" in response.json()["error"].lower()
