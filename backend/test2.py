from flask import Flask, request, jsonify
from flask_cors import CORS
import base64
from PIL import Image
from io import BytesIO
import uuid
import os
import ollama

app = Flask(__name__)
CORS(app)

@app.route("/api/process-image", methods=["POST"])
def process_image():
    data = request.json
    image_data = data.get("image_base64")
    question = data.get("question", "Describe this image:")

    if not image_data:
        return jsonify({"error": "No image data provided."}), 400

    try:
        # Decode base64 image
        image_bytes = base64.b64decode(image_data.split(",")[-1])
        image = Image.open(BytesIO(image_bytes))

        # Save image temporarily
        filename = f"temp_{uuid.uuid4().hex}.jpg"
        image.save(filename)

        # Use the Python Ollama SDK to interact with LLaVA
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

        # Clean up image
        os.remove(filename)

        return jsonify({"result": response["message"]["content"]})

    except Exception as e:
        print("Error processing image:", str(e))
        return jsonify({"error": "Image processing failed."}), 500

if __name__ == "__main__":
    app.run(port=5001, debug=True)
