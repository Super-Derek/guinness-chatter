from flask import Flask, request, jsonify, render_template
import openai
import os
import markdown
import requests
from openai import OpenAI
from pdfminer.high_level import extract_text
import logging
import re
from dotenv import load_dotenv

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Load environment variables from .env file
load_dotenv()

# Get the system prompt from the environment variable
system_prompt_content = os.getenv('SYSTEM_PROMPT')

app = Flask(__name__)

# Set up logging
#logging.basicConfig(level=logging.INFO)  # Change to INFO or WARNING for production
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s', handlers=[logging.FileHandler("app.log"), logging.StreamHandler()])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        user_message = request.json.get('message')
        app.logger.info(f"User message: {user_message}")

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt_content},
                {"role": "user", "content": user_message},
            ],
            temperature=1.0,
            top_p=1.0,
            frequency_penalty=0.5,
            presence_penalty=0.5,
            max_tokens=600,
            timeout=120  # Set a higher timeout value
        )

        bot_reply_markdown = response.choices[0].message.content.strip()
        app.logger.info(f"Bot reply (Markdown): {bot_reply_markdown}")

        # Convert Markdown to HTML
        bot_reply_html = markdown.markdown(bot_reply_markdown)
        app.logger.info(f"Bot reply (HTML): {bot_reply_html}")

        return jsonify(reply=bot_reply_html)

    except openai.Timeout as e:
        app.logger.error(f"OpenAI API request timed out: {e}")
        return jsonify(reply="The request timed out. Please try again later."), 504

    except openai.APIError as e:
        app.logger.error(f"OpenAI API returned an API Error: {e}")
        return jsonify(reply="There was an error with the API. Please try again later."), 500

    except openai.APIConnectionError as e:
        app.logger.error(f"OpenAI API request failed to connect: {e}")
        return jsonify(reply="Failed to connect to the API. Please check your network connection."), 503

    except openai.InvalidRequestError as e:
        app.logger.error(f"Invalid request error: {e}")
        return jsonify(reply="The request was invalid. Please check your input and try again."), 400

    except openai.AuthenticationError as e:
        app.logger.error(f"Authentication error: {e}")
        return jsonify(reply="Authentication failed. Please check your API key."), 401

    except openai.PermissionError as e:
        app.logger.error(f"Permission error: {e}")
        return jsonify(reply="Permission denied. Please check your API key permissions."), 403

    except openai.RateLimitError as e:
        app.logger.error(f"Rate limit error: {e}")
        return jsonify(reply="Rate limit exceeded. Please try again later."), 429

    except Exception as e:
        app.logger.error(f"General error: {e}")
        return jsonify(reply="An unexpected error occurred. Please try again later."), 500

# The following block is only for development. In production, use a WSGI server like Gunicorn.
if __name__ == '__main__':
    app.run(port=8000)
