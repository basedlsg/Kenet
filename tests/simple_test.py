import unittest
import os
import numpy as np
from src.vector_db import VectorDB
from qdrant_client import models

class SimpleTest(unittest.TestCase):
    def setUp(self):
        self.db = VectorDB(collection_name="simple_test_collection")
        self.db.create_collection()

    def test_query_returns_id(self):
        # Add a point with a geometric descriptor
        self.db.client.upsert(
            collection_name="simple_test_collection",
            points=[
                models.PointStruct(
                    id=100,
                    vector=np.random.rand(768).tolist(),
                    payload={"caption": "a geometric caption", "geometric_descriptor": "geo_1"}
                )
            ],
            wait=True,
        )
        # Query with the geometric filter
        query_embedding = self.db.get_embedding("a geometric caption", task_type="RETRIEVAL_QUERY")
        results = self.db.query(query_embedding, geo_filter="geo_1")
        self.assertEqual(len(results), 1)
        self.assertEqual(results.id, 100)

if __name__ == "__main__":
    unittest.main()