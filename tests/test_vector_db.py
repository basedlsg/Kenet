import unittest
import os
import numpy as np
from src.vector_db import VectorDB
from qdrant_client import models

class TestVectorDB(unittest.TestCase):
    def setUp(self):
        self.db = VectorDB(collection_name="test_collection")
        self.db.create_collection()
        self.captions_file = "test_captions.txt"
        with open(self.captions_file, "w") as f:
            f.write("file1.jpg\ta test caption\n")
            f.write("file2.jpg\tanother test caption\n")
            f.write("file3.jpg\ta third test caption\n")

    def tearDown(self):
        os.remove(self.captions_file)

    def test_batch_indexing(self):
        self.assertTrue(self.db.index_captions(self.captions_file, batch_size=2))
        # Verify that the points were added
        result, _ = self.db.client.scroll(collection_name="test_collection")
        self.assertEqual(len(result), 3)

    def test_geometric_pruning(self):
        # Add a point with a geometric descriptor
        self.db.client.upsert(
            collection_name="test_collection",
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
        self.assertEqual(results[0].id, 100)

if __name__ == "__main__":
    unittest.main()