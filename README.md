# WebWhisper 🌐🤖

An intelligent AI chatbot with real-time web search capabilities, powered by OpenAI's GPT and Brave Search API. WebWhisper can search the internet, extract content from web pages, and provide accurate, up-to-date answers with source citations.

## Features

- 🔍 **Real-time Web Search**: Leverages Brave Search API to find current information and recent events
- 📄 **URL Content Extraction**: Retrieves and parses content from web pages for detailed analysis
- 💬 **Interactive Chat Interface**: Built with Gradio for a seamless conversational experience
- 🔧 **Function Calling**: Uses OpenAI's function calling to intelligently decide when to search the web or extract URL content
- 📚 **Source Citation**: Provides references to sources used in answers

## Prerequisites

- Python 3.8 or higher
- OpenAI API key
- Brave Search API key

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/webwhisper.git
cd webwhisper
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install required dependencies:
```bash
pip install openai gradio requests beautifulsoup4 python-dotenv
```

4. Create a `.env` file in the project root with your API keys:
```env
OPENAI_API_KEY=your_openai_api_key_here
BRAVE_API_KEY=your_brave_api_key_here
```

## Getting API Keys

### OpenAI API Key
1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Sign up or log in to your account
3. Navigate to API keys section
4. Create a new API key

### Brave Search API Key
1. Visit [Brave Search API](https://brave.com/search/api/)
2. Sign up for an account
3. Subscribe to a plan (free tier available)
4. Get your API key from the dashboard

## Usage

Run the application:
```bash
python main.py
```

This will launch a Gradio interface in your browser where you can:
- Ask questions that require current information
- Request web searches on specific topics
- Get detailed content from specific URLs
- Have natural conversations with AI that can verify facts using the web

### Example Queries

- "What are the latest news about AI?"
- "Find information about the recent SpaceX launch"
- "What's the current weather in New York?"
- "Search for the best practices in Python async programming"

