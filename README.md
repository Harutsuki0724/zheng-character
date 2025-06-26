Multi-Character Roleplay API
This project provides a FastAPI application that simulates replies from multiple characters. Each character is defined by a YAML file under the characters/ directory. A client sends a message and a list of characters, and the API responds with each character's reply.

Installation
Create a Python environment and install dependencies from requirements.txt:

pip install -r requirements.txt
Running the Server
Start the FastAPI server with uvicorn:

uvicorn GPT_RP:app --reload --host 0.0.0.0 --port 8000
The API will be available at http://localhost:8000.

Example Usage
Send a POST request to /respond with a message and a list of character names. For example using curl:

curl -X POST http://localhost:8000/respond \
  -H 'Content-Type: application/json' \
  -d '{"message": "Hello everyone!", "characters": ["lazul", "chacha"]}'
The response will contain an array of replies, one for each character:

{
  "replies": [
    {"name": "lazul", "reply": "..."},
    {"name": "chacha", "reply": "..."}
  ]
}
