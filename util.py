""" Utility function that returns the tools available to the agent  """

def get_tools():
    return [
        {
            "type": "function",
            "function": {
                "name": "search_web",
                "description": "Search the web for information",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "The query to search the web for"}
                    }
                },
                "required": ["query"]
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_url_raw_content",
                "description": "Get the cleaned text content of a webpage. This extracts the main content while removing ads, navigation, headers, footers, and other unwanted elements. Use this to read detailed information from specific URLs.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "url": {"type": "string", "description": "The URL of the webpage to extract content from"}
                    }
                },
                "required": ["url"]
            }
        }
    ]