# backend/app/api/v1/endpoints/health.py
from fastapi import APIRouter, Depends
from datetime import datetime
from ....models.schemas import HealthCheck
from ....database import db_manager

router = APIRouter()


@router.get("/", response_model=HealthCheck)
async def health_check():
    """
    Check API and database health status
    """
    try:
        with db_manager.get_session() as session:
            # Test database connection
            result = session.run("RETURN 1 as test")
            db_status = "connected" if result.single() else "error"

            # Get basic statistics
            stats = session.run("""
                MATCH (n) 
                WITH count(n) as node_count
                OPTIONAL MATCH ()-[r]->()
                RETURN node_count, count(r) as relationship_count
            """).single()

            return HealthCheck(
                status="healthy",
                database=db_status,
                timestamp=datetime.now(),
                node_count=stats['node_count'] if stats else 0,
                relationship_count=stats['relationship_count'] if stats else 0
            )
    except Exception as e:
        return HealthCheck(
            status="unhealthy",
            database=f"error: {str(e)}",
            timestamp=datetime.now(),
            node_count=0,
            relationship_count=0
        )


@router.get("/ready")
async def readiness_check():
    """
    Check if the service is ready to accept requests
    """
    try:
        with db_manager.get_session() as session:
            session.run("RETURN 1")
            return {"status": "ready"}
    except:
        return {"status": "not_ready"}


@router.get("/live")
async def liveness_check():
    """
    Check if the service is alive
    """
    return {"status": "alive"}