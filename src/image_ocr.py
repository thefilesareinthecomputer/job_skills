import os
import pandas as pd
import pytesseract
from PIL import Image
from dotenv import load_dotenv
import re
import matplotlib.pyplot as plt
from pathlib import Path
import csv

# Load environment variables
load_dotenv()

def setup_directories():
    """Create necessary directories if they don't exist."""
    # Create directories for images and output
    Path("src/images").mkdir(exist_ok=True)
    Path("src/output").mkdir(exist_ok=True)
    
    print("✅ Directories set up")

def extract_text_from_image(image_path):
    """Extract text from an image using OCR, optimized for LinkedIn screenshots."""
    try:
        img = Image.open(image_path)
        
        # Try different OCR configurations for better results
        # First try with default settings
        custom_config = r'--oem 3 --psm 6'
        text = pytesseract.image_to_string(img, config=custom_config)
        
        # If text is very short, try with different PSM mode
        if len(text.strip()) < 20:
            custom_config = r'--oem 3 --psm 4'  # Assume single column of text
            text = pytesseract.image_to_string(img, config=custom_config)
        
        # Debug: Save extracted text
        debug_dir = Path("src/output/debug")
        debug_dir.mkdir(exist_ok=True)
        with open(debug_dir / f"{os.path.basename(image_path)}.txt", "w") as f:
            f.write(text)
            
        return text
    except Exception as e:
        print(f"Error processing {image_path}: {e}")
        return ""

def parse_skills(text):
    """Parse skills from extracted text from LinkedIn job postings."""
    skills = []
    
    # Common LinkedIn skill section headers with variations for OCR errors
    skill_headers = [
        "skills added by the job poster",
        "skills added by job poster",
        "skills added by",
        "skills listed by",
        "skills required",
        "required skills",
        "preferred skills",
        "desired skills"
    ]
    
    # Words to exclude (preferences, job types, etc.)
    exclude_words = [
        'preferences', 'remote', 'full-time', 'part-time', 'contract', 
        'temporary', 'permanent', 'hybrid', 'on-site', 'internship',
        'entry level', 'associate', 'mid-senior level', 'director',
        'executive', '+', '++', '+++', 'match', 'matches', 'preference',
        'about the job', 'about this job', 'job description', 'qualifications'
    ]
    
    # Check if the text contains any LinkedIn skills section header
    skills_section = False
    lines = text.split('\n')
    
    for i, line in enumerate(lines):
        line = line.strip().lower()
        
        # Skip empty lines
        if not line:
            continue
        
        # Check for skills section headers with fuzzy matching
        if any(header in line for header in skill_headers):
            skills_section = True
            continue
        
        # If we're in the skills section, process the skills
        if skills_section:
            # Check if we've reached the end of skills section
            if any(exclude.lower() in line for exclude in exclude_words) and len(line) > 10:
                # Only exit skills section if this looks like a new section header
                if line.endswith(':') or line.isupper() or i > 0 and not lines[i-1].strip():
                    skills_section = False
                    continue
            
            # Skip lines that are likely not skills
            if any(exclude.lower() == line.lower() for exclude in exclude_words):
                continue
                
            # Skip very short lines or lines that are just symbols
            if len(line) <= 2 or line.strip('+-*/=.,:;()[]{}') == '':
                continue
                
            # Clean up the skill
            skill = line.strip()
            skill = re.sub(r'^[@•⋅·*>-]\s*', '', skill)  # Remove leading symbols
            skill = re.sub(r'[.:]$', '', skill)  # Remove trailing periods or colons
            
            # Skip lines that are just symbols or OCR artifacts
            if re.match(r'^[-—–*•⋅·+]+$', skill) or re.match(r'^[^a-z0-9]+$', skill):
                continue
                
            # Skip common non-skill words
            if re.match(r'^(and|the|or|with|for|in|on|to|of|a|an)$', skill.lower()):
                continue
                
            # Skip if it's too long to be a skill (likely a sentence)
            if len(skill) > 50:
                continue
                
            if skill:
                skills.append(skill)
    
    # If no skills were found with the section header approach, try a fallback method
    if not skills:
        # Look for bullet-pointed items that might be skills
        for line in lines:
            line = line.strip()
            # Check if line starts with a bullet-like character
            if re.match(r'^[@•⋅·*>-]', line):
                skill = re.sub(r'^[@•⋅·*>-]\s*', '', line)
                skill = re.sub(r'[.:]$', '', skill)
                
                # Apply the same filtering as above
                if (skill and len(skill) > 2 and len(skill) <= 50 and 
                    not re.match(r'^(and|the|or|with|for|in|on|to|of|a|an)$', skill.lower()) and
                    not any(exclude.lower() == skill.lower() for exclude in exclude_words) and
                    not re.match(r'^[-—–*•⋅·+]+$', skill) and 
                    not re.match(r'^[^a-z0-9]+$', skill)):
                    skills.append(skill)
    
    return skills

def process_images(image_folder=None):
    """Process all images in the specified folder."""
    all_skills = []
    skills_per_image = {}
    
    # Check for custom image path in environment variables
    if image_folder is None:
        image_folder = os.getenv('IMAGES_PATH', 'src/images')
        
    # Convert ~ to user home directory if present
    if image_folder.startswith('~'):
        image_folder = os.path.expanduser(image_folder)
    
    # Ensure the directory exists
    if not os.path.exists(image_folder):
        print(f"Warning: Directory {image_folder} does not exist. Using 'images' directory instead.")
        image_folder = 'src/images'
        Path(image_folder).mkdir(exist_ok=True)
    
    # Get all image files
    image_files = [f for f in os.listdir(image_folder) 
                  if f.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif'))]
    
    if not image_files:
        print("No image files found in the 'images' directory.")
        return pd.DataFrame(columns=["skill"]), []
    
    print(f"Found {len(image_files)} images to process.")
    
    # Process each image
    for image_file in image_files:
        image_path = os.path.join(image_folder, image_file)
        print(f"Processing {image_file}...")
        
        # Extract text from image
        text = extract_text_from_image(image_path)
        
        # Parse skills from text
        skills = parse_skills(text)
        
        # Store skills for this image
        skills_per_image[image_file] = skills
        
        # Add to our collection
        all_skills.extend(skills)
    
    # Print some statistics
    print(f"\nExtracted {len(all_skills)} total skills across {len(image_files)} images")
    print(f"Average of {len(all_skills)/len(image_files):.1f} skills per image")
    
    # Create DataFrame
    df = pd.DataFrame({"skill": all_skills})
    
    return df, all_skills

def analyze_skills(df):
    """Analyze skills by frequency with improved normalization."""
    if df.empty:
        print("No skills to analyze.")
        return df
    
    # Normalize skill names
    df['skill'] = df['skill'].str.lower().str.strip()
    
    # Filter out obvious OCR errors and non-skills
    error_patterns = [
        r'^sa$',           # Common OCR error
        r'^eee+$',         # Repeated characters
        r'^[a-z]$',        # Single letters
        r'^[—–-]+\s*>?$',  # Just dashes with optional >
        r'^[^a-z0-9]+$',   # Strings with no alphanumeric characters
        r'^ch$',           # Common OCR error
        r'^o os$',         # Common OCR error
        r'^ng$',           # Common OCR error
        r'^ops$',          # Too generic
        r'^c$',            # Single letter (C programming language should be "c programming")
        r'^xm$',           # Common OCR error
        r'^cw$',           # Common OCR error
        r'^tama$',         # Likely OCR error
    ]
    
    for pattern in error_patterns:
        df = df[~df['skill'].str.match(pattern, case=False)]
    
    # Additional normalization for common variations
    def normalize_skill(skill):
        """Normalize skill names and fix common OCR errors."""
        # Remove trailing + characters (LinkedIn's "Add" button)
        skill = re.sub(r'\s*\+\s*$', '', skill)
        
        # Remove leading © or other symbols (OCR artifacts)
        skill = re.sub(r'^[©®™]\s*', '', skill)
        
        # Remove quotes
        skill = skill.replace("'", "").replace('"', '')
        
        # Remove common prefixes/suffixes
        skill = re.sub(r'^experience (in|with) ', '', skill)
        skill = re.sub(r'^knowledge of ', '', skill)
        
        # Fix common OCR errors
        skill = re.sub(r'^ata\b', 'data', skill)  # Fix "ata" -> "data"
        
        # Fix specific OCR errors you identified
        if skill == '—eee':
            return 'FILTERED_OUT'  # We'll filter this out later
        if skill == 'pup':
            return 'FILTERED_OUT'
        if skill == 'ch':
            return 'FILTERED_OUT'
        if skill == 'ng':
            return 'FILTERED_OUT'
        if skill == 'pyth (programming language)':
            return 'python'
        if skill == 'realm database':
            return 'relational database'
        if skill == 'mops':
            return 'mlops'
        if skill == 'conversational al':
            return 'conversational ai'
        
        # Fix "al" -> "ai" ONLY for specific cases where it's likely an OCR error
        # Instead of broad replacement, target specific patterns
        skill = re.sub(r'artificial\s+al\b', 'artificial ai', skill)
        skill = re.sub(r'generative\s+al\b', 'generative ai', skill)
        skill = re.sub(r'\bartificial\s+al\b', 'artificial ai', skill)
        skill = re.sub(r'\bgenerative\s+al\b', 'generative ai', skill)
        skill = re.sub(r'^al\s+tools$', 'ai tools', skill)
        skill = re.sub(r'^al\s+solutions$', 'ai solutions', skill)
        skill = re.sub(r'^al\s+prompting$', 'ai prompting', skill)
        skill = re.sub(r'\bal\s+studio\b', 'ai studio', skill)
        skill = re.sub(r'\bconversational\s+al\b', 'conversational ai', skill)
        
        # Normalize programming languages
        if re.match(r'^python\b', skill):
            return 'python'
        if re.match(r'^(javascript|js)\b', skill):
            return 'javascript'
        if re.match(r'^(sql|mysql|postgresql|tsql)\b', skill):
            return 'sql'
        
        # Normalize AI/ML terms
        if re.search(r'\bartificial intelligence\b', skill) or skill == 'ai':
            return 'artificial intelligence (ai)'
        if re.search(r'\bmachine learning\b', skill) or skill == 'ml':
            return 'machine learning'
        if re.search(r'\bnatural language processing\b', skill) or skill == 'nlp':
            return 'natural language processing (nlp)'
        if re.search(r'\blarge language model', skill) or re.search(r'\bllm\b', skill):
            return 'large language models (llms)'
        if re.search(r'\bgenerative ai\b', skill):
            return 'generative ai'
        
        # Normalize data science terms
        if 'data science' in skill:
            return 'data science'
        if 'data analysis' in skill or 'data analytics' in skill:
            return 'data analysis'
        if re.search(r'data\s*engineering', skill):
            return 'data engineering'
        if re.search(r'(etl|extract,?\s*transform,?\s*load)', skill):
            return 'extract, transform, load (etl)'
        
        # Normalize cloud platforms
        if re.search(r'(azure|microsoft azure)', skill):
            return 'microsoft azure'
        if re.search(r'(aws|amazon web services)', skill):
            return 'amazon web services (aws)'
        if re.search(r'(gcp|google cloud)', skill):
            return 'google cloud platform (gcp)'
        
        # Normalize ML frameworks
        if 'tensorflow' in skill:
            return 'tensorflow'
        if 'pytorch' in skill:
            return 'pytorch'
        
        # Normalize other common skills
        if 'computer vision' in skill:
            return 'computer vision'
        if 'deep learning' in skill:
            return 'deep learning'
        if 'computer science' in skill:
            return 'computer science'
        
        return skill
    
    df['skill'] = df['skill'].apply(normalize_skill)
    
    # Filter out skills marked for removal
    df = df[df['skill'] != 'FILTERED_OUT']
    
    # Group by skill and count occurrences
    skill_counts = df['skill'].value_counts().reset_index()
    skill_counts.columns = ['skill', 'frequency']
    
    # Sort by frequency (descending)
    skill_counts = skill_counts.sort_values('frequency', ascending=False)
    
    # Post-processing: Remove any remaining skills that look like OCR errors
    # These are skills that appear only once and have unusual patterns
    if len(skill_counts) > 20:  # Only do this if we have enough skills
        # Keep all skills with frequency > 1
        common_skills = skill_counts[skill_counts['frequency'] > 1]
        
        # For skills with frequency = 1, filter out suspicious ones
        rare_skills = skill_counts[skill_counts['frequency'] == 1]
        suspicious_patterns = [
            r'.*\d{4}\+?$',  # Ends with 4 digits (like "sap erp 4+")
            r'^sp-wan',      # Unusual technical terms that are likely OCR errors
            r'^fastapl$',    # Misspelled or unusual terms
        ]
        
        for pattern in suspicious_patterns:
            rare_skills = rare_skills[~rare_skills['skill'].str.match(pattern, case=False)]
        
        # Combine filtered rare skills with common skills
        skill_counts = pd.concat([common_skills, rare_skills])
        skill_counts = skill_counts.sort_values('frequency', ascending=False)
    
    return skill_counts

def visualize_top_skills(skill_counts, top_n=20):
    """Create a bar chart of the top N skills."""
    if skill_counts.empty or len(skill_counts) == 0:
        print("No skills to visualize.")
        return
    
    # Take top N skills
    top_skills = skill_counts.head(top_n)
    
    # Reverse the order for vertical chart (so highest is on left)
    top_skills = top_skills.iloc[::-1]
    
    # Create vertical bar chart
    plt.figure(figsize=(12, 8))
    plt.bar(top_skills['skill'], top_skills['frequency'])
    plt.ylabel('Frequency')
    plt.xlabel('Skill')
    plt.title(f'Top {top_n} Job Skills by Frequency')
    
    # Rotate x-axis labels for better readability
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    # Save the chart
    plt.savefig('src/output/top_skills.png')
    print(f"Chart saved to src/output/top_skills.png")
    
    # Show the chart
    plt.show()

def save_results(skill_counts):
    """Save the results to CSV."""
    if skill_counts.empty:
        print("No results to save.")
        return
    
    # Make a copy to avoid modifying the original DataFrame
    output_df = skill_counts.copy()
    
    # Rename columns to match desired output format
    output_df.columns = ['skill', 'occurrences']
    
    # Fix quotes in specific skills
    output_df['skill'] = output_df['skill'].str.replace('"extract, transform, load (etl)"', 
                                                       'extract, transform, load (etl)')
    
    output_file = 'src/output/skill_analysis.csv'
    
    try:
        # Try to save the file
        output_df.to_csv(output_file, index=False, quoting=csv.QUOTE_MINIMAL)
        print(f"Results saved to {output_file}")
    except PermissionError:
        # Handle case where file is open or locked
        print(f"ERROR: Could not save to {output_file} - file may be open in another program.")
        # Try with a different filename
        alt_file = 'src/output/skill_analysis_new.csv'
        try:
            output_df.to_csv(alt_file, index=False, quoting=csv.QUOTE_MINIMAL)
            print(f"Saved results to alternate file: {alt_file}")
        except Exception as e:
            print(f"Failed to save results: {e}")
    except Exception as e:
        print(f"Error saving results: {e}")

def print_extraction_stats(all_skills, skill_counts):
    """Print statistics about the extraction process."""
    print("\n--- Extraction Statistics ---")
    print(f"Total skills extracted: {len(all_skills)}")
    print(f"Unique skills found: {len(skill_counts)}")
    print(f"Top 10 skills:")
    for i, (skill, count) in enumerate(zip(skill_counts['skill'].head(10), 
                                          skill_counts['frequency'].head(10)), 1):
        print(f"{i}. {skill}: {count}")
    print("---------------------------\n")

def main():
    """Main function to run the analysis."""
    print("Starting Job Skills Analysis")
    
    # Setup directories
    setup_directories()
    
    # Process images and get skills dataframe
    skills_df, all_skills = process_images()
    
    # Analyze skills
    skill_counts = analyze_skills(skills_df)
    
    # Print extraction statistics
    print_extraction_stats(all_skills, skill_counts)
    
    # Visualize top skills
    visualize_top_skills(skill_counts)
    
    # Save results
    save_results(skill_counts)
    
    print("Analysis complete!")

if __name__ == "__main__":
    main()
