import logging
from agents import LinkUpSearchTool

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def test_linkup_api(query: str):
    logging.debug(f"Testing LinkUp API with query: {query}")
    try:
        # Initialize the LinkUp Search Tool
        linkup_search_tool = LinkUpSearchTool()

        # Perform the search
        result = linkup_search_tool._run(query=query)
        logging.debug(f"Search result: {result}")
        print("Search result:", result)
    except Exception as e:
        logging.error(f"Error during LinkUp API test: {str(e)}")
        print(f"Error: {str(e)}")

# Test the LinkUp API with a sample query
test_query = "AI advancements in 2023"
test_linkup_api(test_query) 