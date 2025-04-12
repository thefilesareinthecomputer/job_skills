import os
import sys
from pathlib import Path
import time
from typing import List, Dict, Any

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.job_skills.tools.howdoi_tool import HowDoITool
from dotenv import load_dotenv

load_dotenv()

class TestResult:
    def __init__(self, query: str, response: str, category: str):
        self.query = query
        self.response = response
        self.category = category
        self.success = self._evaluate_success(response)
        self.code_blocks = self._count_code_blocks(response)
        self.length = len(response)
    
    def _evaluate_success(self, response: str) -> bool:
        """Determine if the response appears to be successful."""
        if "No answer found on Stack Overflow" in response:
            return False
        if "Error" in response and len(response) < 200:
            return False
        return True
    
    def _count_code_blocks(self, response: str) -> int:
        """Count the number of code blocks in the response."""
        # Simple heuristic: count the number of lines that start with 4 spaces or a tab
        lines = response.split('\n')
        code_lines = [line for line in lines if line.startswith('    ') or line.startswith('\t')]
        # If we have at least 3 code lines, consider it a code block
        return len(code_lines) // 3

def test_howdoi_tool_queries():
    """Test the HowDoITool with a wide range of query types."""
    
    # Create the tool
    tool = HowDoITool()
    
    # Define test query categories and queries
    test_queries = {
        "Basic Programming": [
            "python read file",
            "python write to file",
            "python sort list",
            "python sort dictionary by value",
            "python remove duplicates from list",
            "python check if key in dictionary",
            "python convert string to datetime",
            "python regular expression match email"
        ],
        "Data Structures": [
            "python implement queue",
            "python implement stack",
            "python implement linked list",
            "python implement binary tree",
            "python implement hash table",
            "python implement graph",
            "python implement priority queue"
        ],
        "Data Science": [
            "python pandas read csv",
            "python pandas filter dataframe",
            "python pandas group by",
            "python pandas merge dataframes",
            "python matplotlib plot bar chart",
            "python seaborn heatmap",
            "python numpy array operations"
        ],
        "Machine Learning": [
            "python scikit-learn classification example",
            "python scikit-learn regression example",
            "python scikit-learn clustering example",
            "python scikit-learn model evaluation",
            "python scikit-learn cross validation",
            "python scikit-learn hyperparameter tuning"
        ],
        "Deep Learning": [
            "python tensorflow neural network example",
            "python pytorch neural network example",
            "python keras lstm example",
            "python tensorflow image classification",
            "python pytorch transfer learning",
            "python keras text classification"
        ],
        "Web Development": [
            "python flask hello world",
            "python django create model",
            "python fastapi endpoint",
            "python requests post json",
            "python beautiful soup scrape table"
        ],
        "DevOps & Deployment": [
            "python docker example",
            "python kubernetes deployment",
            "python aws lambda function",
            "python github actions workflow",
            "python setup logging"
        ],
        "Complex Phrases": [
            "how to implement a neural network from scratch in python",
            "best practices for deploying machine learning models",
            "steps to build a recommendation system in python",
            "techniques for natural language processing in python",
            "how to optimize python code for performance"
        ],
        "Non-Programming Questions": [
            "what is machine learning",
            "difference between AI and ML",
            "explain deep learning",
            "what is transfer learning",
            "explain reinforcement learning"
        ]
    }
    
    # Store results
    results: List[TestResult] = []
    
    # Run tests for each category
    for category, queries in test_queries.items():
        print(f"\n{'='*80}\nTesting category: {category}\n{'='*80}\n")
        
        for query in queries:
            print(f"\nTesting query: {query}")
            
            # Run the tool
            start_time = time.time()
            response = tool._run(query)
            elapsed_time = time.time() - start_time
            
            # Store result
            result = TestResult(query, response, category)
            results.append(result)
            
            # Print summary
            status = "✅ Success" if result.success else "❌ Failed"
            print(f"{status} | Code blocks: {result.code_blocks} | Length: {result.length} chars | Time: {elapsed_time:.2f}s")
            
            # Avoid rate limiting
            time.sleep(1)
    
    # Analyze results
    print("\n\n" + "="*80)
    print("RESULTS SUMMARY")
    print("="*80)
    
    # Overall statistics
    total_queries = len(results)
    successful_queries = sum(1 for r in results if r.success)
    success_rate = (successful_queries / total_queries) * 100
    
    print(f"\nOverall Success Rate: {success_rate:.1f}% ({successful_queries}/{total_queries})")
    
    # Category statistics
    print("\nSuccess Rate by Category:")
    for category in test_queries.keys():
        category_results = [r for r in results if r.category == category]
        category_success = sum(1 for r in category_results if r.success)
        category_rate = (category_success / len(category_results)) * 100
        print(f"  {category}: {category_rate:.1f}% ({category_success}/{len(category_results)})")
    
    # Best performing queries
    print("\nTop 5 Most Successful Queries (by code blocks and length):")
    top_queries = sorted(results, key=lambda r: (r.success, r.code_blocks, r.length), reverse=True)[:5]
    for i, result in enumerate(top_queries, 1):
        print(f"  {i}. '{result.query}' - {result.code_blocks} code blocks, {result.length} chars")
    
    # Worst performing queries
    print("\nTop 5 Least Successful Queries:")
    bottom_queries = sorted(results, key=lambda r: (r.success, r.code_blocks, r.length))[:5]
    for i, result in enumerate(bottom_queries, 1):
        print(f"  {i}. '{result.query}' - {'Success' if result.success else 'Failed'}, {result.code_blocks} code blocks")
    
    # Generate recommendations
    print("\nRECOMMENDATIONS FOR AGENT INSTRUCTIONS:")
    print("\n1. Best Query Patterns:")
    best_patterns = [
        f"'{q.query}'" for q in sorted(
            [r for r in results if r.success and r.code_blocks > 0], 
            key=lambda r: (r.code_blocks, r.length), 
            reverse=True
        )[:5]
    ]
    print("   " + "\n   ".join(best_patterns))
    
    print("\n2. Best Categories:")
    category_success_rates = {}
    for category in test_queries.keys():
        category_results = [r for r in results if r.category == category]
        category_success = sum(1 for r in category_results if r.success and r.code_blocks > 0)
        category_rate = (category_success / len(category_results)) * 100
        category_success_rates[category] = category_rate
    
    best_categories = sorted(category_success_rates.items(), key=lambda x: x[1], reverse=True)[:3]
    for category, rate in best_categories:
        print(f"   {category}: {rate:.1f}% success rate")
    
    print("\n3. Recommended Query Format:")
    print("   'python [library/framework] [specific operation]'")
    print("   Examples:")
    for result in sorted(results, key=lambda r: (r.code_blocks, r.length), reverse=True)[:3]:
        if result.success and result.code_blocks > 0:
            print(f"   - {result.query}")
    
    print("\n4. Query Types to Avoid:")
    print("   - Conceptual questions (what is X, explain Y)")
    print("   - Very long, complex queries")
    print("   - Queries without specific programming tasks")
    
    # Write detailed results to file
    output_dir = project_root / "logs" / "test_results"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"howdoi_test_results_{timestamp}.txt"
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("HOWDOI TOOL TEST RESULTS\n")
        f.write("="*80 + "\n\n")
        
        f.write(f"Overall Success Rate: {success_rate:.1f}% ({successful_queries}/{total_queries})\n\n")
        
        f.write("DETAILED RESULTS BY CATEGORY:\n\n")
        
        for category, queries in test_queries.items():
            f.write(f"Category: {category}\n")
            f.write("-"*80 + "\n")
            
            category_results = [r for r in results if r.category == category]
            for result in category_results:
                status = "SUCCESS" if result.success else "FAILED"
                f.write(f"Query: '{result.query}' - {status}\n")
                f.write(f"Code Blocks: {result.code_blocks}, Length: {result.length} chars\n")
                f.write(f"Response Preview: {result.response[:200]}...\n\n")
            
            f.write("\n")
    
    print(f"\nDetailed results written to: {output_file}")

if __name__ == "__main__":
    test_howdoi_tool_queries() 