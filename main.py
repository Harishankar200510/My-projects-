import os
import json
import certifi
import pathlib
import io
import threading
import fitz  # PyMuPDF for PDF text extraction
from datetime import datetime
from flask import Flask, request, render_template, redirect, url_for, flash
from flask_socketio import SocketIO
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import google.generativeai as genai
class PDFKnowledge:
    def __init__(self, summary="", key_topics=None, action_items=None, entities=None):
        self.summary = summary
        self.key_topics = key_topics if key_topics else []
        self.action_items = action_items if action_items else []
        self.entities = entities if entities else {}

    def to_dict(self):
        return {
            "summary": self.summary,
            "key_topics": self.key_topics,
            "action_items": self.action_items,
            "entities": self.entities,
        }


# Load environment variables
load_dotenv()

# Flask Configuration
app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'default-secret-key')
UPLOAD_FOLDER = 'uploads'
KNOWLEDGE_STORAGE_FOLDER = 'knowledge_storage'
ALLOWED_EXTENSIONS = {'pdf', 'txt'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(KNOWLEDGE_STORAGE_FOLDER, exist_ok=True)

# Enable WebSocket
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

# Configure Google Gemini API
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY is not set in the environment variables.")
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# Send real-time progress
def send_progress(percent):
    socketio.emit('progress', {'percentage': percent})
    socketio.sleep(1)  # Ensure immediate update

# Extract text from PDF
def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        with fitz.open(pdf_path) as doc:
            for page in doc:
                text += page.get_text("text") + "\n"
    except Exception as e:
        print(f"❌ Error extracting text: {e}")
    return text.strip()

# Process document with Gemini
# Extract knowledge from PDF
def extract_knowledge_from_pdf(pdf_data: bytes, filename: str, file_id: str):
    try:
        send_progress(10)  # Step 1: Uploading file
        file_stream = io.BytesIO(pdf_data)
        file_part = genai.upload_file(file_stream, mime_type="application/pdf")
        
        send_progress(30)  # Step 2: File uploaded successfully

        # Define AI prompt for extraction
        prompt = """Analyze the document and provide a structured JSON output:
        {
            "summary": "A brief summary of the document",
            "key_topics": ["Topic1", "Topic2"],
            "action_items": ["Action1", "Action2"],
            "entities": {"People": ["Name1"], "Organizations": ["Org1"]}
        }
        """
        
        send_progress(50)  # Step 3: AI processing started
        response = model.generate_content([prompt, file_part])

        send_progress(70)  # Step 4: AI processing completed

        if not response or not response.text:
            raise ValueError("Empty response from Gemini API")

        response_text = response.text.strip().replace('```json', '').replace('```', '').strip()
        
        try:
            knowledge_data = json.loads(response_text)
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON response: {response_text}")

        send_progress(80)  # Step 5: Parsing response

        knowledge = PDFKnowledge(**knowledge_data)
        json_file_path = save_knowledge_to_file(knowledge, file_id, filename)

        send_progress(100)  # Step 6: Extraction completed

        return json_file_path
    except Exception as e:
        print(f"❌ Error processing document: {e}")
        send_progress(100)  # Ensure progress completes even on failure
        return None



# Save knowledge to file
# Save knowledge to file
def save_knowledge_to_file(knowledge_data, file_id, filename):
    json_filename = f"knowledge_{file_id}_{secure_filename(filename)}.json"
    file_path = os.path.join(KNOWLEDGE_STORAGE_FOLDER, json_filename)

    try:
        # Convert PDFKnowledge object to dictionary
        with open(file_path, "w", encoding="utf-8") as json_file:
            json.dump(knowledge_data.to_dict(), json_file, indent=4)  # Convert before saving

        print(f"✅ Knowledge saved to {file_path}")
        return file_path
    except Exception as e:
        print(f"❌ Error saving knowledge: {e}")
        return None

    # Define allowed file extensions
ALLOWED_EXTENSIONS = {'pdf', 'txt'}
# Function to check if file type is allowed
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    # File Type Validation
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# File Upload Route
@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files.get('file')
    if not file or file.filename == '':
        flash("No selected file")
        return redirect(request.url)

    if allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        send_progress(10)  # File upload started
        file.save(file_path)

        send_progress(30)  # File uploaded

        # Read the file in binary mode
        with open(file_path, "rb") as f:
            pdf_data = f.read()  # Read as bytes
        
        file_id = str(datetime.now().timestamp())  # Unique file ID
        
        # Start extraction in a separate thread
        threading.Thread(target=extract_knowledge_from_pdf, args=(pdf_data, filename, file_id)).start()

        flash("File uploaded successfully. Knowledge extraction in progress!")
        return redirect(url_for('index'))
    
    flash("Invalid file type")
    return redirect(request.url)

@app.route('/')
def index():
    return render_template('upload.html')

if __name__ == '__main__':
    socketio.run(app, debug=True, host="127.0.0.1", port=5000)
