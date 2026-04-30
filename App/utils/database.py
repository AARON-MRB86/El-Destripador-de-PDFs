<<<<<<< HEAD
"""MongoDB connection helpers and database bootstrap."""

from functools import lru_cache
from typing import Generator
=======
from functools import lru_cache
from typing import Generator, Optional
import logging
>>>>>>> 2bf893a305a8446f9cb5a945715bba12f3c44eed

from pymongo import ASCENDING, MongoClient
from pymongo.database import Database
from pymongo.errors import PyMongoError

from app.config import settings

<<<<<<< HEAD

@lru_cache(maxsize=1)
def get_client() -> MongoClient:
    """Create and cache a MongoDB client."""
    if settings.database_url.startswith("mongomock://"):
        try:
            import mongomock
        except ImportError as exc:
            raise RuntimeError(
                "mongomock is required when DATABASE_URL starts with mongomock://"
            ) from exc
        return mongomock.MongoClient()

    return MongoClient(
        settings.database_url,
        serverSelectionTimeoutMS=settings.database_timeout_ms,
    )


def reset_client() -> None:
    """Clear the cached client instance."""
    get_client.cache_clear()


def get_database() -> Database:
    """Return the configured MongoDB database."""
    return get_client()[settings.database_name]


def get_db() -> Generator[Database, None, None]:
    """Yield the configured MongoDB database."""
    yield get_database()


def create_tables() -> None:
    """Initialize collections and indexes."""
    try:
        documents = get_database()["documents"]
        documents.create_index([("id", ASCENDING)], unique=True)
        documents.create_index([("checksum", ASCENDING)], unique=True)
        documents.create_index([("file_path", ASCENDING)], unique=True)
        documents.create_index([("name", ASCENDING)])

        counters = get_database()["counters"]
        counters.update_one(
            {"_id": "document_id"},
            {"$setOnInsert": {"value": 0}},
            upsert=True,
        )
    except PyMongoError as exc:
        raise RuntimeError(
            "No se pudo conectar a MongoDB. "
            "Verifica DATABASE_URL o inicia el servidor antes de levantar la API."
        ) from exc


def drop_tables() -> None:
    """Drop the configured database."""
    client = get_client()
    client.drop_database(settings.database_name)
=======
logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def get_client() -> MongoClient:
	"""Create and cache a MongoDB client.

	Supports `mongomock://` URLs for tests.
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
	"""Close the cached MongoClient and clear the cache.

	Use this in tests or shutdown hooks when you need to release resources.
	"""
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
		# keep client open between requests; explicit shutdown handled by `close_client`
		pass


def ping_database(timeout_ms: Optional[int] = None) -> bool:
	"""Simple healthcheck: return True if DB responds to ping command."""
	try:
		client = get_client()
		# optional override for timeout (not always supported by mongomock)
		client.admin.command("ping")
		return True
	except Exception:  # keep broad to surface connectivity issues as False
		logger.exception("Database ping failed")
		return False


def ensure_indexes() -> None:
	"""Create collections and indexes required by the app.

	Raises a RuntimeError with a helpful message when connection fails.
	"""
	try:
		db = get_database()

		documents = db["documents"]
		documents.create_index([("id", ASCENDING)], unique=True, name="idx_documents_id")
		documents.create_index(
			[("checksum", ASCENDING)], unique=True, name="idx_documents_checksum"
		)
		documents.create_index(
			[("file_path", ASCENDING)], unique=True, name="idx_documents_file_path"
		)
		documents.create_index([("name", ASCENDING)], name="idx_documents_name")

		counters = db["counters"]
		counters.update_one(
			{"_id": "document_id"}, {"$setOnInsert": {"value": 0}}, upsert=True
		)
	except PyMongoError as exc:
		logger.exception("No se pudo inicializar índices/colecciones en MongoDB")
		raise RuntimeError(
			"No se pudo conectar a MongoDB. Verifica DATABASE_URL o inicia el servidor antes de levantar la API."
		) from exc


def drop_database() -> None:
	"""Drop the configured database. Intended for tests or dev cleanup."""
	try:
		client = get_client()
		client.drop_database(settings.database_name)
	except PyMongoError:
		logger.exception("Fallo al eliminar la base de datos")
		raise

>>>>>>> 2bf893a305a8446f9cb5a945715bba12f3c44eed
