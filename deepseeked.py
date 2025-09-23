from flask import Flask, request, Response
from flask_cors import CORS
import requests
import json

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*", "methods": ["GET", "POST", "OPTIONS"], "allow_headers": "*"}})

# Configuration
OLLAMA_SERVER = "http://localhost:11434" # Default OLLAMA_HOST 11434
PROXY_PORT = 11435 # forwarded new ENDPOINT

def process_thinking_content(message_content, thinking_started):
    """Process content based on thinking tags state"""
    if not message_content:
        return "", thinking_started

    # Handle opening tag
    if '<think>' in message_content:
        thinking_started = True
        # If there's content before <think>, keep it
        content_before = message_content.split('<think>')[0]
        return content_before, thinking_started

    # Handle closing tag
    if '</think>' in message_content:
        thinking_started = False
        # If there's content after </think>, keep it
        content_after = message_content.split('</think>')[-1]
        return content_after, thinking_started

    # If we're in thinking mode, return empty
    if thinking_started:
        return "", thinking_started

    return message_content, thinking_started

def is_empty_content(message_content):
    """Check if the content is empty. Preserves whitespace-only messages."""
    return not message_content

def generate_streaming_response(response):
    """Processes and yields chunks from a streaming Ollama response."""
    thinking_started = False
    for chunk in response.iter_lines():
        if chunk:
            try:
                # Parse the JSON response
                data = json.loads(chunk.decode('utf-8'))

                # Check if this is a message with content
                if 'message' in data and 'content' in data['message']:
                    content = data['message']['content']

                    # Process thinking tags and get cleaned content
                    cleaned_content, thinking_started = process_thinking_content(
                        content, thinking_started
                    )

                    # Update the content in the data. We send the message even
                    # if the content is now empty to keep the stream valid.
                    data['message']['content'] = cleaned_content

                    # Convert back to JSON and send
                    yield json.dumps(data).encode('utf-8') + b'\n'
                else:
                    # Forward non-content messages (like 'done' messages)
                    yield chunk + b'\n'

            except json.JSONDecodeError:
                # If we can't parse the JSON, forward it anyway
                yield chunk + b'\n'

@app.route('/api/<path:path>', methods=['POST'])
def proxy_api(path):
    allowed_paths = ['generate', 'chat', 'show']
    if path not in allowed_paths:
        return Response('Not Found', status=404)

    is_streaming_endpoint = path in ['generate', 'chat']

    payload = None
    if request.is_json:
        payload = request.json
    else:
        try:
            payload = json.loads(request.get_data())
        except json.JSONDecodeError:
            return Response("Failed to decode JSON from request body.", status=400)

    # Make the request to the Ollama server
    response = requests.post(
        f"{OLLAMA_SERVER}/api/{path}",
        json=payload,
        stream=is_streaming_endpoint
    )

    if is_streaming_endpoint:
        return Response(
            generate_streaming_response(response),
            mimetype='application/json',
            headers={
                'X-Accel-Buffering': 'no',
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
                'Content-Type': 'application/json'
            }
        )
    # Handle non-streaming endpoints (e.g., 'show')
    else:
        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        headers = [(name, value) for (name, value) in response.raw.headers.items()
                   if name.lower() not in excluded_headers]

        return Response(response.content, response.status_code, headers)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>', methods=['GET', 'OPTIONS'])
def catch_all(path):
    if request.method == 'OPTIONS':
        return Response('', 204)

    resp = requests.request(
        method=request.method,
        url=f"{OLLAMA_SERVER}/{path}",
        headers={key: value for key, value in request.headers if key != 'Host'},
        data=request.get_data(),
        cookies=request.cookies,
        allow_redirects=False
    )

    excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
    headers = [(name, value) for (name, value) in resp.raw.headers.items()
               if name.lower() not in excluded_headers]

    return Response(resp.content, resp.status_code, headers)

if __name__ == '__main__':
    print(f"Starting proxy server on port {PROXY_PORT}")
    print(f"Forwarding requests to {OLLAMA_SERVER}")
    app.run(port=PROXY_PORT, debug=True)
