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
- **Research Logging**: Automatically saves all tool interactions and research results to disk for later analysis or use in RAG applications

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

3. **Skill Coach**: Provides personalized recommendations for skill development
   - Offers tailored learning paths and resources
   - Helps users stay updated with the latest trends
   - Provides feedback on skill proficiency

## 📊 Tools

### OCR Integration

Extracts text from job posting images:

- Processes screenshots of job listings
- Identifies skills and requirements from visual content
- Logs ranked OCR results as CSV for later use

### Skills CSV Tool

Provides access to a dataset of real AI/ML skills extracted from job postings:

- Ranks skills by occurrence in actual job listings
- Supports both broad overview and targeted skill queries
- Displays the exact terminology used by employers

### Wikipedia Search Tool

Accesses Wikipedia for factual information about technologies and concepts:

- Provides definitions and background information
- Includes key sections and related articles
- Logs all searches and results for later use

### Perplexity Research Tool

Connects to the Perplexity API to provide up-to-date information:

- Researches current trends and emerging technologies
- Provides context and details about specific skills
- Logs all queries and responses to disk for future reference

### HowDoI Tool

Accesses Stack Overflow to find programming solutions:

- Retrieves code examples and solutions for programming questions
- Provides implementation details and best practices
- Logs all queries and responses for future reference

## 📝 Research Logging System

The platform includes a comprehensive logging system that:

- **Saves All Research**: Every tool interaction is saved to disk with timestamps and query details
- **Organized Structure**: Logs are organized by tool type in the `logs/tool_logs/` directory
- **Query-Based Filenames**: Log files are named based on the actual queries for easy searching
- **RAG-Ready Format**: Logs are stored in a format that's ready for use in Retrieval Augmented Generation systems
- **Persistent Knowledge**: Research results can be reused across sessions or incorporated into other AI applications

### Log Locations

- Perplexity API results: `logs/tool_logs/perplexity/{timestamp}_perplexity_{query}.txt`
- Wikipedia search results: `logs/tool_logs/wikipedia/wikipedia_{query}.txt`
- Other tool results: `logs/tool_logs/{tool_name}/{filename}`

## 🧩 How to Use

### Installation

```bash
git clone https://github.com/yourusername/job-skills-analysis.git
cd job-skills-analysis
pip install -e .
```

### Configuration

Create a `.env` file with your API keys:

```
OPENAI_API_KEY=your_openai_api_key
MODEL_NAME=gpt-4o-mini
PERPLEXITY_API_KEY=your_perplexity_api_key
PROJECT_ROOT=/path/to/your/project
IMAGES_PATH=/path/to/your/images
TESSERACT_PATH=/path/to/your/tesseract
```

### Run the application

```bash
crewai run
```

### Example Queries

- Search for specific skills: `"Python"` or `"Machine Learning"`
- Research emerging trends: `"What are the emerging AI skills for 2025 and beyond?"`

## 🧪 Testing

Run the test suite to verify all components are working correctly:

```bash
python -m job_skills.tests.test_perplexity_api
python -m job_skills.tests.test_perplexity_tool
python -m job_skills.tests.test_skills_csv_tool
python -m job_skills.tests.test_wikipedia_tool
python -m job_skills.tests.test_howdoi_tool
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

## 🔄 Using Logged Research in RAG Applications

The logged research data can be used in RAG (Retrieval Augmented Generation) applications:

1. **Document Indexing**: Index the log files using tools like LangChain, LlamaIndex, or Pinecone
2. **Knowledge Retrieval**: Use the indexed data to retrieve relevant information for new queries
3. **Enhanced Generation**: Augment LLM responses with the retrieved information for more accurate and up-to-date answers

Example RAG integration:

```python
from langchain.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma

# Load the research logs
loader = DirectoryLoader("logs/tool_logs/", glob="**/*.txt")
documents = loader.load()

# Split into chunks
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
texts = text_splitter.split_documents(documents)

# Create vector store
embeddings = OpenAIEmbeddings()
db = Chroma.from_documents(texts, embeddings)

# Retrieve relevant information for a query
docs = db.similarity_search("What are the most in-demand AI skills?")
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📄 Acknowledgements

- [CrewAI](https://github.com/joaomdmoura/crewAI) for the multi-agent orchestration framework
- [Perplexity AI](https://www.perplexity.ai/) for providing the research API
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) for image text extraction 
- [Wikipedia](https://www.wikipedia.org/) for providing the factual information
- [HowDoI](https://github.com/gleitz/howdoi) for Stack Overflow code solutions