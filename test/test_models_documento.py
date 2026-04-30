from App.models.documento import Document


def test_document_defaults_and_fields():
    doc = Document(name="Test Doc", file_path="memory://x.pdf", checksum="abc123", file_size=10)
    assert doc.id is None
    assert doc.name == "Test Doc"
    assert doc.file_path.startswith("memory://")
    assert doc.file_size == 10
    assert not doc.is_processed or isinstance(doc.is_processed, bool)
