import os
import logging
from neo4j import AsyncGraphDatabase

logger = logging.getLogger(__name__)

class Neo4jClient:
    def __init__(self):
        self.uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.user = os.getenv("NEO4J_USER", "neo4j")
        self.password = os.getenv("NEO4J_PASSWORD", "password123")
        
        logger.info(f"[Neo4jClient] Initializing connection to uri={self.uri}")
        self.driver = AsyncGraphDatabase.driver(
            self.uri, 
            auth=(self.user, self.password)
        )

    async def close(self):
        logger.info("[Neo4jClient] Closing database driver connection pool.")
        await self.driver.close()

    async def initialize_database(self):
        """Creates the vector search index for Document node embeddings if it doesn't exist."""
        # Note: nomic-embed-text generates 768 dimensions. Google's text-embedding-004 also has 768 dimensions.
        index_query = """
        CREATE VECTOR INDEX document_embeddings IF NOT EXISTS
        FOR (d:Document)
        ON (d.embedding)
        OPTIONS {
          indexConfig: {
            `vector.dimensions`: 768,
            `vector.similarity_function`: 'cosine'
          }
        }
        """
        logger.info("[Neo4jClient] Ensuring vector index document_embeddings is initialized.")
        try:
            await self.driver.execute_query(index_query)
            logger.info("[Neo4jClient] Vector index initialized successfully.")
        except Exception as e:
            logger.error(f"[Neo4jClient] Error initializing vector index: {e}")
            raise e

    async def create_user(self, user_id: str):
        query = """
        MERGE (u:User {id: $user_id})
        ON CREATE SET u.createdAt = datetime()
        RETURN u.id AS id
        """
        records, _, _ = await self.driver.execute_query(query, user_id=user_id)
        return records[0]["id"] if records else None

    async def create_thread(self, user_id: str, thread_id: str, title: str):
        # First ensure user exists
        await self.create_user(user_id)
        
        query = """
        MATCH (u:User {id: $user_id})
        MERGE (t:Thread {id: $thread_id})
        ON CREATE SET t.title = $title, t.createdAt = datetime()
        MERGE (u)-[:HAS_THREAD]->(t)
        RETURN t.id AS id, t.title AS title, t.createdAt AS createdAt
        """
        records, _, _ = await self.driver.execute_query(
            query, user_id=user_id, thread_id=thread_id, title=title
        )
        return records[0] if records else None

    async def get_threads(self, user_id: str):
        query = """
        MATCH (u:User {id: $user_id})-[:HAS_THREAD]->(t:Thread)
        RETURN t.id AS id, t.title AS title, toString(t.createdAt) AS createdAt
        ORDER BY t.createdAt DESC
        """
        records, _, _ = await self.driver.execute_query(query, user_id=user_id)
        return [dict(record) for record in records]

    async def delete_thread(self, thread_id: str):
        query = """
        MATCH (t:Thread {id: $thread_id})
        OPTIONAL MATCH (t)-[:HAS_MESSAGE]->(m:Message)
        DETACH DELETE t, m
        """
        await self.driver.execute_query(query, thread_id=thread_id)

    async def get_messages(self, thread_id: str):
        query = """
        MATCH (t:Thread {id: $thread_id})-[:HAS_MESSAGE]->(m:Message)
        RETURN m.id AS id, m.role AS role, m.content AS content, toString(m.createdAt) AS createdAt
        ORDER BY m.createdAt ASC
        """
        records, _, _ = await self.driver.execute_query(query, thread_id=thread_id)
        return [dict(record) for record in records]

    async def save_message(self, thread_id: str, message_id: str, role: str, content: str):
        query = """
        MATCH (t:Thread {id: $thread_id})
        CREATE (m:Message {id: $message_id, role: $role, content: $content, createdAt: datetime()})
        CREATE (t)-[:HAS_MESSAGE]->(m)
        WITH t, m
        OPTIONAL MATCH (t)-[:HAS_MESSAGE]->(prev:Message)
        WHERE prev <> m
        WITH m, prev ORDER BY prev.createdAt DESC LIMIT 1
        FOREACH (_ IN CASE WHEN prev IS NOT NULL THEN [1] ELSE [] END |
            CREATE (prev)-[:NEXT_MESSAGE]->(m)
        )
        RETURN m.id AS id, m.role AS role, m.content AS content, toString(m.createdAt) AS createdAt
        """
        records, _, _ = await self.driver.execute_query(
            query, thread_id=thread_id, message_id=message_id, role=role, content=content
        )
        return records[0] if records else None

    async def ingest_document(self, doc_id: str, content: str, embedding: list[float]):
        query = """
        MERGE (d:Document {id: $doc_id})
        SET d.content = $content, d.embedding = $embedding
        RETURN d.id AS id
        """
        records, _, _ = await self.driver.execute_query(
            query, doc_id=doc_id, content=content, embedding=embedding
        )
        return records[0]["id"] if records else None

    async def search_documents(self, query_embedding: list[float], limit: int = 3):
        query = """
        CALL db.index.vector.queryNodes('document_embeddings', $limit, $query_embedding)
        YIELD node, score
        RETURN node.content AS content, score
        """
        records, _, _ = await self.driver.execute_query(
            query, query_embedding=query_embedding, limit=limit
        )
        return [dict(record) for record in records]
