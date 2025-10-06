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
                "description": "Get the raw content of a url, use this when you need to get the raw content of a url to answer the question",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "url": {"type": "string", "description": "The url to get the raw content of"}
                    }
                },
                "required": ["url"]
            }
        }
    ]