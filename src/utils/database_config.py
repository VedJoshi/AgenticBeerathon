"""
Database configuration and connection utilities for the cocktail vector database
"""

import os
import psycopg2
from psycopg2.extensions import connection as Connection
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class DatabaseConfig:
    """Database configuration management"""
    
    def __init__(self):
        self.config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'database': os.getenv('DB_NAME', 'agenticbeerathon'),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD', ''),
            'port': int(os.getenv('DB_PORT', '5432'))
        }
    
    def get_connection_string(self) -> str:
        """Get PostgreSQL connection string"""
        return f"postgresql://{self.config['user']}:{self.config['password']}@{self.config['host']}:{self.config['port']}/{self.config['database']}"
    
    def get_connection(self) -> Connection:
        """Get a database connection"""
        return psycopg2.connect(**self.config)
    
    def test_connection(self) -> bool:
        """Test database connection"""
        try:
            conn = self.get_connection()
            cur = conn.cursor()
            cur.execute("SELECT 1")
            cur.close()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False

def setup_database():
    """Setup database with schema and extensions"""
    config = DatabaseConfig()
    
    try:
        conn = config.get_connection()
        conn.autocommit = True
        cur = conn.cursor()
        
        # Enable pgvector extension
        cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        logger.info("pgvector extension enabled")
        
        cur.close()
        conn.close()
        logger.info("Database setup completed")
        
    except Exception as e:
        logger.error(f"Database setup failed: {e}")
        raise

def run_schema_setup():
    """Run the schema setup from SQL files"""
    config = DatabaseConfig()
    
    # Read and execute schema.sql
    schema_path = os.path.join(os.path.dirname(__file__), '../../database/schema.sql')
    functions_path = os.path.join(os.path.dirname(__file__), '../../database/vector_functions.sql')
    
    try:
        conn = config.get_connection()
        cur = conn.cursor()
        
        # Execute schema
        if os.path.exists(schema_path):
            with open(schema_path, 'r') as f:
                schema_sql = f.read()
                cur.execute(schema_sql)
                logger.info("Database schema created")
        
        # Execute vector functions
        if os.path.exists(functions_path):
            with open(functions_path, 'r') as f:
                functions_sql = f.read()
                cur.execute(functions_sql)
                logger.info("Vector search functions created")
        
        conn.commit()
        cur.close()
        conn.close()
        
    except Exception as e:
        logger.error(f"Schema setup failed: {e}")
        raise

if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    # Test and setup database
    config = DatabaseConfig()
    
    if config.test_connection():
        logger.info("Database connection successful")
        setup_database()
        run_schema_setup()
    else:
        logger.error("Database connection failed")
