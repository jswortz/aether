import unittest
import time
from memory.context_buffer import ContextBuffer, ActiveAttentionFilter, ContextItem

class TestContextBuffer(unittest.TestCase):

    def setUp(self):
        self.buffer = ContextBuffer()

    def test_add_memory(self):
        self.buffer.add_memory("Project Alpha details", importance=5.0)
        self.assertEqual(len(self.buffer.global_history), 1)
        self.assertEqual(self.buffer.global_history[0].content, "Project Alpha details")
        self.assertEqual(self.buffer.global_history[0].importance, 5.0)

    def test_keyword_relevance(self):
        self.buffer.add_memory("Information about carrots", tags=["vegetable"])
        self.buffer.add_memory("Information about spaceship engines", tags=["tech"])
        
        context = self.buffer.get_active_context("Tell me about engines", max_items=1)
        self.assertIn("spaceship engines", context)
        self.assertNotIn("carrots", context)

    def test_importance_relevance(self):
        # Two similar items, but one is more important
        self.buffer.add_memory("Generic task update", importance=1.0)
        self.buffer.add_memory("CRITICAL: Server is down", importance=10.0)
        
        # Querying for something neutral
        context = self.buffer.get_active_context("What's happening?", max_items=1)
        self.assertIn("CRITICAL", context)

    def test_recency_relevance(self):
        # Add an old item
        old_item = ContextItem(content="Old context", timestamp=time.time() - 10000)
        self.buffer.global_history.append(old_item)
        
        # Add a new item
        self.buffer.add_memory("New context")
        
        context = self.buffer.get_active_context("Give me context", max_items=1)
        self.assertIn("New context", context)
        self.assertNotIn("Old context", context)

    def test_max_items(self):
        for i in range(10):
            self.buffer.add_memory(f"Item {i}")
        
        context = self.buffer.get_active_context("Items", max_items=3)
        # Should contain 3 blocks (split by --- Memory)
        blocks = [b for b in context.split("--- Memory") if b.strip()]
        self.assertEqual(len(blocks), 3)

    def test_empty_buffer(self):
        context = self.buffer.get_active_context("Any query")
        self.assertEqual(context, "")

if __name__ == '__main__':
    unittest.main()
