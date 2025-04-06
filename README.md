# Job Skills Analysis Platform

![Job Skills Analysis](https://img.shields.io/badge/AI-Job%20Skills%20Analysis-blue)
![Python](https://img.shields.io/badge/Python-3.9%2B-brightgreen)
![CrewAI](https://img.shields.io/badge/CrewAI-Latest-orange)
![License](https://img.shields.io/badge/License-MIT-green)

An AI-powered platform for analyzing and researching in-demand skills for AI Engineers and Machine Learning Engineers. This project uses crewAI to orchestrate specialized AI agents, gathers skills data from real job posts, augments the skills data with perplexity search, generates a report that provides comprehensive insights into the current job market.

## 🚀 Features

- **AI Agent Collaboration**: Utilizes CrewAI to orchestrate specialized AI agents that work together to research and analyze job skills
- **Real Job Posting Data**: Analyzes actual job postings to extract the most in-demand skills with occurrence metrics
- **OCR Integration**: Extracts text from job posting images using Optical Character Recognition
- **Perplexity API Integration**: Accesses up-to-date information about AI/ML job skills, technologies, and trends
- **Customizable Research**: Allows for targeted queries about specific skills or comprehensive market analysis
- **Report Generation**: Generates a comprehensive report on in-demand skills, trends, learning paths, and recommendations for skill development

## 🛠️ Architecture

The platform is built around a multi-agent system using CrewAI:

1. **Research Agent**: Specialized in talent market analysis and skill forecasting
   - Accesses the Skills CSV dataset
   - Utilizes Perplexity AI for up-to-date research
   - Analyzes trends and patterns in job requirements

2. **Reporting Analyst**: Transforms research into actionable insights
   - Creates comprehensive reports on in-demand skills
   - Provides strategic recommendations for skill development
   - Formats findings for easy consumption

## 📊 Tools

### Skills CSV Tool

Provides access to a dataset of real AI/ML skills extracted from job postings:

- Ranks skills by occurrence in actual job listings
- Supports both broad overview and targeted skill queries
- Displays the exact terminology used by employers

### OCR Integration

Extracts text from job posting images:

- Processes screenshots of job listings
- Identifies skills and requirements from visual content
- Integrates findings with other data sources

### Perplexity AI Research Tool

Connects to Perplexity AI to provide current information from across the web:

- Researches specific skills and technologies
- Analyzes job market trends
- Identifies learning resources and certification paths
- Provides context on emerging technologies

## 🔧 Setup and Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/thefilesareinthecomputer/job_skills_research_agents.git
   cd job_skills_research_agents
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv venv_job_skills
   source venv_job_skills/bin/activate  # On Windows: venv_job_skills\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the root directory with the following variables:
   ```
   SKILLS_CSV_PATH="/path/to/your/skill_analysis.csv"
   IMAGES_PATH="/path/to/your/job_skills_images/"
   TESSERACT_PATH="/path/to/tesseract"
   OPENAI_API_KEY="your_openai_api_key"
   PERPLEXITY_API_KEY="your_perplexity_api_key"
   MODEL="gpt-4o-mini"  # Or your preferred model
   ```

## 📝 Usage

### Run the application
```bash
python main
python main.py
crewai run --active
```

### Running a Research Task

```python
from job_skills import JobSkills

# Initialize the crew
job_skills_crew = JobSkills()

# Run the crew to generate a comprehensive skills report
result = job_skills_crew.crew.kickoff()

# The report will be saved to report.md
print(f"Report generated: {result}")
```

### Sample Queries

- Get all skills: `"List all skills"`
- Search for specific skills: `"Python"` or `"Machine Learning"`
- Research emerging trends: `"What are the emerging AI skills for 2025 and beyond?"`

## 🧪 Testing

Run the test suite to verify all components are working correctly:

```bash
python -m job_skills.tests.test_perplexity_api
python -m job_skills.tests.test_perplexity_tool
python -m job_skills.tests.test_skills_csv_tool
```

## 📈 Example Output

The platform generates comprehensive reports like this:

```markdown
# AI/ML Skills Analysis Report

## Top Skills by Demand
1. **Machine Learning** (105 occurrences)
2. **Python** (99 occurrences)
3. **Artificial Intelligence (AI)** (75 occurrences)
...

## Emerging Technologies
- Large Language Models (LLMs)
- Generative AI
- MLOps

## Recommendations for Skill Development
...
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgements

- [CrewAI](https://github.com/joaomdmoura/crewAI) for the multi-agent orchestration framework
- [Perplexity AI](https://www.perplexity.ai/) for providing the research API
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) for image text extraction 