from unittest.mock import MagicMock

from App.repositories.documento_repository import DocumentRepository
from App.models.documento import Document


class FakeDB:
    def __init__(self):
        self._cols = {
            "documents": MagicMock(),
            "counters": MagicMock(),
        }

    def __getitem__(self, name):
        return self._cols[name]


def test_serialize_deserialize_roundtrip():
    db = FakeDB()
    repo = DocumentRepository(db)
    doc = Document(id=1, name="A", file_path="p", checksum="c", file_size=2)
    payload = repo._serialize(doc)
    assert isinstance(payload, dict)
    payload["_id"] = "mongoid"
    deserialized = repo._deserialize(payload)
    assert deserialized is not None
    assert deserialized.id == 1
    assert deserialized.name == "A"


def test_next_document_id_increments():
    db = FakeDB()
    db._cols["counters"].find_one_and_update.return_value = {"value": 5}
    repo = DocumentRepository(db)
    assert repo._next_document_id() == 5
