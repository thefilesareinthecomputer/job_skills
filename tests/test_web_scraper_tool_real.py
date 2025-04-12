import os
import sys
import unittest
from pathlib import Path

# Add the src directory to the path so we can import the module
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.job_skills.tools.web_scraper_tool import WebScraperTool

class WebScraperToolRealTest(unittest.TestCase):
    """Test the WebScraperTool with real websites."""
    
    def setUp(self):
        """Set up the test environment."""
        self.scraper = WebScraperTool()
    
    def test_scrape_python_docs(self):
        """Test scraping Python documentation - a real, useful site."""
        url = "https://docs.python.org/3/library/unittest.html"
        result = self.scraper._run(url, depth=1)
        
        # Verify we got substantial content
        self.assertGreater(len(result), 5000)
        
        # Verify content relevance
        self.assertIn("unittest", result)
        self.assertIn("TestCase", result)
        
        # Verify code examples were extracted
        self.assertIn("```", result)
    
    def test_invalid_url(self):
        """Test handling of invalid URLs."""
        result = self.scraper._run("not_a_valid_url", depth=1)
        self.assertIn("Invalid URL", result)
    
    def test_log_file_creation(self):
        """Test that log files are created correctly."""
        url = "https://docs.python.org/3/library/unittest.html"
        self.scraper._run(url, depth=1)
        
        # Check log file exists
        log_files = list(self.scraper._log_dir.glob("scrape_docs_python_org*.txt"))
        self.assertGreater(len(log_files), 0)

if __name__ == "__main__":
    unittest.main() 