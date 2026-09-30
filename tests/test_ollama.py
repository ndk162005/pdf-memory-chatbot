import pytest
import requests
from unittest.mock import patch, MagicMock
from app.llm.ollama_client import OllamaClient

@patch("requests.post")
def test_chat_success(mock_post):
    mock_resp = MagicMock()
    mock_resp.json.return_value = {"message": {"content": "Hello"}}
    mock_post.return_value = mock_resp
    
    client = OllamaClient()
    resp = client.chat([{"role": "user", "content": "Hi"}])
    assert resp == "Hello"

@patch("requests.post")
def test_chat_connection_error(mock_post):
    mock_post.side_effect = requests.exceptions.ConnectionError()
    client = OllamaClient()
    with pytest.raises(Exception):
        client.chat([])

@patch("requests.post")
def test_chat_timeout(mock_post):
    mock_post.side_effect = requests.exceptions.Timeout()
    client = OllamaClient()
    with pytest.raises(TimeoutError):
        client.chat([])

@patch("requests.post")
def test_chat_model_not_found(mock_post):
    mock_resp = MagicMock()
    mock_resp.status_code = 404
    mock_post.return_value = mock_resp
    client = OllamaClient()
    with pytest.raises(ValueError):
        client.chat([])

@patch("requests.get")
def test_is_available_true(mock_get):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_get.return_value = mock_resp
    
    client = OllamaClient()
    assert client.is_available() is True

@patch("requests.get")
def test_is_available_false(mock_get):
    mock_get.side_effect = Exception()
    client = OllamaClient()
    assert client.is_available() is False

@patch("requests.get")
def test_check_model(mock_get):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"models": [{"name": "mistral:latest"}]}
    mock_get.return_value = mock_resp
    
    client = OllamaClient()
    client.model = "mistral"
    assert client.check_model() is True
