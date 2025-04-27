import os
import logging
import argparse
import json
import time
import requests
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from linkup import LinkupClient

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class LinkUpSearchInput(BaseModel):
    """Input schema for LinkUp Search."""
    query: str = Field(description="The search query to perform")
    depth: str = Field(default="standard", description="Depth of search: 'standard' or 'deep'")
    output_type: str = Field(default="sourcedAnswer", description="Output type: 'searchResults', 'sourcedAnswer', or 'structured'")
    include_images: bool = Field(default=False, description="Whether to include images in the search results")

class BlogGenerator:
    """Main class for blog generation."""
    
    def __init__(self):
        """Initialize the blog generator with necessary resources."""
        self.api_key = os.getenv("LINKUP_API_KEY")
        if not self.api_key:
            raise ValueError("LINKUP_API_KEY environment variable is not set")
            
        # Cache available models at startup to avoid repeated API calls
        self.base_url = os.getenv("LLM_BASE_URL", "http://localhost:11434")
        self.model = os.getenv("LLM_MODEL", "llama3:latest")
        self.available_models = self._get_available_models()
        
        # Choose best available model once at initialization
        if self.model not in self.available_models and self.available_models:
            for fallback in ["llama3", "llama2", "mistral", "gemma"]:
                if fallback in self.available_models:
                    self.model = fallback
                    logger.info(f"Using fallback model: {self.model}")
                    break
        
        # Load minimal style guidelines
        self.style_guide = "- Casual, friendly tone\n- Use first-person perspective\n- Include practical advice\n- Be conversational\n- No pretentious language"
        
        logger.info(f"BlogGenerator initialized with model {self.model}")
    
    def _get_available_models(self) -> List[str]:
        """Get available models once at initialization."""
        try:
            headers = {"Content-Type": "application/json"}
            models_response = requests.get(
                f"{self.base_url}/api/tags",
                headers=headers,
                timeout=10
            )
            if models_response.status_code == 200:
                available_models = models_response.json().get("models", [])
                model_names = [model.get('name') for model in available_models if 'name' in model]
                logger.info(f"Available models: {model_names}")
                return model_names
        except Exception as e:
            logger.warning(f"Could not check available models: {str(e)}")
        return []
            
    def get_research(self, query: str) -> Dict[str, Any]:
        """Get research results from LinkUp API with focused parameters."""
        logger.info(f"Researching: {query}")
        try:
            client = LinkupClient(api_key=self.api_key)
            search_response = client.search(
                query=query,
                depth="standard",
                output_type="sourcedAnswer",
                include_images=False
            )
            logger.info("Research complete")
            
            # Process the results to extract only what's needed - maximum brevity
            if isinstance(search_response, str):
                try:
                    data = json.loads(search_response)
                except:
                    return {"summary": search_response[:200]}
            else:
                data = search_response
                
            # Extract minimal information - just 2-3 key points
            processed_results = {"summary": ""}
            
            if isinstance(data, dict):
                if 'answer' in data:
                    # Extract just first 2 sentences or 200 chars max
                    answer = data['answer']
                    sentences = answer.split('. ')
                    short_answer = '. '.join(sentences[:2])
                    if len(short_answer) > 200:
                        short_answer = short_answer[:197] + "..."
                    processed_results['summary'] = short_answer
            
            return processed_results
        except Exception as e:
            logger.error(f"Research error: {str(e)}")
            return {"summary": f"Key trends in {query}"}
            
    def generate_blog(self, query: str, research_results: Dict[str, Any]) -> str:
        """Generate blog content using the LLM with proper prompting."""
        logger.info("Generating blog content")
        
        # Create an extremely concise prompt
        summary = research_results.get('summary', '')
        prompt = f"""Write a short blog post (600 words max) about {query}. 
Style: casual, first-person, practical advice.
Key point: {summary}
End with: "Keep being awesome at what you do!"
Format: title, intro, 2-3 sections, conclusion."""

        try:
            # Use streaming to avoid timeouts
            headers = {"Content-Type": "application/json"}
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": True,  # Use streaming to avoid timeout
                "temperature": 0.7,
                "num_predict": 500,  # Reduced for faster generation
                "stop": ["# END"]
            }
            
            logger.info(f"Sending streaming request to LLM API using model: {self.model}")
            start_time = time.time()
            
            # Stream the response to avoid timeout
            response = requests.post(
                f"{self.base_url}/api/generate",
                headers=headers,
                json=payload,
                stream=True,
                timeout=30  # Initial connection timeout
            )
            
            if response.status_code != 200:
                logger.error(f"LLM API error: {response.status_code}")
                return self._generate_fallback_content(query)
            
            # Collect the streamed response
            content = ""
            try:
                for line in response.iter_lines():
                    if line:
                        try:
                            # Process each line of the stream
                            line_data = json.loads(line)
                            if 'response' in line_data:
                                content += line_data['response']
                        except json.JSONDecodeError:
                            pass
            except requests.exceptions.ChunkedEncodingError:
                logger.warning("Streaming connection broken")
            except requests.exceptions.Timeout:
                logger.warning("Streaming connection timed out")
            
            generation_time = time.time() - start_time
            logger.info(f"Generation completed in {generation_time:.2f} seconds")
            
            # Add signature if missing
            if "Keep being awesome at what you do" not in content:
                content += "\n\nKeep being awesome at what you do!"
            
            # If we got at least some content, return it
            if len(content) > 50:
                logger.info(f"Blog generation complete - Length: {len(content)} characters")
                return content
            else:
                # If very little content was generated, use fallback
                return self._generate_fallback_content(query)
            
        except Exception as e:
            logger.error(f"Blog generation error: {str(e)}")
            return self._generate_fallback_content(query)
    
    def _generate_fallback_content(self, query: str) -> str:
        """Generate a simple fallback blog post without using the LLM."""
        return f"""
# {query}: Essential Guide for 2025

Hey there! Today we're looking at {query} - an important topic for professionals in 2025.

## Key Points
- Focus on what matters most
- Use the right tools for your specific needs
- Remember that fundamentals remain important even as technologies change
- Start small and build momentum
- Learn from others but develop your own approach

The landscape is always changing, but don't let that intimidate you. The most successful people aren't necessarily the ones with the most advanced tools or techniques - they're the ones who consistently apply what they know and keep learning.

I've found that setting aside just 15 minutes a day to work on mastering {query} leads to significant improvements over time. It's not about massive overhauls, but rather small, consistent actions.

Keep being awesome at what you do!
"""
    
    def create_blog_post(self, query: str) -> str:
        """Complete end-to-end process to create a blog post."""
        logger.info(f"Creating blog post for: {query}")
        
        try:
            # Get research results
            research_results = self.get_research(query)
            
            # Generate the blog post
            blog_content = self.generate_blog(query, research_results)
            
            return blog_content
            
        except Exception as e:
            logger.error(f"Blog post creation error: {str(e)}")
            return self._generate_fallback_content(query)


def check_ollama_status() -> tuple[bool, List[str]]:
    """Check if Ollama is running and which models are available."""
    try:
        headers = {"Content-Type": "application/json"}
        response = requests.get(
            "http://localhost:11434/api/tags",
            headers=headers,
            timeout=10
        )
        if response.status_code == 200:
            models = response.json().get("models", [])
            model_names = [model.get('name') for model in models if 'name' in model]
            logger.info(f"Ollama is running with models: {model_names}")
            return True, model_names
        else:
            logger.error(f"Ollama returned status code {response.status_code}")
            return False, []
    except Exception as e:
        logger.error(f"Error checking Ollama status: {str(e)}")
        return False, []


def main():
    """Main function to run the blog generation process."""
    parser = argparse.ArgumentParser(description='Generate a Substack-ready blog post')
    parser.add_argument('query', help='The topic to write about')
    parser.add_argument('--output', '-o', help='Output file path (optional)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging')
    parser.add_argument('--model', '-m', help='Specify the LLM model to use')
    parser.add_argument('--timeout', '-t', type=int, default=90, 
                       help='Timeout in seconds for LLM generation (default: 90)')
    
    args = parser.parse_args()
    
    # Set logging level based on verbosity
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Check Ollama status
    ollama_running, available_models = check_ollama_status()
    if not ollama_running:
        print("Error: Ollama is not running. Please start Ollama before running this script.")
        return
    
    # Set model from argument if provided
    if args.model:
        if args.model in available_models:
            os.environ["LLM_MODEL"] = args.model
            print(f"Using specified model: {args.model}")
        else:
            print(f"Warning: Model {args.model} is not available. Available models: {available_models}")
            if available_models:
                os.environ["LLM_MODEL"] = available_models[0]
                print(f"Using fallback model: {available_models[0]}")
    elif available_models:
        # Set first available model as default if not specified
        os.environ["LLM_MODEL"] = available_models[0]
        print(f"Using default model: {available_models[0]}")
    
    try:
        print(f"Generating blog post for: {args.query}")
        print("This may take a minute or two depending on your hardware...")
        
        # Initialize the blog generator
        generator = BlogGenerator()
        
        # Generate the blog post with progress indicators
        start_time = time.time()
        blog_content = generator.create_blog_post(args.query)
        elapsed_time = time.time() - start_time
        
        # Output the blog content
        if args.output:
            with open(args.output, 'w') as f:
                f.write(blog_content)
            print(f"Blog post written to {args.output}")
        else:
            print("\n--- BLOG POST ---\n")
            print(blog_content)
            print("\n--- END OF BLOG POST ---\n")
            
        print(f"Generation completed in {elapsed_time:.2f} seconds")
            
    except Exception as e:
        logging.error(f"Error in main function: {str(e)}")
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()