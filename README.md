# LinkedIn Job Skills Analyzer

## Overview

The LinkedIn Job Skills Analyzer is a Python tool that extracts, analyzes, and visualizes skills from LinkedIn job postings. It uses Optical Character Recognition (OCR) to extract text from screenshots of LinkedIn job listings, identifies the skills listed by job posters, and generates insights about the most in-demand skills in your job market.

## Features

- **Automated Skill Extraction**: Extract skills from LinkedIn job posting screenshots
- **Intelligent Parsing**: Specifically targets the "Skills added by the job poster" section
- **Skill Normalization**: Standardizes variations of the same skill (e.g., "Python Programming" → "Python")
- **OCR Error Correction**: Handles common OCR misreadings and artifacts
- **Data Visualization**: Creates a bar chart of the most frequently occurring skills
- **CSV Export**: Saves all extracted skills with their occurrence counts for further analysis

## Requirements

- Python 3.6+
- Tesseract OCR engine
- Python packages listed in `requirements.txt`

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/linkedin-job-skills-analyzer.git
   cd linkedin-job-skills-analyzer
   ```

2. **Create and activate a virtual environment** (recommended):
   ```bash
   python -m venv venv_job_skills
   # On Windows
   venv_job_skills\Scripts\activate
   # On macOS/Linux
   source venv_job_skills/bin/activate
   ```

3. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Tesseract OCR**:
   - **macOS**: `brew install tesseract`
   - **Windows**: Download from [UB-Mannheim's GitHub](https://github.com/UB-Mannheim/tesseract/wiki)
   - **Linux**: `sudo apt-get install tesseract-ocr`

5. **Configure the environment**:
   - Create a `.env` file in the project root
   - Set `IMAGES_PATH` to the folder containing your LinkedIn screenshots
   ```
   IMAGES_PATH=~/Desktop/job_skills_images/
   ```

## Usage

1. **Collect LinkedIn job posting screenshots**:
   - Take screenshots of the "Skills added by the job poster" section from LinkedIn job postings
   - Save them to your designated images folder (default: `~/Desktop/job_skills_images/`)

2. **Run the analyzer**:
   ```bash
   python main.py
   ```

3. **View the results**:
   - A bar chart will be displayed and saved to `output/top_skills.png`
   - A CSV file with all skills and their frequencies will be saved to `output/skill_analysis.csv`
   - Debug information is saved to `output/debug/` for troubleshooting

## How It Works

1. **Image Processing**: The script loads each image and passes it to Tesseract OCR
2. **Text Extraction**: Tesseract extracts text from the images
3. **Skill Identification**: The script identifies the "Skills added by the job poster" section and extracts individual skills
4. **Normalization**: Skills are normalized to handle variations and correct OCR errors
5. **Analysis**: The script counts occurrences of each skill and ranks them by frequency
6. **Visualization**: A bar chart is generated showing the most common skills
7. **Export**: Results are saved to CSV for further analysis

## Project Structure 