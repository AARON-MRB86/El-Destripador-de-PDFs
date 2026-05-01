from collections.abc import Mapping
from typing import Any, List, Optional

from pymongo import ReturnDocument
from pymongo.database import Database

from App.models.documento import Document, utcnow


class DocumentRepository:
    """Repository for document database operations."""

    def __init__(self, database: Database):
        """
        Initialize repository with database handle.

        Args:
            database: MongoDB database
        """
        self.collection = database["documents"]
        self.counters = database["counters"]

    def create(self, document: Document) -> Document:
        """
        Create a new document.

        Args:
            document: Document to create

        Returns:
            Created document
        """
        created_document = document.model_copy(
            update={
                "id": self._next_id(),
                "created_at": utcnow(),
                "updated_at": utcnow(),
            }
        )
        self.collection.insert_one(self._serialize(created_document))
        return created_document

    def get_by_id(self, document_id: int) -> Optional[Document]:
        """
        Get document by ID.

        Args:
            document_id: Document ID

        Returns:
            Document if found, None otherwise
        """
        doc = self.collection.find_one({"id": document_id})
        return self._deserialize(doc)

    def get_all(self, skip: int = 0, limit: int = 10) -> List[Document]:
        """
        Get all documents with pagination.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of documents
        """
        docs = self.collection.find().sort("id", 1).skip(skip).limit(limit)
        return [self._deserialize(doc) for doc in docs]

    def get_by_checksum(self, checksum: str) -> Optional[Document]:
        """
        Get document by checksum.

        Args:
            checksum: SHA-256 checksum of the file

        Returns:
            Document if found, None otherwise
        """
        doc = self.collection.find_one({"checksum": checksum})
        return self._deserialize(doc)

    def update(self, document_id: int, data: dict[str, Any]) -> Optional[Document]:
        """
        Update document.

        Args:
            document_id: Document ID
            data: Dictionary with fields to update

        Returns:
            Updated document if found, None otherwise
        """
        update_data = {k: v for k, v in data.items() if v is not None}
        if not update_data:
            return self.get_by_id(document_id)

        update_data["updated_at"] = utcnow()
        doc = self.collection.find_one_and_update(
            {"id": document_id},
            {"$set": update_data},
            return_document=ReturnDocument.AFTER,
        )
        return self._deserialize(doc)

    def delete(self, document_id: int) -> bool:
        """
        Delete document.

        Args:
            document_id: Document ID

        Returns:
            True if deleted, False if not found
        """
        result = self.collection.delete_one({"id": document_id})
        return result.deleted_count == 1

    def _next_id(self) -> int:
        """Generate the next sequential document ID."""
        counter = self.counters.find_one_and_update(
            {"_id": "document_id"},
            {"$inc": {"value": 1}},
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )
        return int(counter["value"])

    def _serialize(self, document: Document) -> dict[str, Any]:
        """Convert Document model to MongoDB document."""
        return document.model_dump(mode="python")

    def _deserialize(self, data: Mapping[str, Any] | None) -> Optional[Document]:
        """Convert MongoDB document to Document model."""
        if not data:
            return None
        payload = dict(data)
        payload.pop("_id", None)
        return Document.model_validate(payload)
