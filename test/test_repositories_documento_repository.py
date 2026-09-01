"""Pruebas unitarias para el repositorio de documentos.
Estas pruebas verifican la correcta serialización, deserialización y generación de IDs en el `DocumentRepository`."""

from App.models.documento import Document


def test_serialize_deserialize_roundtrip(repo):
    doc = Document(id=1, name="A", file_path="p", checksum="c", file_size=2)
    payload = repo._serialize(doc)
    assert isinstance(payload, dict)
    payload["_id"] = "mongoid"
    deserialized = repo._deserialize(payload)
    assert deserialized is not None
    assert deserialized.id == 1
    assert deserialized.name == "A"


def test_next_id_increments(repo, fake_db):
    fake_db._cols["counters"].find_one_and_update.return_value = {"value": 5}
    assert repo._next_id() == 5
