from flask import Flask, request, jsonify
from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from flask_cors import CORS
import base64
from PIL import Image
from io import BytesIO
import uuid
import os
import ollama
app = Flask(__name__)
CORS(app)

# Initialize the Ollama model
model = OllamaLLM(model="llama3.2")

template = """
You are an assistant that extracts borrowing request details from a user's message.
Only reply with a JSON object in this format:

{
  "name": "...",
  "email": "...",
  "department": "...",
  "item_name": "...",
  "quantity": "...",
  "purpose": "...",
  "return_date": "..."
}

Ignore anything not related to borrowing. Be concise and accurate. Do not include explanations or extra text.

User input: {question}
"""
# Define the chat prompt template
# template = """
# You are an assistant that helps users create borrow requests (ignore anything not related to borrowing).
# You must gather the following: name, email, item name, quantity, purpose, and return date.
# Here is the user input: {question}
# """
prompt = ChatPromptTemplate.from_template(template)
chain = prompt | model

@app.route("/api/ask", methods=["POST"])
def ask():
    data = request.json
    messages = data.get("messages")

    if not messages or not isinstance(messages, list):
        return jsonify({"error": "Missing or invalid 'messages' in request."}), 400

    # Get the latest user message
    last_user_msg = next((msg["content"] for msg in reversed(messages) if msg["role"] == "user"), None)

    if not last_user_msg:
        return jsonify({"error": "No user message found."}), 400

    try:
        print("Calling LLaMA model with message:", last_user_msg)
        response = chain.invoke({"question": last_user_msg})
        print("Model response:", response)
        return jsonify({"reply": response})
    except Exception as e:
        print("Error invoking model:", str(e))
        return jsonify({"reply": "Oops! Something went wrong."}), 500

@app.route("/submit", methods=["POST"])
def submit_borrow_info():
    data = request.json
    required_fields = ["name", "email", "item_name", "quantity", "purpose", "return_date"]
    missing = [field for field in required_fields if field not in data]

    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    return jsonify({
        "message": "Borrow info received successfully.",
        "borrow_info": data
    })

@app.route("/edit", methods=["POST"])
def edit_borrow_info():
    data = request.json
    borrow_info = data.get("borrow_info")
    field = data.get("field_to_edit")
    value = data.get("new_value")

    if not borrow_info or not field or not value:
        return jsonify({"error": "Missing data."}), 400

    if field not in borrow_info:
        return jsonify({"error": f"Invalid field: {field}"}), 400

    borrow_info[field] = value
    return jsonify({
        "message": f"{field} updated successfully.",
        "updated_borrow_info": borrow_info
    })

@app.route("/api/process-image", methods=["POST"])
def process_image():
    data = request.json
    image_data = data.get("image_base64")
    question = data.get("question", "Describe this image:")

    if not image_data:
        return jsonify({"error": "No image data provided."}), 400
    try:
        image_bytes = base64.b64decode(image_data.split(",")[-1])
        image = Image.open(BytesIO(image_bytes))
        if image.mode != 'RGB':
            image = image.convert('RGB')

        filename = f"temp_{uuid.uuid4().hex}.jpg"
        image.save(filename)
        response = ollama.chat(
            model="llava",
            messages=[
                {
                    "role": "user",
                    "content": question,
                    "images": [filename]
                }
            ]
        )
        os.remove(filename)

        return jsonify({"result": response["message"]["content"]})

    except Exception as e:
        print("Error processing image:", str(e))
        return jsonify({"error": "Image processing failed."}), 500

if __name__ == "__main__":
    app.run(debug=True)
