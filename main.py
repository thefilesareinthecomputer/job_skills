#!/usr/bin/env python3
import os
import subprocess
from pathlib import Path

def main():
    """
    Simple script to run the CrewAI application with real-time output.
    """
    # Get the root directory of the project
    root_dir = Path(__file__).parent.absolute()
    
    # Path to the job_skills directory
    job_skills_dir = root_dir / "job_skills"
    
    # Check if the directory exists
    if not job_skills_dir.exists():
        print(f"Error: Directory {job_skills_dir} not found.")
        return 1
    
    # Change to the job_skills directory
    os.chdir(job_skills_dir)
    print(f"Changed directory to: {os.getcwd()}")
    
    # Run the crewai run command with real-time output
    print("Running CrewAI...")
    
    # Use subprocess.Popen to get real-time output
    process = subprocess.Popen(
        ["crewai", "run"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1  # Line buffered
    )
    
    # Print output in real-time
    for line in process.stdout:
        print(line, end='')  # end='' because the line already has a newline
    
    # Wait for the process to complete and get the return code
    return_code = process.wait()
    
    if return_code != 0:
        print(f"\nCrewAI command failed with return code {return_code}")
        return return_code
    
    # Check for the report file
    report_path = os.path.join(os.getcwd(), "report.md")
    if os.path.exists(report_path):
        print(f"\nReport saved to: {report_path}")
    else:
        # Check if it's in the root directory
        root_report_path = os.path.join(root_dir, "report.md")
        if os.path.exists(root_report_path):
            print(f"\nReport saved to: {root_report_path}")
    
    return 0

if __name__ == "__main__":
    exit(main()) 