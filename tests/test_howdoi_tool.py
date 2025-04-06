import os
import sys
from pathlib import Path

# Add the parent directory to the path so we can import the tool
sys.path.append(str(Path(__file__).parent.parent))

from src.job_skills.tools.howdoi_tool import HowDoITool

def test_howdoi_tool():
    """Test the HowDoI tool."""
    
    print("🧪 Testing HowDoI Tool")
    
    # Create the tool
    tool = HowDoITool()
    
    # Test query - something simple that should have stable answers
    query = "python read file"
    
    print(f"🔄 Sending query to HowDoI: '{query}'")
    
    # Run the tool
    result = tool._run(query, num_answers=1)
    
    # Print the result
    print("\n--- Response Content ---")
    print(result)
    
    # Check if the log file was created
    log_dir = tool._log_dir
    log_files = list(log_dir.glob("howdoi_python_read_file.txt"))
    
    if log_files:
        print(f"\n✅ Log file created at: {log_files[0]}")
    else:
        print("\n⚠️ No log file found in the expected location")
    
    # Basic validation
    if result and "Stack Overflow Solution" in result and not result.startswith("Error"):
        print("\n✅ HowDoI Tool test completed successfully!")
        return True
    else:
        print("\n❌ HowDoI Tool test failed.")
        return False

def test_howdoi_tool_multiple_answers():
    """Test the HowDoI tool with multiple answers."""
    
    print("\n🧪 Testing HowDoI Tool with multiple answers")
    
    # Create the tool
    tool = HowDoITool()
    
    # Test query
    query = "python sort dictionary by value"
    
    print(f"🔄 Sending query to HowDoI with multiple answers: '{query}'")
    
    # Run the tool with 3 answers
    result = tool._run(query, num_answers=3)
    
    # Print the result
    print("\n--- Response Content ---")
    print(result)
    
    # Basic validation - with multiple answers, the response should be longer
    if result and len(result.split('\n')) > 10:
        print("\n✅ HowDoI Tool multiple answers test completed successfully!")
        return True
    else:
        print("\n❌ HowDoI Tool multiple answers test failed.")
        return False

if __name__ == "__main__":
    print("\n" + "*"*80)
    print("RUNNING HOWDOI TOOL TESTS")
    print("*"*80)
    
    # Run the basic test
    basic_test_result = test_howdoi_tool()
    
    # Run the multiple answers test
    multiple_test_result = test_howdoi_tool_multiple_answers()
    
    # Overall result
    if basic_test_result and multiple_test_result:
        print("\n🎉 All HowDoI Tool tests passed!")
        sys.exit(0)
    else:
        print("\n⚠️ Some HowDoI Tool tests failed.")
        sys.exit(1) 