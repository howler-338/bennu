from app.services.chunker import chunk_text


def test_empty_text():
    assert chunk_text("") == []
    assert chunk_text("   ") == []


def test_short_text_single_chunk():
    chunks = chunk_text("Hello world", chunk_size=1000, overlap=200)
    assert chunks == ["Hello world"]


def test_text_exactly_chunk_size():
    text = "a" * 1000
    chunks = chunk_text(text, chunk_size=1000, overlap=200)
    assert len(chunks) == 1
    assert chunks[0] == text


def test_multiple_chunks():
    text = "a" * 2500
    chunks = chunk_text(text, chunk_size=1000, overlap=200)
    assert len(chunks) == 3


def test_overlap_content_repeats():
    text = "A" * 2000
    chunks = chunk_text(text, chunk_size=1000, overlap=200)
    # Last 200 chars of chunk 0 must equal first 200 chars of chunk 1
    assert chunks[0][-200:] == chunks[1][:200]


def test_no_empty_chunks():
    text = "Hello\n\n\nWorld"
    chunks = chunk_text(text, chunk_size=1000, overlap=200)
    assert all(c.strip() for c in chunks)


def test_whitespace_stripped():
    text = "  hello world  "
    chunks = chunk_text(text, chunk_size=1000, overlap=200)
    assert chunks[0] == "hello world"
