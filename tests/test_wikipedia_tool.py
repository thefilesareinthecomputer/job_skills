import unittest
import sys
import os
import json

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.job_skills.tools.wikipedia_tool import WikipediaTool

class TestWikipediaTool(unittest.TestCase):
    def setUp(self):
        self.tool = WikipediaTool()
        print("\n" + "="*80)
        print(f"Setting up test: {self._testMethodName}")
        print("="*80)
    
    def tearDown(self):
        print("-"*80)
        print(f"Completed test: {self._testMethodName}")
        print("="*80)
    
    def test_string_input(self):
        """Test the tool with a simple string input."""
        query = "Python programming"
        print(f"\nTesting with string input: '{query}'")
        
        result = self.tool.run(query)
        print(f"\nResult snippet (first 300 chars):\n{result[:300]}...\n")
        
        self.assertIn("Python", result, "Result should contain 'Python'")
        self.assertIn("programming language", result.lower(), "Result should mention 'programming language'")
        self.assertIn("wikipedia.org", result, "Result should contain Wikipedia URL")
        
        print("✅ All assertions passed for string input test")
    
    def test_dict_input(self):
        """Test the tool with a dictionary input."""
        query = {"query": "Machine learning"}
        print(f"\nTesting with dictionary input: {json.dumps(query)}")
        
        result = self.tool.run(query)
        print(f"\nResult snippet (first 300 chars):\n{result[:300]}...\n")
        
        self.assertIn("Machine learning", result, "Result should contain 'Machine learning'")
        self.assertIn("artificial intelligence", result.lower(), "Result should mention 'artificial intelligence'")
        self.assertIn("wikipedia.org", result, "Result should contain Wikipedia URL")
        
        print("✅ All assertions passed for dictionary input test")
    
    def test_nonexistent_topic(self):
        """Test the tool with a query that likely won't have a Wikipedia page."""
        query = "xyzabcdefghijklmnopqrstuvwxyz123456789"
        print(f"\nTesting with nonexistent topic: '{query}'")
        
        result = self.tool.run(query)
        print(f"\nFull result:\n{result}\n")
        
        self.assertIn("No Wikipedia articles found", result, 
                      "Result should indicate no articles were found")
        
        print("✅ All assertions passed for nonexistent topic test")
    
    def test_disambiguation(self):
        """Test the tool with a query that might lead to disambiguation."""
        query = "Python"
        print(f"\nTesting with potentially ambiguous query: '{query}'")
        
        result = self.tool.run(query)
        print(f"\nResult snippet (first 300 chars):\n{result[:300]}...\n")
        
        self.assertIn("Python", result, "Result should contain 'Python'")
        self.assertTrue(len(result) > 100, "Result should be substantial (>100 chars)")
        
        # Additional verbose output about what was returned
        if "programming language" in result.lower():
            print("✓ Returned the Python programming language")
        elif "snake" in result.lower():
            print("✓ Returned the Python snake")
        else:
            print("✓ Returned some other Python-related article")
        
        print("✅ All assertions passed for disambiguation test")
    
    def test_error_handling(self):
        """Test the tool's error handling with invalid input."""
        query = 123  # Not a string or dict
        print(f"\nTesting with invalid input type: {type(query).__name__} = {query}")
        
        result = self.tool.run(query)
        print(f"\nFull result:\n{result}\n")
        
        self.assertIn("Error", result, "Result should contain an error message")
        
        print("✅ All assertions passed for error handling test")
    
    def test_complex_query(self):
        """Test the tool with a more complex technical query."""
        query = "Transformer neural network architecture"
        print(f"\nTesting with complex technical query: '{query}'")
        
        result = self.tool.run(query)
        print(f"\nResult snippet (first 300 chars):\n{result[:300]}...\n")
        
        # Check for relevant technical content
        technical_terms = ["attention", "neural", "network", "model", "language"]
        found_terms = [term for term in technical_terms if term.lower() in result.lower()]
        
        print(f"Found {len(found_terms)}/{len(technical_terms)} expected technical terms:")
        for term in found_terms:
            print(f"  ✓ Found '{term}'")
        
        self.assertTrue(len(found_terms) >= 2, 
                       f"Result should contain at least 2 technical terms, found {len(found_terms)}")
        self.assertIn("wikipedia.org", result, "Result should contain Wikipedia URL")
        
        print("✅ All assertions passed for complex query test")

if __name__ == "__main__":
    print("\n" + "*"*80)
    print("RUNNING WIKIPEDIA TOOL TESTS")
    print("*"*80)
    unittest.main(verbosity=2) 