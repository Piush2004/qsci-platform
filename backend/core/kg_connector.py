import os
from neo4j import GraphDatabase
import networkx as nx

class KnowledgeGraphConnector:
    """
    Connects to Neo4j for Enterprise usage, falling back to NetworkX for offline/local development.
    Maps relationships: Supplier -> Warehouse -> Store -> Customer -> Product.
    """
    def __init__(self, use_neo4j=False):
        self.use_neo4j = use_neo4j
        if self.use_neo4j:
            uri = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
            user = os.environ.get("NEO4J_USER", "neo4j")
            password = os.environ.get("NEO4J_PASSWORD", "password")
            self.driver = GraphDatabase.driver(uri, auth=(user, password))
            print("Initialized Neo4j driver.")
        else:
            self.graph = nx.DiGraph()
            print("Initialized local NetworkX graph for fallback.")

    def close(self):
        if self.use_neo4j:
            self.driver.close()

    def add_relationship(self, entity1, relation, entity2):
        """Add a directed relationship between two entities."""
        if self.use_neo4j:
            with self.driver.session() as session:
                session.run(
                    f"MERGE (a {{name: $entity1}}) MERGE (b {{name: $entity2}}) MERGE (a)-[:{relation}]->(b)",
                    entity1=entity1, entity2=entity2
                )
        else:
            self.graph.add_edge(entity1, entity2, type=relation)
