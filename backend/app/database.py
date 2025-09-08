# backend/app/database.py
from neo4j import GraphDatabase
from typing import Optional, Any
from config import settings
import logging

logger = logging.getLogger(__name__)


class DatabaseManager:
    """
    Manages Neo4j database connections and sessions
    """

    def __init__(self):
        self.driver: Optional[Any] = None
        self.uri = settings.neo4j_uri
        self.user = settings.neo4j_user
        self.password = settings.neo4j_password

    def connect(self):
        """
        Initialize connection to Neo4j database
        """
        try:
            self.driver = GraphDatabase.driver(
                self.uri,
                auth=(self.user, self.password),
                max_connection_lifetime=3600,
                max_connection_pool_size=50,
                connection_acquisition_timeout=60
            )
            # Verify connectivity
            self.driver.verify_connectivity()
            logger.info(f"Connected to Neo4j at {self.uri}")
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {e}")
            raise

    def close(self):
        """
        Close database connection
        """
        if self.driver:
            self.driver.close()
            logger.info("Neo4j connection closed")

    def get_session(self):
        """
        Get a new database session
        """
        if not self.driver:
            self.connect()
        return self.driver.session()

    def execute_query(self, query: str, parameters: dict = None):
        """
        Execute a single query and return results
        """
        with self.get_session() as session:
            result = session.run(query, parameters or {})
            return [record.data() for record in result]

    def execute_write(self, query: str, parameters: dict = None):
        """
        Execute a write transaction
        """
        with self.get_session() as session:
            with session.begin_transaction() as tx:
                result = tx.run(query, parameters or {})
                tx.commit()
                return result

    def check_connection(self) -> bool:
        """
        Check if database connection is active
        """
        try:
            with self.get_session() as session:
                result = session.run("RETURN 1 as test")
                return result.single()["test"] == 1
        except Exception as e:
            logger.error(f"Connection check failed: {e}")
            return False

    def get_statistics(self) -> dict:
        """
        Get database statistics
        """
        try:
            with self.get_session() as session:
                # Get node count
                nodes = session.run("MATCH (n) RETURN count(n) as count").single()["count"]

                # Get relationship count
                relationships = session.run("MATCH ()-[r]->() RETURN count(r) as count").single()["count"]

                # Get node labels
                labels = session.run("CALL db.labels() YIELD label RETURN collect(label) as labels").single()["labels"]

                # Get relationship types
                rel_types = session.run(
                    "CALL db.relationshipTypes() YIELD relationshipType RETURN collect(relationshipType) as types").single()[
                    "types"]

                return {
                    "nodes": nodes,
                    "relationships": relationships,
                    "labels": labels,
                    "relationship_types": rel_types
                }
        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            return {}


# Create singleton instance
db_manager = DatabaseManager()