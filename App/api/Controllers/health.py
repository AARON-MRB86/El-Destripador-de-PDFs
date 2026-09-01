from app.utils.database import ping_database


def ping() -> dict:
    """Respuesta simple para facilitar su analisis desde Docker, Kubernetes o balanceadores de carga.
    Devuelve un estado "ok" si la base de datos responde correctamente, o "degraded" si no lo hace.
    Esto permite a los orquestadores determinar rápidamente el estado de salud de la aplicación sin necesidad de realizar análisis complejos.
    """
    db_ok = ping_database()
    status = "ok" if db_ok else "degraded"
    return {"status": status, "database": db_ok}
