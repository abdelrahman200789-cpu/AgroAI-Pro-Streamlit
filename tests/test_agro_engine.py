import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from knowledge_engine import KnowledgeEngine
from ir_engine import SimpleIRSystem


class AgroEngineTests(unittest.TestCase):
    def setUp(self):
        self.knowledge = KnowledgeEngine()
        self.ir = SimpleIRSystem()

    def test_tomato_early_blight_rule_matches(self):
        result = self.knowledge.diagnose_plant("Tomato", "yellow spots, dark spots")
        self.assertTrue(any(item["diagnosis"] == "Early Blight" for item in result))

    def test_crop_recommendation(self):
        result = self.knowledge.recommend_crops("Summer", "Loamy")
        names = {item["crop_name"] for item in result}
        self.assertIn("Tomato", names)
        self.assertIn("Corn", names)

    def test_iot_returns_advisories(self):
        result = self.knowledge.analyze_iot_data(38, 90, 20)
        self.assertGreaterEqual(len(result), 3)
        self.assertTrue(any(item["level"] in {"High", "Warning"} for item in result))

    def test_ir_retrieves_blight_document(self):
        result = self.ir.search("early blight yellow spots tomato")
        self.assertTrue(result)
        self.assertEqual(result[0][0], "doc1_blight.txt")

    def test_unknown_query_returns_no_results(self):
        self.assertEqual(self.ir.search("qzxv randomword 998877"), [])


if __name__ == "__main__":
    unittest.main()
