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
import urllib.parse

load_dotenv()

class WebScraperToolInput(BaseModel):
    """Input schema for WebScraperTool."""
    url: str = Field(..., description="The URL of the website to scrape.")
    depth: int = Field(1, description="How deep to scrape (1 = just this page, 2 = also follow links on this page).")

class WebScraperTool(BaseTool):
    name: str = "Web Scraper"
    description: str = """
    Use this tool to perform a thorough scrape of a specific website URL.
    This tool is perfect for extracting detailed information from documentation pages, tutorials, 
    or other technical resources that you've identified as particularly valuable.
    Input should be a URL that you want to analyze in depth.
    You can optionally specify a depth parameter to control how many levels of links to follow.
    """
    args_schema: Type[BaseModel] = WebScraperToolInput
    
    # Use PrivateAttr for attributes that shouldn't be part of the model schema
    _log_dir: Path = PrivateAttr(default=None)

    def __init__(self, **data):
        """Initialize the tool with logging directory setup."""
        super().__init__(**data)
        
        # Get the project root directory
        project_root = os.getenv("PROJECT_ROOT")
        
        if project_root:
            # Normalize the path (remove trailing slashes)
            project_root = project_root.rstrip('/')
            project_root = Path(project_root)
            print(f"Using normalized PROJECT_ROOT from environment: {project_root}")
        else:
            current_file = Path(__file__).resolve()
            project_root = current_file.parent.parent.parent.parent
            print(f"No PROJECT_ROOT found, using derived path: {project_root}")
        
        # Check if the project root exists
        if not project_root.exists():
            print(f"WARNING: Project root path does not exist: {project_root}")
        
        # Create logs directory structure
        self._log_dir = project_root / "logs" / "tool_logs" / "web_scraper"
        print(f"Attempting to create log directory at: {self._log_dir}")
        
        try:
            self._log_dir.mkdir(parents=True, exist_ok=True)
            print(f"Web Scraper tool log directory created/verified: {self._log_dir}")
        except Exception as e:
            print(f"Error creating Web Scraper log directory: {e}")
            fallback_dir = Path.home() / "job_skills_logs" / "web_scraper"
            print(f"Falling back to home directory: {fallback_dir}")
            self._log_dir = fallback_dir
            self._log_dir.mkdir(parents=True, exist_ok=True)
    
    def _create_safe_filename(self, url):
        """Convert a URL into a safe filename."""
        # Extract domain and path
        parsed_url = urllib.parse.urlparse(url)
        domain = parsed_url.netloc
        path = parsed_url.path
        
        # Create a safe filename
        safe_name = f"{domain}{path}".replace('/', '_').replace('.', '_')
        safe_name = ''.join(c for c in safe_name if c.isalnum() or c == '_' or c == '-')
        
        if not safe_name:
            safe_name = "unknown_url"
        
        # Limit length
        if len(safe_name) > 100:
            safe_name = safe_name[:100]
            
        return safe_name.lower()
    
    def _log_scrape(self, url, content, timestamp):
        """Log the scraped content to a file."""
        try:
            safe_url = self._create_safe_filename(url)
            
            log_file = self._log_dir / f"scrape_{safe_url}.txt"
            print(f"Attempting to write log to: {log_file}")
            
            # Ensure parent directory exists
            log_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(log_file, "w", encoding="utf-8") as f:
                f.write("=== WEB SCRAPER TOOL RESULT ===\n\n")
                f.write(f"Timestamp: {timestamp}\n\n")
                f.write(f"URL: {url}\n\n")
                f.write("=== CONTENT ===\n\n")
                f.write(content)
            
            print(f"Web scrape successfully logged to: {log_file}")
            return log_file
        except Exception as e:
            print(f"Error writing Web Scraper log file: {str(e)}")
            print(f"Log directory exists: {self._log_dir.exists()}")
            print(f"Log directory is writable: {os.access(str(self._log_dir), os.W_OK)}")
            return None
    
    def _get_user_agents(self):
        """Return a list of user agents to try."""
        return [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Safari/605.1.15',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0'
        ]
    
    def _scrape_url(self, url, visited_urls=None, current_depth=1, max_depth=1):
        """
        Scrape content from a URL with multiple user agent options and retries.
        
        Args:
            url: The URL to scrape
            visited_urls: Set of already visited URLs to avoid loops
            current_depth: Current depth level
            max_depth: Maximum depth to scrape
            
        Returns:
            dict: Scraped content and metadata
        """
        if visited_urls is None:
            visited_urls = set()
            
        # Skip if already visited
        if url in visited_urls:
            return None
            
        # Add to visited
        visited_urls.add(url)
        
        # List of different user agents to try
        user_agents = self._get_user_agents()
        
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
                    
                    # Get the page title
                    title = soup.title.string if soup.title else "No Title"
                    
                    # Remove script and style elements
                    for script in soup(["script", "style"]):
                        script.extract()
                    
                    # Get the main content
                    main_content = ""
                    
                    # Try to find the main article content
                    article = (
                        soup.find('article') or 
                        soup.find('main') or
                        soup.find(attrs={"role": "main"}) or 
                        soup.find(class_=re.compile("content|article|post|main|documentation|tutorial|guide"))
                    )
                    
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
                    
                    # Extract code blocks
                    code_blocks = []
                    for code in soup.find_all(['pre', 'code']):
                        code_text = code.get_text(strip=True)
                        if len(code_text) > 20:  # Only include substantial code blocks
                            code_blocks.append(code_text)
                    
                    # Extract links for deeper scraping
                    links = []
                    if current_depth < max_depth:
                        for link in soup.find_all('a', href=True):
                            href = link['href']
                            
                            # Skip anchors, javascript, etc.
                            if href.startswith('#') or href.startswith('javascript:') or href.startswith('mailto:'):
                                continue
                                
                            # Handle relative URLs
                            if not href.startswith('http'):
                                parsed_url = urllib.parse.urlparse(url)
                                base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
                                
                                if href.startswith('/'):
                                    href = f"{base_url}{href}"
                                else:
                                    path_parts = parsed_url.path.split('/')
                                    if len(path_parts) > 1:
                                        path_parts.pop()  # Remove the last part (file)
                                    base_path = '/'.join(path_parts)
                                    href = f"{base_url}{base_path}/{href}"
                            
                            # Only include links from the same domain
                            if urllib.parse.urlparse(href).netloc == urllib.parse.urlparse(url).netloc:
                                links.append(href)
                    
                    # Check if we actually got content
                    if len(main_content) > 200:  # Reasonable minimum length for actual content
                        print(f"Successfully scraped {url} (content length: {len(main_content)} chars)")
                        
                        result = {
                            "url": url,
                            "title": title,
                            "content": main_content,
                            "code_blocks": code_blocks,
                            "links": links[:5]  # Limit to 5 links to avoid excessive scraping
                        }
                        
                        # Recursively scrape linked pages if needed
                        if current_depth < max_depth and links:
                            result["sub_pages"] = []
                            
                            for link in links[:5]:  # Limit to 5 links
                                print(f"Following link: {link} (depth {current_depth+1}/{max_depth})")
                                sub_result = self._scrape_url(
                                    link, 
                                    visited_urls, 
                                    current_depth + 1, 
                                    max_depth
                                )
                                
                                if sub_result:
                                    result["sub_pages"].append(sub_result)
                                
                                # Add a delay between requests
                                time.sleep(2)
                        
                        return result
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
            "url": url,
            "title": "Failed to scrape",
            "content": f"Failed to scrape content after {len(user_agents)} attempts. Last error: {last_error}",
            "code_blocks": [],
            "links": []
        }
    
    def _format_scraped_content(self, result, indent=0):
        """Format the scraped content into a readable string."""
        indent_str = "  " * indent
        output = []
        
        # Add the title and URL
        output.append(f"{indent_str}# {result['title']}")
        output.append(f"{indent_str}URL: {result['url']}")
        output.append("")
        
        # Add the main content
        output.append(f"{indent_str}## Main Content")
        output.append("")
        
        # Split content into paragraphs for better readability
        paragraphs = result['content'].split('\n')
        for paragraph in paragraphs:
            if paragraph.strip():
                output.append(f"{indent_str}{paragraph}")
                output.append("")
        
        # Add code blocks if any
        if result['code_blocks']:
            output.append(f"{indent_str}## Code Examples")
            output.append("")
            
            for i, code in enumerate(result['code_blocks'], 1):
                output.append(f"{indent_str}### Code Example {i}")
                output.append(f"{indent_str}```")
                output.append(code)
                output.append(f"{indent_str}```")
                output.append("")
        
        # Add sub-pages if any
        if 'sub_pages' in result and result['sub_pages']:
            output.append(f"{indent_str}## Related Pages")
            output.append("")
            
            for sub_page in result['sub_pages']:
                sub_content = self._format_scraped_content(sub_page, indent + 1)
                output.append(sub_content)
        
        return "\n".join(output)

    def _run(self, url: str, depth: int = 1) -> str:
        """Run the Web Scraper tool to thoroughly scrape a website."""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        try:
            # Validate URL
            if not url.startswith('http'):
                error_msg = f"Invalid URL: {url}. URL must start with http:// or https://"
                return error_msg
            
            # Limit depth to reasonable values
            depth = max(1, min(3, depth))  # Between 1 and 3
            
            print(f"Starting deep scrape of {url} with depth {depth}")
            
            # Perform the scrape
            result = self._scrape_url(url, max_depth=depth)
            
            if not result:
                error_msg = f"Failed to scrape {url}"
                return error_msg
            
            # Format the results
            formatted_content = self._format_scraped_content(result)
            
            # Log the results
            log_file = self._log_scrape(url, formatted_content, timestamp)
            
            # Create a summary for the response
            summary = f"# Web Scraper Results for {url}\n\n"
            
            # Add the title
            summary += f"## {result['title']}\n\n"
            
            # Add content length info
            content_length = len(result['content'])
            summary += f"Content Length: {content_length} characters\n\n"
            
            # Add code blocks info
            summary += f"Code Examples: {len(result['code_blocks'])}\n\n"
            
            # Add sub-pages info if any
            if 'sub_pages' in result and result['sub_pages']:
                summary += f"Related Pages Scraped: {len(result['sub_pages'])}\n\n"
            
            # Add a preview of the content
            summary += "## Content Preview\n\n"
            
            # Get the first 1000 characters as a preview
            preview = result['content'][:1000]
            if len(result['content']) > 1000:
                preview += "...(content truncated)..."
            
            summary += preview + "\n\n"
            
            # Add code examples preview
            if result['code_blocks']:
                summary += "## Code Examples Preview\n\n"
                
                for i, code in enumerate(result['code_blocks'][:2], 1):  # Show first 2 code blocks
                    code_preview = code[:500]
                    if len(code) > 500:
                        code_preview += "...(code truncated)..."
                    
                    summary += f"### Code Example {i}\n"
                    summary += "```\n"
                    summary += code_preview + "\n"
                    summary += "```\n\n"
                
                if len(result['code_blocks']) > 2:
                    summary += f"*{len(result['code_blocks']) - 2} more code examples available in the full content*\n\n"
            
            # Add full content
            summary += "## Full Content\n\n"
            summary += formatted_content
            
            # Add log file info
            if log_file:
                summary += f"\n\nDetailed scrape results saved to: {log_file}\n"
            
            return summary
            
        except Exception as e:
            error_msg = f"Error using Web Scraper: {str(e)}"
            return error_msg 