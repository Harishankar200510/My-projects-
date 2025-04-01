import os
import json
import io
import threading
import fitz  # PyMuPDF for PDF text extraction
from datetime import datetime
from flask import Flask, request, render_template, jsonify
from flask_socketio import SocketIO
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Flask Configuration
app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'default-secret-key')
UPLOAD_FOLDER = 'uploads'
KNOWLEDGE_STORAGE_FOLDER = 'knowledge_storage'
ALLOWED_EXTENSIONS = {'pdf', 'txt'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(KNOWLEDGE_STORAGE_FOLDER, exist_ok=True)

# Enable WebSocket
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

# Configure Google Gemini API
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
model = genai.GenerativeModel('gemini-1.5-flash')

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

# Send real-time progress per file
def send_progress(file_id, filename, percent, status="Processing"):
    socketio.emit('progress', {'file_id': file_id, 'filename': filename, 'percentage': percent, 'status': status})
    socketio.sleep(1)

# Check allowed file types
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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

# Extract knowledge from PDF
def extract_knowledge_from_pdf(pdf_data, filename, file_id):
    try:
        send_progress(file_id, filename, 10)  # Uploading file
        file_stream = io.BytesIO(pdf_data)
        file_part = genai.upload_file(file_stream, mime_type="application/pdf")
        send_progress(file_id, filename, 30)  # File uploaded

        prompt = """Analyze the document and provide a structured JSON output:
        {
            "summary": "A brief summary of the document",
            "key_topics": ["Topic1", "Topic2"],
            "action_items": ["Action1", "Action2"],
            "entities": {"People": ["Name1"], "Organizations": ["Org1"]}
        }
        """
        send_progress(file_id, filename, 50)  # AI processing started
        response = model.generate_content([prompt, file_part])
        send_progress(file_id, filename, 70)  # AI processing completed

        if not response or not response.text:
            raise ValueError("Empty response from Gemini API")

        response_text = response.text.strip().replace('```json', '').replace('```', '').strip()
        try:
            knowledge_data = json.loads(response_text)
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON response: {response_text}")

        send_progress(file_id, filename, 80)  # Parsing response
        knowledge = PDFKnowledge(**knowledge_data)
        json_file_path = save_knowledge_to_file(knowledge, file_id, filename)
        send_progress(file_id, filename, 100, status="Completed")  # Extraction completed

        # Inform the frontend to remove the file from UI after completion
        socketio.emit('completed', {'file_id': file_id, 'filename': filename})
        return json_file_path
    except Exception as e:
        print(f"❌ Error processing document: {e}")
        send_progress(file_id, filename, 100, status="Failed")
        return None

# Save extracted knowledge to file
def save_knowledge_to_file(knowledge_data, file_id, filename):
    json_filename = f"knowledge_{file_id}_{secure_filename(filename)}.json"
    file_path = os.path.join(KNOWLEDGE_STORAGE_FOLDER, json_filename)
    try:
        with open(file_path, "w", encoding="utf-8") as json_file:
            json.dump(knowledge_data.to_dict(), json_file, indent=4)
        print(f"✅ Knowledge saved to {file_path}")
        return file_path
    except Exception as e:
        print(f"❌ Error saving knowledge: {e}")
        return None

# Handle multiple file uploads
@app.route('/upload', methods=['POST'])
def upload_files():
    files = request.files.getlist('files')
    if not files or all(f.filename == '' for f in files):
        return jsonify({"error": "No files selected"}), 400

    responses = []
    for file in files:
        if allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_id = str(datetime.now().timestamp())
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(file_path)
            with open(file_path, "rb") as f:
                pdf_data = f.read()
            threading.Thread(target=extract_knowledge_from_pdf, args=(pdf_data, filename, file_id)).start()
            responses.append({"file_id": file_id, "filename": filename, "status": "Processing"})
        else:
            responses.append({"filename": file.filename, "error": "Invalid file type"})
    return jsonify(responses)

@app.route('/')
def index():
    return render_template('upload.html')

if __name__ == '__main__':
    socketio.run(app, debug=True, host="127.0.0.1", port=5000)
