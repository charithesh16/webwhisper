from openai import OpenAI
import os
import gradio as gr
import requests
from dotenv import load_dotenv
import website
import json
from util import get_tools

load_dotenv()
openai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL = "gpt-5-mini-2025-08-07"
system_message = """
You are a helpful AI assistant with access to real-time web search capabilities. You can:

1. Search the web using the search_web function to find current information, news, facts, and answers to questions
2. Extract and read content from specific URLs using the get_url_raw_content function to get detailed information from web pages

When answering questions:
- Use web search when you need current information, recent events, or facts you're not certain about
- After searching, you can retrieve full content from promising URLs to get detailed information
- Synthesize information from multiple sources when appropriate
- Always provide clear, accurate, and well-sourced answers
- Cite your sources when referencing web content

Be proactive in using your tools to provide the most accurate and up-to-date information possible.
"""

''' calls brave search api to get the search results and returns the top 5 urls with title'''
def search_web(query: str):
    print("calling brave search api")
    api_key = os.getenv("BRAVE_API_KEY")
    if not api_key:
        return []
    if not query:
        return []

    try:
        response = requests.get(
            "https://api.search.brave.com/res/v1/web/search",
            params={
                "q": query,
                "count": 1,
            },
            headers={
                "X-Subscription-Token": api_key,
                "Accept": "application/json",
            },
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()

        results = data.get("web", {}).get("results", [])
        urls = [{"title": item.get("title"), "url":item.get("url")} for item in results if isinstance(item, dict) and item.get("url")]
        return urls[:5]
    except requests.RequestException:
        return []

""" returns the content of the url """
def get_url_raw_content(url: str):
    site = website.Website(url)
    return site.get_raw_content()


def chat(message, history):
    messages = [{"role": "system", "content": system_message}] + history + [{"role": "user", "content": message}]
    response = openai.chat.completions.create(model=MODEL, messages=messages, tools=get_tools())

    # process the tool calls until all the tool calls are processed
    while response.choices[0].message.tool_calls:
        # Add the assistant's response with tool calls to the messages
        messages.append(response.choices[0].message)
        
        # Execute each tool call and collect results
        for tool_call in response.choices[0].message.tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)
            
            # Call the appropriate function
            if function_name == "search_web":
                result = search_web(function_args.get("query", ""))
            elif function_name == "get_url_raw_content":
                result = get_url_raw_content(function_args.get("url", ""))
            else:
                result = {"error": "Unknown function"}
            
            # Add the tool response to messages
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(result)
            })
        
        # Get the next response from the model
        response = openai.chat.completions.create(model=MODEL, messages=messages,tools=get_tools())
    
    # Return the final response content
    return response.choices[0].message.content



gr.ChatInterface(fn=chat, type="messages").launch()

