from App.utils.database import ping_database


def ping() -> dict:
    """Return a lightweight health status used by orchestrators.

    The response is intentionally simple to make it easy to probe from
    Docker, Kubernetes or load balancers.
    """
    db_ok = ping_database()
    status = "ok" if db_ok else "degraded"
    return {"status": status, "database": db_ok}
