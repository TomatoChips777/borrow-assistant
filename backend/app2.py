# from flask import Flask, request, jsonify
# from flask_cors import CORS
# from dotenv import load_dotenv
# import os
# from groq import Groq

# # Load environment variables from .env
# load_dotenv()

# # Initialize Flask app
# app = Flask(__name__)
# CORS(app)
# # Initialize Groq client with API key from environment variable
# client = Groq(api_key=os.getenv("GROQ_API_KEY"))
# template = """
# You are an assistant that extracts borrowing request details from a user's message.
# Only reply with a JSON object in this format:
# {
#   "name": "...",
#   "email": "...",
#   "department": "...",
#   "item_name": "...",
#   "quantity": "...",
#   "purpose": "...",
#   "return_date": "..."
# }

# Ignore anything not related to borrowing. Be concise and accurate. Do not include explanations or extra text.

# User input: {question}
# """

# @app.route('/api/ask', methods=['POST'])
# def ask():
#     data = request.get_json()
#     user_messages = data.get('messages', [])

#     if not user_messages:
#         return jsonify({'error': 'No conversation messages provided'}), 400

#     # Prepend system instruction to guide the model
#     system_message = {
#         "role": "system",
#         "content": template
#     }

#     messages = [system_message] + user_messages

#     try:
#         completion = client.chat.completions.create(
#             model="meta-llama/llama-4-scout-17b-16e-instruct",
#             messages=messages,
#             temperature=1,
#             max_completion_tokens=1024,
#             top_p=1,
#             stream=True,
#         )

#         response_text = ""
#         for chunk in completion:
#             delta = chunk.choices[0].delta
#             if delta and delta.content:
#                 response_text += delta.content

#         return jsonify({'reply': response_text})

#     except Exception as e:
#         return jsonify({'error': str(e)}), 500

from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
import ollama

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Prompt template
template = """
You are an assistant that extracts borrowing request details from a user's message.
Only reply with a JSON object in this format:
{{
  "name": "...",
  "email": "...",
  "department": "...",
  "item_name": "...",
  "quantity": "...",
  "purpose": "...",
  "return_date": "..."
}}
Ignore anything not related to borrowing. Be concise and accurate. Do not include explanations or extra text.

User input: {question}
"""


@app.route('/api/ask', methods=['POST'])
def ask():
    data = request.get_json()
    user_messages = data.get('messages', [])

    if not user_messages:
        return jsonify({'error': 'No conversation messages provided'}), 400

    # Combine user messages into a single string
    combined_input = "\n".join([msg["content"] for msg in user_messages if msg["role"] == "user"])
    prompt = template.format(question=combined_input)

    try:
        response = ollama.chat(
            model="llama3.2",  # or llama2, mistral, etc.
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        )

        reply = response['message']['content']
        return jsonify({'reply': reply})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# @app.route('/api/ask', methods=['POST'])
# def ask():
#     data = request.get_json()
#     messages = data.get('messages', [])

#     if not messages:
#         return jsonify({'error': 'No conversation messages provided'}), 400

#     try:
#         completion = client.chat.completions.create(
#             model="meta-llama/llama-4-scout-17b-16e-instruct",
#             messages=messages,
#             temperature=1,
#             max_completion_tokens=1024,
#             top_p=1,
#             stream=True,
#         )

#         response_text = ""
#         for chunk in completion:
#             delta = chunk.choices[0].delta
#             if delta and delta.content:
#                 response_text += delta.content

#         return jsonify({'reply': response_text})

#     except Exception as e:
#         return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(port=5000, debug=True)

# from flask import Flask, request, jsonify
# from flask_cors import CORS
# from dotenv import load_dotenv
# import os
# import re
# from groq import Groq

# # Load environment variables
# load_dotenv()

# app = Flask(__name__)
# CORS(app)

# client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# # Helper to extract fields
# def extract_borrow_info(convo):
#     text = "\n".join([msg['content'] for msg in convo if msg['role'] == 'user'])
#     name = re.search(r"\bname\b.*?:?\s*([A-Z][a-z]+\s[A-Z][a-z]+|\w+)", text, re.IGNORECASE)
#     email = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", text)
#     item = re.search(r"\b(?:borrow|need|get)\b.*?\b(\w+)", text, re.IGNORECASE)
#     quantity = re.search(r"\b\d+\b", text)
#     return_date = re.search(r"\b(?:on\s*)?(\d{4}-\d{2}-\d{2}|\w+ \d{1,2}(st|nd|rd|th)?,? \d{4})", text)

#     if all([name, email, item, quantity, return_date]):
#         return {
#             "name": name.group(1),
#             "email": email.group(0),
#             "item": item.group(1),
#             "quantity": quantity.group(0),
#             "return_date": return_date.group(1),
#             "generated_description": f"{name.group(1)} requests to borrow {quantity.group(0)} {item.group(1)} and will return it by {return_date.group(1)}."
#         }
#     return None

# @app.route('/api/ask', methods=['POST'])
# def ask():
#     data = request.get_json()
#     messages = data.get('messages', [])

#     if not messages:
#         return jsonify({'error': 'No conversation messages provided'}), 400

#     try:
#         # Generate response from LLaMA
#         completion = client.chat.completions.create(
#             model="meta-llama/llama-4-scout-17b-16e-instruct",
#             messages=messages,
#             temperature=1,
#             max_completion_tokens=1024,
#             top_p=1,
#             stream=True,
#         )

#         response_text = ""
#         for chunk in completion:
#             delta = chunk.choices[0].delta
#             if delta and delta.content:
#                 response_text += delta.content

#         # Check if we can extract full info
#         info = extract_borrow_info(messages)
#         if info:
#             print("✅ Final Borrowing Request Received:")
#             print(info)

#         return jsonify({'reply': response_text})

#     except Exception as e:
#         return jsonify({'error': str(e)}), 500

# if __name__ == '__main__':
#     app.run(port=5000, debug=True)
