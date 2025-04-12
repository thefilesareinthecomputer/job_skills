import os
import sys
from pathlib import Path
import time
from typing import List, Dict, Any
import re

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.job_skills.tools.howdoi_tool import HowDoITool
from dotenv import load_dotenv

load_dotenv()

class TestResult:
    def __init__(self, query: str, response: str, category: str, format_type: str = None):
        self.query = query
        self.response = response
        self.category = category
        self.format_type = format_type  # Store the query format type
        self.success = self._evaluate_success(response)
        self.code_blocks = self._count_code_blocks(response)
        self.code_quality = self._evaluate_code_quality(response)
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
        # Extract the actual response content (after "## Solution:")
        solution_match = re.search(r'## Solution:\s*\n\n([\s\S]*)', response)
        if solution_match:
            content = solution_match.group(1)
        else:
            content = response
        
        # Different code block patterns
        patterns = [
            # Markdown code blocks
            r'```[\s\S]*?```',
            
            # Indented code blocks (4+ spaces or tabs)
            r'(?:^|\n)[ \t]{4,}[^\n]+(?:\n[ \t]{4,}[^\n]+)*',
            
            # Python REPL style (>>> followed by code)
            r'(?:^|\n)>>>.*(?:\n[^>\n]+)*',
            
            # Common code patterns without explicit formatting
            r'(?:^|\n)(?:def |class |if __name__ |import |from \w+ import )[^\n]+(?:\n[^\n]+)*',
            
            # Assignment patterns
            r'(?:^|\n)[a-zA-Z_][a-zA-Z0-9_]* = [^\n]+',
            
            # Function calls
            r'(?:^|\n)[a-zA-Z_][a-zA-Z0-9_]*\([^\n]*\)'
        ]
        
        # Count matches for each pattern
        total_blocks = 0
        for pattern in patterns:
            matches = re.findall(pattern, content)
            if matches:
                total_blocks += len(matches)
                print(f"Found {len(matches)} code blocks with pattern: {pattern[:30]}...")
        
        # Print debug info
        print(f"Code block detection: {total_blocks} blocks found")
        if total_blocks > 0:
            print("Code blocks detected!")
        
        return total_blocks
    
    def _evaluate_code_quality(self, response: str) -> float:
        """Rate the quality of code in the response on a scale of 0-10."""
        # Extract the actual response content (after "## Solution:")
        solution_match = re.search(r'## Solution:\s*\n\n([\s\S]*)', response)
        if solution_match:
            content = solution_match.group(1)
        else:
            content = response
            
        if not self.success or self.code_blocks == 0:
            return 0.0
        
        score = 0.0
        
        # Check for presence of code-specific keywords
        code_keywords = ['def ', 'class ', 'import ', 'return ', 'if ', 'for ', 'while ', '= ']
        for keyword in code_keywords:
            if keyword in content:
                score += 0.5
                print(f"Found code keyword: {keyword}")
        
        # Check for comments in code
        if '#' in content or '//' in content:
            score += 1.0
            print("Found comments in code")
        
        # Check for explanation alongside code
        if self.code_blocks > 0 and len(content) > 300:
            score += 2.0
            print("Found explanation with code")
        
        # Bonus for multiple code blocks (showing different approaches)
        if self.code_blocks > 1:
            score += 1.0
            print("Found multiple code blocks")
        
        # Cap at 10
        return min(score, 10.0)

def test_query_format_variations():
    """Test different query format variations to determine which ones work best."""
    
    # Create the tool
    tool = HowDoITool()
    
    # Define base operations and languages to test
    operations = ["sort list", "read file", "create dictionary", "filter array"]
    languages = ["python", "javascript", "java"]
    
    # Define different query format patterns
    format_types = {
        "operation_only": lambda op, lang: op,
        "language_first": lambda op, lang: f"{lang} {op}",
        "operation_then_language": lambda op, lang: f"{op} in {lang}",
        "how_do_i": lambda op, lang: f"how do I {op} in {lang}",
        "language_operation_example": lambda op, lang: f"{lang} {op} example"
    }
    
    # Store results
    results: List[TestResult] = []
    
    # Run tests for each format type
    for format_name, format_func in format_types.items():
        print(f"\n{'='*80}\nTesting format: {format_name}\n{'='*80}\n")
        
        # Test each operation with each language
        for operation in operations:
            for language in languages:
                # Generate query using this format
                query = format_func(operation, language)
                
                print(f"\nTesting query: '{query}'")
                print(f"(Tool will run as: 'howdoi {query}')")
                
                # Run the tool
                start_time = time.time()
                response = tool._run(query)
                elapsed_time = time.time() - start_time
                
                # Store result
                result = TestResult(query, response, language, format_name)
                results.append(result)
                
                # Print summary
                status = "✅ Success" if result.success else "❌ Failed"
                print(f"{status} | Code blocks: {result.code_blocks} | Quality: {result.code_quality:.1f}/10 | Length: {result.length} chars | Time: {elapsed_time:.2f}s")
                
                # Avoid rate limiting
                time.sleep(5)  # Increased delay to avoid rate limiting
    
    # Analyze results by format type
    print("\n\n" + "="*80)
    print("QUERY FORMAT ANALYSIS")
    print("="*80)
    
    # Overall statistics by format type
    print("\nSuccess Rate by Format Type:")
    for format_type in format_types.keys():
        format_results = [r for r in results if r.format_type == format_type]
        format_success = sum(1 for r in format_results if r.success)
        format_with_code = sum(1 for r in format_results if r.code_blocks > 0)
        
        if format_results:
            success_rate = (format_success / len(format_results)) * 100
            code_rate = (format_with_code / len(format_results)) * 100
            print(f"  {format_type}: {success_rate:.1f}% success, {code_rate:.1f}% with code ({format_with_code}/{len(format_results)})")
    
    # Success rate by language
    print("\nSuccess Rate by Language:")
    for language in languages:
        language_results = [r for r in results if r.category == language]
        language_success = sum(1 for r in language_results if r.success)
        language_with_code = sum(1 for r in language_results if r.code_blocks > 0)
        
        if language_results:
            success_rate = (language_success / len(language_results)) * 100
            code_rate = (language_with_code / len(language_results)) * 100
            print(f"  {language}: {success_rate:.1f}% success, {code_rate:.1f}% with code ({language_with_code}/{len(language_results)})")
    
    # Best performing format for each language
    print("\nBest Format by Language:")
    for language in languages:
        best_format = None
        best_code_rate = 0
        
        for format_type in format_types.keys():
            format_lang_results = [r for r in results if r.format_type == format_type and r.category == language]
            format_lang_with_code = sum(1 for r in format_lang_results if r.code_blocks > 0)
            
            if format_lang_results and format_lang_with_code / len(format_lang_results) > best_code_rate:
                best_code_rate = format_lang_with_code / len(format_lang_results)
                best_format = format_type
        
        if best_format:
            print(f"  {language}: {best_format} ({best_code_rate*100:.1f}% with code)")
    
    # Best performing queries
    print("\nTop 5 Most Successful Queries:")
    top_queries = sorted(results, key=lambda r: (r.code_blocks, r.code_quality), reverse=True)[:5]
    for i, result in enumerate(top_queries, 1):
        print(f"  {i}. '{result.query}' - Format: {result.format_type}, Code blocks: {result.code_blocks}")
    
    # Write detailed results to file
    output_dir = project_root / "logs" / "test_results"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"howdoi_format_test_{timestamp}.txt"
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("HOWDOI QUERY FORMAT TEST RESULTS\n")
        f.write("="*80 + "\n\n")
        
        f.write("RESULTS BY FORMAT TYPE:\n\n")
        
        for format_type in format_types.keys():
            format_results = [r for r in results if r.format_type == format_type]
            format_success = sum(1 for r in format_results if r.success)
            format_with_code = sum(1 for r in format_results if r.code_blocks > 0)
            
            if format_results:
                success_rate = (format_success / len(format_results)) * 100
                code_rate = (format_with_code / len(format_results)) * 100
                
                f.write(f"Format: {format_type}\n")
                f.write("-"*80 + "\n")
                f.write(f"Success Rate: {success_rate:.1f}%, Code Rate: {code_rate:.1f}%\n\n")
                
                for result in format_results:
                    status = "SUCCESS" if result.success else "FAILED"
                    code_status = "HAS CODE" if result.code_blocks > 0 else "NO CODE"
                    f.write(f"Query: 'howdoi {result.query}' - {status}, {code_status}\n")
                    f.write(f"Language: {result.category}, Code Blocks: {result.code_blocks}\n")
                    f.write(f"Response Preview: {result.response[:200]}...\n\n")
                
                f.write("\n")
    
    print(f"\nDetailed results written to: {output_file}")
    
    # Return the best format based on results
    best_format = max(format_types.keys(), 
                      key=lambda fmt: sum(1 for r in results if r.format_type == fmt and r.code_blocks > 0) / 
                                     max(1, len([r for r in results if r.format_type == fmt])))
    
    print(f"\nRECOMMENDED QUERY FORMAT: {best_format}")
    return best_format

if __name__ == "__main__":
    best_format = test_query_format_variations()
    print(f"\nBased on testing, the recommended query format is: {best_format}") 