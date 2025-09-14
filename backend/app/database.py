"""
Database connection manager for Neo4j
"""
from neo4j import GraphDatabase
from .config import settings


class DatabaseManager:
    """
    Manages Neo4j database connections and provides session management
    """
    def __init__(self):
        self.driver = None
        self.uri = settings.neo4j_uri
        self.user = settings.neo4j_user
        self.password = settings.neo4j_password

    def connect(self):
        """Establish connection to Neo4j database"""
        try:
            self.driver = GraphDatabase.driver(
                self.uri,
                auth=(self.user, self.password),
                max_connection_lifetime=30 * 60,  # 30 minutes
                max_connection_pool_size=50,
                connection_acquisition_timeout=2 * 60  # 2 minutes
            )
            # Verify connection
            self.driver.verify_connectivity()
            return True
        except Exception as e:
            print(f"❌ Failed to connect to Neo4j: {e}")
            self.driver = None
            return False

    def close(self):
        """Close the database connection"""
        if self.driver:
            self.driver.close()
            self.driver = None

    def get_session(self):
        """Get a new database session"""
        if not self.driver:
            if not self.connect():
                raise Exception("Database connection not established")
        return self.driver.session()

    def execute_query(self, query, parameters=None):
        """Execute a query and return results"""
        with self.get_session() as session:
            result = session.run(query, parameters or {})
            return [record.data() for record in result]

    def execute_write_query(self, query, parameters=None):
        """Execute a write query"""
        with self.get_session() as session:
            # In neo4j-driver v5, auto-commit is used for session.run
            # Alternatively, use explicit write transactions
            result = session.run(query, parameters or {})
            return result.consume()

    def check_connection(self):
        """Check if database connection is alive"""
        try:
            with self.get_session() as session:
                result = session.run("RETURN 1 as test")
                return result.single() is not None
        except Exception:
            return False

    def get_database_info(self):
        """Get information about the database"""
        try:
            with self.get_session() as session:
                # Get node counts
                node_query = """
                MATCH (n)
                RETURN labels(n)[0] as label, count(n) as count
                ORDER BY count DESC
                """
                nodes = session.run(node_query).data()

                # Get relationship counts
                rel_query = """
                MATCH ()-[r]->()
                RETURN type(r) as type, count(r) as count
                ORDER BY count DESC
                """
                relationships = session.run(rel_query).data()

                return {
                    "nodes": nodes,
                    "relationships": relationships,
                    "status": "connected"
                }
        except Exception as e:
            return {
                "status": "disconnected",
                "error": str(e)
            }


# Create global database manager instance
db_manager = DatabaseManager()