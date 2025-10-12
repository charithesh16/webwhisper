from openai import OpenAI
import os
import gradio as gr
import requests
from dotenv import load_dotenv
import website
import json
from util import get_tools
import tiktoken

load_dotenv()
openai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL = "gpt-5-mini-2025-08-07"
MAX_TOKENS = 120000  # Maximum tokens before summarization (leaving buffer for model's max context)
KEEP_RECENT_MESSAGES = 4  # Number of recent messages to keep when summarizing

system_message = """
You are a helpful AI assistant with access to real-time web search capabilities. You can:

1. Search the web using the search_web function to find current information, news, facts, and answers to questions
2. Extract and read cleaned content from specific URLs using the get_url_raw_content function to get detailed information from web pages (this removes ads, navigation, and other unwanted content)

When answering questions:
- Use web search when you need current information, recent events, or facts you're not certain about
- After searching, you can retrieve clean, focused content from promising URLs to get detailed information
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

""" returns the cleaned content of the url """
def get_url_raw_content(url: str):
    site = website.Website(url)
    return site.get_content()


def count_tokens(messages):
    """Count the number of tokens in messages"""
    try:
        encoding = tiktoken.encoding_for_model(MODEL)
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")
    
    num_tokens = 0
    for message in messages:
        # Convert Pydantic objects to dict if needed
        if hasattr(message, 'model_dump'):
            message = message.model_dump()
        elif hasattr(message, 'dict'):
            message = message.dict()
        
        # Count tokens in each message
        num_tokens += 4  # Every message follows <im_start>{role/name}\n{content}<im_end>\n
        for key, value in message.items():
            if isinstance(value, str):
                num_tokens += len(encoding.encode(value))
            elif key == "tool_calls" and value:
                # Handle tool calls
                num_tokens += len(encoding.encode(json.dumps(value)))
    num_tokens += 2  # Every reply is primed with <im_start>assistant
    return num_tokens


def summarize_conversation(messages):
    """Summarize older messages to reduce token count"""
    print("Summarizing conversation to reduce token count...")
    
    # Keep system message, summarize middle messages, keep recent messages
    system_msg = messages[0] if messages and messages[0]["role"] == "system" else None
    
    # Find where to split - keep the last KEEP_RECENT_MESSAGES messages
    if len(messages) <= KEEP_RECENT_MESSAGES + 1:  # +1 for system message
        return messages
    
    recent_messages = messages[-KEEP_RECENT_MESSAGES:]
    messages_to_summarize = messages[1:-KEEP_RECENT_MESSAGES] if system_msg else messages[:-KEEP_RECENT_MESSAGES]
    
    if not messages_to_summarize:
        return messages
    
    # Create a prompt to summarize the conversation
    summary_prompt = "Please provide a concise summary of the following conversation history, preserving key information, context, and important details:\n\n"
    for msg in messages_to_summarize:
        role = msg.get("role", "")
        content = msg.get("content", "")
        if content:
            summary_prompt += f"{role}: {content}\n\n"
    
    try:
        # Get summary from OpenAI
        summary_response = openai.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that summarizes conversations concisely while preserving important context and details."},
                {"role": "user", "content": summary_prompt}
            ]
        )
        
        summary = summary_response.choices[0].message.content
        
        # Build new messages list with summary
        new_messages = []
        if system_msg:
            new_messages.append(system_msg)
        
        # Add summary as a system message
        new_messages.append({
            "role": "system",
            "content": f"Previous conversation summary: {summary}"
        })
        
        # Add recent messages
        new_messages.extend(recent_messages)
        
        print(f"Conversation summarized. Token count reduced from {count_tokens(messages)} to {count_tokens(new_messages)}")
        return new_messages
    
    except Exception as e:
        print(f"Error during summarization: {e}")
        # If summarization fails, just keep system message and recent messages
        new_messages = []
        if system_msg:
            new_messages.append(system_msg)
        new_messages.extend(recent_messages)
        return new_messages


def chat(message, history):
    messages = [{"role": "system", "content": system_message}] + history + [{"role": "user", "content": message}]
    
    # Check token count and summarize if needed
    token_count = count_tokens(messages)
    print(f"Current token count: {token_count}")
    
    if token_count > MAX_TOKENS:
        print(f"Token limit exceeded ({token_count} > {MAX_TOKENS}). Summarizing conversation...")
        messages = summarize_conversation(messages)
    
    response = openai.chat.completions.create(model=MODEL, messages=messages, tools=get_tools())

    # process the tool calls until all the tool calls are processed
    while response.choices[0].message.tool_calls:
        # Add the assistant's response with tool calls to the messages (convert to dict)
        assistant_message = response.choices[0].message
        messages.append({
            "role": assistant_message.role,
            "content": assistant_message.content,
            "tool_calls": [
                {
                    "id": tc.id,
                    "type": tc.type,
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments
                    }
                } for tc in assistant_message.tool_calls
            ]
        })
        
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
        
        # Check token count after adding tool responses
        token_count = count_tokens(messages)
        if token_count > MAX_TOKENS:
            print(f"Token limit exceeded during tool execution ({token_count} > {MAX_TOKENS}). Summarizing...")
            messages = summarize_conversation(messages)
        
        # Get the next response from the model
        response = openai.chat.completions.create(model=MODEL, messages=messages,tools=get_tools())
    
    # Return the final response content
    return response.choices[0].message.content



gr.ChatInterface(fn=chat, type="messages").launch()

