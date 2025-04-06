import os
import sys
from pathlib import Path

def find_csv_file():
    """Find the skill_analysis.csv file."""
    
    print("🔍 Searching for skill_analysis.csv file...")
    print(f"Current working directory: {os.getcwd()}")
    
    # List of possible locations to search
    search_locations = [
        # Current directory
        os.getcwd(),
        
        # Parent directories
        Path(os.getcwd()).parent,
        Path(os.getcwd()).parent.parent,
        
        # Common project paths
        os.path.join(os.getcwd(), "src"),
        os.path.join(os.getcwd(), "src", "output"),
        os.path.join(os.getcwd(), "output"),
        os.path.join(os.getcwd(), "data"),
        
        # Relative to this script
        Path(__file__).parent,
        Path(__file__).parent.parent,
        Path(__file__).parent.parent / "src",
        Path(__file__).parent.parent / "src" / "output",
    ]
    
    # Search for the file in all locations
    found_files = []
    for location in search_locations:
        location_path = Path(location)
        print(f"Searching in: {location_path}")
        
        # Check if the directory exists
        if not location_path.exists():
            print(f"  - Directory does not exist")
            continue
        
        # Look for the file directly in this location
        csv_path = location_path / "skill_analysis.csv"
        if csv_path.exists():
            print(f"  - ✅ FOUND: {csv_path}")
            found_files.append(str(csv_path))
        
        # Also search subdirectories (up to 2 levels deep)
        try:
            for subdir in location_path.glob("**/"):
                if subdir.name.startswith('.'):  # Skip hidden directories
                    continue
                    
                csv_path = subdir / "skill_analysis.csv"
                if csv_path.exists():
                    print(f"  - ✅ FOUND: {csv_path}")
                    found_files.append(str(csv_path))
        except Exception as e:
            print(f"  - Error searching subdirectories: {e}")
    
    # Summary
    if found_files:
        print("\n✅ Found skill_analysis.csv at the following locations:")
        for i, file_path in enumerate(found_files, 1):
            print(f"{i}. {file_path}")
        
        # Suggest the path to use
        print("\nSuggested path to use in your tool:")
        print(f"self._csv_path = '{found_files[0]}'")
    else:
        print("\n❌ Could not find skill_analysis.csv in any of the searched locations.")
        print("Please create the file or specify its exact location.")
    
    return found_files

if __name__ == "__main__":
    find_csv_file() 