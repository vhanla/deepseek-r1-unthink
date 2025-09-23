# deepseek-r1-unthink

  Ollama's API proxy server that captures `/api/chat` and `/api/generate` responses and 
    removes <think></think> streamed content, so we get rid of 
    the "&lt;THINK&gt;-ing process" specially on DeepSeek-R1's generated content.
| e.g. |
|:--:|
| ![imagen](https://github.com/user-attachments/assets/bf18ba19-a63f-40ba-aa07-0f8aa8a87009) |
|    Zed's settings.json demo in action, notice it doesn't show the &lt;think&gt;&lt;/think&gt; content anymore. |


# Ollama Proxy Server
A Flask-based proxy server for Ollama that provides enhanced streaming capabilities and thinking tag handling. This proxy sits between your client application and the Ollama server, filtering and processing the response stream.

## Features

- Proxies requests to Ollama server
- Handles streaming responses efficiently
- Processes special thinking tags (<think> and </think>) to filter internal processing
- Maintains CORS support for cross-origin requests
- Supports both chat and generate endpoints
- Cleans up response formatting and removes excessive newlines

## Prerequisites

- Python 3.7+
- Ollama server running locally or remotely
- pip (Python package manager)

## Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/ollama-proxy.git
cd ollama-proxy
``` 
3. Install required dependencies:
```bash
pip install flask flask-cors requests
```
## Configuration

The proxy server uses two main configuration variables at the top of the script:

```python
OLLAMA_SERVER = "http://localhost:11434"  # Your Ollama server address
PROXY_PORT = 11435                        # Port for this proxy server
```
Modify these values in the code to match your setup if needed.
## Usage

1. Start the proxy server:
```python
python app.py
```
2. The server will start on port 11435 (default) and forward requests to your Ollama server
3. Use the proxy in your applications by pointing them to:
```
http://localhost:11435
```
## API Endpoints

The proxy server supports the following Ollama endpoints:

- /api/generate - For text generation
- /api/chat - For chat interactions

All other Ollama endpoints are proxied as-is.

## Thinking Tag Processing

The proxy server handles special thinking tags in the response stream:

- Content between <think> and </think> tags is filtered out
- Content before <think> and after </think> is preserved
- Handles cases where tags may appear in any order or be unpaired

**Example:**

```
Input stream: "Hello <think>processing request</think> World!"
Output stream: "Hello World!"
```

## CORS Support
The server includes CORS support with the following configuration:

- Allows all origins (*)
- Supports GET, POST, and OPTIONS methods
- Allows all headers

## Error Handling

Invalid JSON responses are forwarded as-is
Non-content messages (like 'done' signals) are preserved
Missing or malformed thinking tags are handled gracefully
HTTP errors from Ollama are properly proxied

## Development
The server includes debug mode by default when running directly. To modify this behavior, change the `debug` parameter in:

```python
app.run(port=PROXY_PORT, debug=True)
```
## License
MIT Licence

## Contributing

1. Fork the repository
2. Create your feature branch (git checkout -b feature/amazing-feature)
3. Commit your changes (git commit -m 'Add some amazing feature')
4. Push to the branch (git push origin feature/amazing-feature)
5. Open a Pull Request

## Support
For issues, questions, or contributions, please:

1. Check existing GitHub issues
2. Create a new issue if needed
3. Provide as much context as possible

## Acknowledgments

- Ollama team for the base server
- Contributors to Flask and related packages

2025-09-19
Updated and tested with aider and qwen3
