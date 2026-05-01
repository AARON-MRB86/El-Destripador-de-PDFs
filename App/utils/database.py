"""MongoDB connection helpers and database bootstrap.

Provides a cached `MongoClient` factory, a FastAPI dependency `get_db`,
and helpers for index creation, pinging and teardown. Supports
`mongomock://` urls for tests.
"""

from functools import lru_cache
from typing import Generator, Optional
import logging

from pymongo import ASCENDING, MongoClient
from pymongo.database import Database
from pymongo.errors import PyMongoError

from App.config import settings

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def get_client() -> MongoClient:
	"""Create and cache a MongoDB client.

	When `settings.database_url` starts with `mongomock://` a `mongomock`
	client is returned (tests). Otherwise returns a real `MongoClient`.
	"""
	if settings.database_url.startswith("mongomock://"):
		try:
			import mongomock
		except ImportError as exc:
			raise RuntimeError(
				"mongomock is required when DATABASE_URL starts with mongomock://"
			) from exc
		return mongomock.MongoClient()

	timeout = int(settings.database_timeout_ms or 5000)
	return MongoClient(
		settings.database_url,
		serverSelectionTimeoutMS=timeout,
		connect=False,
	)


def close_client() -> None:
	"""Close the cached MongoClient and clear the cache."""
	try:
		client = get_client()
		client.close()
	finally:
		get_client.cache_clear()


def get_database() -> Database:
	"""Return the configured MongoDB database instance."""
	return get_client()[settings.database_name]


def get_db() -> Generator[Database, None, None]:
	"""FastAPI dependency generator that yields the Database instance."""
	db = get_database()
	try:
		yield db
	finally:
		# client lifecycle is managed separately
		pass


def ping_database(timeout_ms: Optional[int] = None) -> bool:
	"""Return True if DB responds to ping command."""
	try:
		client = get_client()
		client.admin.command("ping")
		return True
	except Exception:
		logger.exception("Database ping failed")
		return False


def ensure_indexes() -> None:
	"""Create collections and indexes required by the app."""
	try:
		db = get_database()

		documents = db["documents"]
		documents.create_index([("id", ASCENDING)], unique=True, name="idx_documents_id")
		documents.create_index([("checksum", ASCENDING)], unique=True, name="idx_documents_checksum")
		documents.create_index([("file_path", ASCENDING)], unique=True, name="idx_documents_file_path")
		documents.create_index([("name", ASCENDING)], name="idx_documents_name")

		counters = db["counters"]
		counters.update_one({"_id": "document_id"}, {"$setOnInsert": {"value": 0}}, upsert=True)
	except PyMongoError as exc:
		logger.exception("Failed to initialize MongoDB indexes/collections")
		raise RuntimeError(
			"No se pudo conectar a MongoDB. Verifica DATABASE_URL o inicia el servidor antes de levantar la API."
		) from exc


def drop_database() -> None:
	"""Drop the configured database. Intended for tests or dev cleanup."""
	try:
		client = get_client()
		client.drop_database(settings.database_name)
	except PyMongoError:
		logger.exception("Failed to drop database")
		raise

