from crewai.tools import BaseTool
from typing import Type, Optional
from pydantic import BaseModel, Field, PrivateAttr
import requests
import os
import json
import datetime
import time
from pathlib import Path
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import re

load_dotenv()

class SerperToolInput(BaseModel):
    """Input schema for SerperTool."""
    query: str = Field(..., description="The search query related to AI/ML topics.")
    num_results: int = Field(5, description="Number of search results to return (1-10).")

class SerperTool(BaseTool):
    name: str = "AI/ML Search Engine"
    description: str = """
    Use this tool to search for information about AI/ML topics, technologies, frameworks, and concepts.
    Perfect for finding the latest information about machine learning techniques, AI frameworks, 
    programming libraries, and best practices in the field of artificial intelligence.
    Input should be a specific AI/ML related query like 'latest advancements in transformer models' 
    or 'best practices for fine-tuning LLMs'.
    """
    args_schema: Type[BaseModel] = SerperToolInput
    
    # Use PrivateAttr for attributes that shouldn't be part of the model schema
    _log_dir: Path = PrivateAttr(default=None)
    _scrape_dir: Path = PrivateAttr(default=None)

    def __init__(self, **data):
        """Initialize the tool with logging directory setup."""
        super().__init__(**data)
        
        # Get the project root directory
        project_root = os.getenv("PROJECT_ROOT")
        
        if not project_root:
            current_file = Path(__file__).resolve()
            project_root = current_file.parent.parent.parent.parent
        else:
            project_root = Path(project_root)
        
        # Create logs directory structure
        self._log_dir = project_root / "logs" / "tool_logs" / "serper"
        self._scrape_dir = project_root / "logs" / "tool_logs" / "serper_scrapes"
        
        try:
            self._log_dir.mkdir(parents=True, exist_ok=True)
            self._scrape_dir.mkdir(parents=True, exist_ok=True)
            print(f"Serper tool log directory: {self._log_dir}")
            print(f"Serper scrape directory: {self._scrape_dir}")
        except Exception as e:
            print(f"Error creating Serper directories: {e}")
            self._log_dir = Path.home() / "job_skills_logs" / "serper"
            self._scrape_dir = Path.home() / "job_skills_logs" / "serper_scrapes"
            self._log_dir.mkdir(parents=True, exist_ok=True)
            self._scrape_dir.mkdir(parents=True, exist_ok=True)
    
    def _create_safe_filename(self, query):
        """Convert a query string into a safe filename."""
        safe_name = query.replace(' ', '_')
        safe_name = ''.join(c for c in safe_name if c.isalnum() or c == '_' or c == '-')
        if not safe_name:
            safe_name = "empty_query"
        return safe_name.lower()
    
    def _log_interaction(self, query, response, timestamp):
        """Log the query and response to a file."""
        try:
            safe_query = self._create_safe_filename(query)
            if len(safe_query) > 50:
                safe_query = safe_query[:50]
            
            log_file = self._log_dir / f"serper_{safe_query}.txt"
            
            with open(log_file, "w", encoding="utf-8") as f:
                f.write("=== SERPER TOOL INTERACTION ===\n\n")
                f.write(f"Timestamp: {timestamp}\n\n")
                f.write("=== INPUT ===\n")
                f.write(f"Query: {query}\n\n")
                f.write("=== OUTPUT ===\n")
                f.write(f"{response}\n")
            
            print(f"Serper interaction logged to: {log_file}")
            return log_file
        except Exception as e:
            print(f"Error writing Serper log file: {e}")
            return None
    
    def _scrape_url(self, url, title):
        """Scrape content from a URL with multiple user agent options and retries."""
        # List of different user agents to try
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Safari/605.1.15',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (iPad; CPU OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0'
        ]
        
        # Try each user agent
        last_error = None
        for i, user_agent in enumerate(user_agents):
            try:
                print(f"Attempt {i+1}/{len(user_agents)} for {url} with user agent: {user_agent[:30]}...")
                
                headers = {
                    'User-Agent': user_agent,
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Referer': 'https://www.google.com/',
                    'DNT': '1',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                    'Cache-Control': 'max-age=0'
                }
                
                # Add a small delay between attempts
                if i > 0:
                    time.sleep(2)
                    
                response = requests.get(url, headers=headers, timeout=15)
                
                # Check if we got a successful response
                if response.status_code == 200:
                    # Parse the HTML content
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Remove script and style elements
                    for script in soup(["script", "style"]):
                        script.extract()
                    
                    # Get the main content
                    main_content = ""
                    
                    # Try to find the main article content
                    article = soup.find('article') or soup.find(attrs={"role": "main"}) or soup.find(class_=re.compile("content|article|post|main"))
                    
                    if article:
                        # If we found a main content area, use that
                        main_content = article.get_text(separator="\n", strip=True)
                    else:
                        # Otherwise, get all paragraphs
                        paragraphs = soup.find_all('p')
                        main_content = "\n".join([p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 50])
                    
                    # If we still don't have much content, get all text
                    if len(main_content) < 500:
                        main_content = soup.get_text(separator="\n", strip=True)
                    
                    # Clean up the content
                    main_content = re.sub(r'\n+', '\n', main_content)  # Remove multiple newlines
                    main_content = re.sub(r'\s+', ' ', main_content)   # Remove multiple spaces
                    
                    # Check if we actually got content
                    if len(main_content) > 200:  # Reasonable minimum length for actual content
                        print(f"Successfully scraped {url} (content length: {len(main_content)} chars)")
                        return {
                            "title": title,
                            "url": url,
                            "content": main_content[:10000]  # Limit content length
                        }
                    else:
                        print(f"Got response but content too short ({len(main_content)} chars), trying next user agent")
                        last_error = "Content too short"
                        continue
                
                elif response.status_code == 403 or response.status_code == 429:
                    # Access forbidden or rate limited, try another user agent
                    print(f"Access denied (HTTP {response.status_code}), trying next user agent")
                    last_error = f"HTTP {response.status_code}"
                    continue
                
                else:
                    # Other HTTP error
                    print(f"HTTP error: {response.status_code}")
                    last_error = f"HTTP {response.status_code}"
                    continue
                    
            except Exception as e:
                print(f"Error on attempt {i+1}: {str(e)}")
                last_error = str(e)
                continue
        
        # If we get here, all attempts failed
        print(f"All scraping attempts failed for {url}")
        return {
            "title": title,
            "url": url,
            "content": f"Failed to scrape content after {len(user_agents)} attempts. Last error: {last_error}"
        }
    
    def _log_scraped_content(self, query, scraped_result, timestamp):
        """Log the scraped content to a file."""
        try:
            safe_query = self._create_safe_filename(query)
            if len(safe_query) > 50:
                safe_query = safe_query[:50]
            
            scrape_file = self._scrape_dir / f"scrape_{safe_query}.txt"
            
            with open(scrape_file, "w", encoding="utf-8") as f:
                f.write(f"=== SCRAPED CONTENT FOR QUERY: '{query}' ===\n\n")
                f.write(f"Timestamp: {timestamp}\n\n")
                f.write(f"=== SOURCE: {scraped_result['title']} ===\n")
                f.write(f"URL: {scraped_result['url']}\n\n")
                f.write("CONTENT:\n")
                f.write("-" * 80 + "\n")
                f.write(scraped_result['content'])
                f.write("\n" + "-" * 80 + "\n\n")
            
            print(f"Scraped content logged to: {scrape_file}")
            return scrape_file
        except Exception as e:
            print(f"Error writing scraped content file: {e}")
            return None

    def _run(self, query: str, num_results: int = 5) -> str:
        """Run the Serper tool to search for AI/ML related information."""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        try:
            # Ensure num_results is within valid range
            num_results = max(1, min(10, num_results))
            
            # Get API key from environment
            api_key = os.getenv("SERPER_API_KEY")
            if not api_key:
                error_msg = "Serper API key not found in environment variables."
                self._log_interaction(query, error_msg, timestamp)
                return error_msg
            
            # Prepare the request
            url = "https://google.serper.dev/search"
            headers = {
                'X-API-KEY': api_key,
                'Content-Type': 'application/json'
            }
            payload = {
                'q': f"{query} AI machine learning",
                'num': num_results
            }
            
            # Make the request
            response = requests.post(url, headers=headers, data=json.dumps(payload))
            
            # Track credit usage
            credits_used = None
            credits_remaining = None
            
            # Check for credit usage in headers
            if 'X-Credits-Used' in response.headers:
                credits_used = response.headers['X-Credits-Used']
                print(f"CREDITS: Used {credits_used} credits for query: '{query}'")
            
            if 'X-Credits-Remaining' in response.headers:
                credits_remaining = response.headers['X-Credits-Remaining']
                print(f"CREDITS: Remaining balance: {credits_remaining} credits")
            
            # If we didn't find the standard headers, look for any credit-related headers
            if not credits_used and not credits_remaining:
                credit_headers = {k: v for k, v in response.headers.items() if 'credit' in k.lower()}
                if credit_headers:
                    print(f"CREDITS: Credit-related headers found: {credit_headers}")
                else:
                    print("CREDITS: No credit information found in response headers")
            
            if response.status_code == 200:
                data = response.json()
                
                # Debug: Print the raw response structure
                print(f"DEBUG: Raw response keys: {data.keys()}")
                
                # Debug: Check if knowledgeGraph exists
                if 'knowledgeGraph' in data:
                    print(f"DEBUG: Knowledge Graph found with title: {data['knowledgeGraph'].get('title', 'No Title')}")
                else:
                    print("DEBUG: No Knowledge Graph in this response")
                
                # Format the results
                formatted_response = f"# Search Results for: '{query}'\n\n"
                
                # Add credit usage information to the response
                if credits_used or credits_remaining:
                    formatted_response += f"*API Credits: Used {credits_used or 'unknown'}, Remaining {credits_remaining or 'unknown'}*\n\n"
                
                # Add organic results
                if 'organic' in data and data['organic']:
                    formatted_response += "## Top Results\n\n"
                    
                    # Create a directory for this query's scraped content
                    query_timestamp = f"{self._create_safe_filename(query)}"
                    query_scrape_dir = self._scrape_dir / query_timestamp
                    query_scrape_dir.mkdir(exist_ok=True)
                    
                    # Scrape all results
                    scraped_files = []
                    scraped_contents = []  # Store scraped content for inclusion in response
                    
                    for i, result in enumerate(data['organic'][:num_results], 1):
                        title = result.get('title', 'No Title')
                        link = result.get('link', 'No Link')
                        snippet = result.get('snippet', 'No Snippet')
                        
                        # Add to formatted response
                        formatted_response += f"### {i}. {title}\n"
                        formatted_response += f"**Link**: {link}\n"
                        formatted_response += f"**Snippet**: {snippet}\n\n"
                        
                        # Scrape the content
                        print(f"Scraping content from result {i}: {link}")
                        scraped_content = self._scrape_url(link, title)
                        scraped_contents.append(scraped_content)
                        
                        # Save to individual file
                        safe_title = self._create_safe_filename(title)
                        if len(safe_title) > 30:
                            safe_title = safe_title[:30]
                        
                        scrape_file = query_scrape_dir / f"{i}_{safe_title}.txt"
                        
                        with open(scrape_file, "w", encoding="utf-8") as f:
                            f.write(f"=== SCRAPED CONTENT FROM: {title} ===\n\n")
                            f.write(f"URL: {link}\n\n")
                            f.write("CONTENT:\n")
                            f.write("-" * 80 + "\n")
                            f.write(scraped_content['content'])
                            f.write("\n" + "-" * 80 + "\n\n")
                        
                        scraped_files.append(scrape_file)
                        
                        # Add a delay to avoid overloading servers
                        if i < num_results:  # Don't delay after the last request
                            time.sleep(1)
                    
                    # Create an index file with all scraped content
                    index_file = self._scrape_dir / f"all_scrapes_{query_timestamp}.txt"
                    
                    with open(index_file, "w", encoding="utf-8") as f:
                        f.write(f"=== ALL SCRAPED CONTENT FOR QUERY: '{query}' ===\n\n")
                        f.write(f"Timestamp: {timestamp}\n\n")
                        f.write(f"Number of results scraped: {len(scraped_files)}\n\n")
                        
                        for i, result in enumerate(data['organic'][:num_results], 1):
                            title = result.get('title', 'No Title')
                            link = result.get('link', 'No Link')
                            
                            f.write(f"=== RESULT {i}: {title} ===\n")
                            f.write(f"URL: {link}\n\n")
                            
                            # Find the corresponding scraped content
                            if i-1 < len(scraped_contents):
                                content = scraped_contents[i-1]['content']
                            else:
                                content = "Content not available"
                            
                            f.write("CONTENT:\n")
                            f.write("-" * 80 + "\n")
                            f.write(content)
                            f.write("\n" + "-" * 80 + "\n\n")
                    
                    # Add note about scraped content files
                    formatted_response += f"*Detailed content from all results has been scraped and saved to: {index_file}*\n\n"
                    
                    # Add summarized scraped content to the response
                    formatted_response += "## Extracted Content from Top Results\n\n"
                    
                    for i, scraped in enumerate(scraped_contents, 1):
                        title = scraped['title']
                        url = scraped['url']
                        content = scraped['content']
                        
                        # Calculate content length for summary
                        content_length = len(content)
                        
                        # Create a summary of the content
                        if content_length > 1500:
                            # For long content, include beginning and end with a note about truncation
                            summary = content[:750] + "\n\n[...content truncated...]\n\n" + content[-750:]
                        else:
                            # For shorter content, include it all
                            summary = content
                        
                        # Add to formatted response
                        formatted_response += f"### Content from Result {i}: {title}\n"
                        formatted_response += f"**Source**: {url}\n"
                        formatted_response += f"**Content Length**: {content_length} characters\n\n"
                        formatted_response += f"```\n{summary}\n```\n\n"
                        formatted_response += "-" * 40 + "\n\n"
                
                # Add knowledge graph if available
                if 'knowledgeGraph' in data:
                    kg = data['knowledgeGraph']
                    formatted_response += "## Knowledge Graph\n\n"
                    formatted_response += f"**Title**: {kg.get('title', 'No Title')}\n"
                    formatted_response += f"**Type**: {kg.get('type', 'No Type')}\n"
                    if 'description' in kg:
                        formatted_response += f"**Description**: {kg['description']}\n"
                    formatted_response += "\n"
                
                # Add related searches if available
                if 'relatedSearches' in data and data['relatedSearches']:
                    formatted_response += "## Related Searches\n\n"
                    for search in data['relatedSearches'][:5]:
                        formatted_response += f"- {search.get('query', '')}\n"
                
                # Log the interaction
                self._log_interaction(query, formatted_response, timestamp)
                
                return formatted_response
            else:
                error_msg = f"Error: {response.status_code} - {response.text}"
                self._log_interaction(query, error_msg, timestamp)
                return error_msg
                
        except Exception as e:
            error_msg = f"Error using Serper API: {str(e)}"
            self._log_interaction(query, error_msg, timestamp)
            return error_msg 