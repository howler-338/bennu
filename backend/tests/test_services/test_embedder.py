from unittest.mock import MagicMock, patch


def _mock_response(vector=None):
    resp = MagicMock()
    resp.json.return_value = {"embedding": vector or [0.1] * 768}
    resp.raise_for_status = MagicMock()
    return resp


def test_embed_text_returns_vector(app):
    from app.services.embedder import embed_text
    with app.app_context():
        with patch("app.services.embedder.requests.post", return_value=_mock_response()):
            result = embed_text("hello world")
    assert len(result) == 768
    assert result[0] == 0.1


def test_embed_text_sends_correct_payload(app):
    from app.services.embedder import embed_text
    with app.app_context():
        with patch("app.services.embedder.requests.post", return_value=_mock_response()) as mock_post:
            embed_text("test input")

    payload = mock_post.call_args[1]["json"]
    assert payload["model"] == "nomic-embed-text"
    assert payload["prompt"] == "test input"


def test_embed_text_uses_ollama_url(app):
    from app.services.embedder import embed_text
    with app.app_context():
        with patch("app.services.embedder.requests.post", return_value=_mock_response()) as mock_post:
            embed_text("test")

    url = mock_post.call_args[0][0]
    assert "11434" in url
    assert "embeddings" in url
