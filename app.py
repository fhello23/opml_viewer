# app.py
from flask import Flask, render_template, jsonify, request, redirect, url_for, session, flash
import random
import os
import glob
import uuid
import shutil
import tempfile
from datetime import datetime, timedelta
from collections import defaultdict
from werkzeug.utils import secure_filename
from opml_parser import parse_opml

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Needed for session

# Configuration
TTOS_FOLDER = 'ttos'
TEMP_FOLDER = os.path.join(tempfile.gettempdir(), 'opml_viewer_uploads')

# Ensure temp folder exists
os.makedirs(TEMP_FOLDER, exist_ok=True)

# Function to get available OPML files (only from ttos folder)
def get_available_opml_files():
    # Get files only from ttos folder
    ttos_files = glob.glob(f"{TTOS_FOLDER}/*.opml")
    return ttos_files

# Helper function to extract clean filename
def get_clean_filename(file_path):
    if not file_path:
        return "Unknown file"
    
    # Get just the filename without path
    filename = os.path.basename(file_path)
    
    # Remove the extension
    clean_name = os.path.splitext(filename)[0]
    
    return clean_name

# Function to clean up old temporary files (older than 1 hour)
def cleanup_temp_files():
    now = datetime.now()
    for filename in os.listdir(TEMP_FOLDER):
        file_path = os.path.join(TEMP_FOLDER, filename)
        file_modified = datetime.fromtimestamp(os.path.getmtime(file_path))
        if now - file_modified > timedelta(hours=1):
            try:
                os.remove(file_path)
                print(f"Removed old temp file: {file_path}")
            except Exception as e:
                print(f"Error removing temp file: {e}")

# Load cards data based on file path
def load_cards_data(file_path=None):
    if not file_path:
        # Check if there's a temporary uploaded file
        temp_file_id = session.get('temp_file_id')
        if temp_file_id:
            temp_file_path = os.path.join(TEMP_FOLDER, temp_file_id)
            if os.path.exists(temp_file_path):
                return parse_opml(temp_file_path)
        
        # Otherwise use selected file from ttos folder
        file_path = session.get('current_opml')
        if not file_path and get_available_opml_files():
            # Default to first available file if none selected
            file_path = get_available_opml_files()[0]
    
    if file_path:
        return parse_opml(file_path)
    
    return []

@app.route('/')
def index():
    """Renders the landing page."""
    # Clean up old temporary files
    cleanup_temp_files()
    
    # Get list of available OPML files from ttos folder
    available_files = get_available_opml_files()
    
    # Show landing page
    return render_template('landing.html', available_files=available_files)

@app.route('/viewer')
def viewer():
    """Renders the viewer which will load data via JavaScript."""
    # Simplified viewer route - client will request data via AJAX
    return render_template('index.html')

@app.route('/get_opml_data')
def get_opml_data():
    """API endpoint to get OPML data for the client-side app."""
    # Get file path from session or find default
    file_path = session.get('current_opml')
    using_uploaded = 'temp_file_id' in session
    uploaded_filename = session.get('uploaded_filename', 'Uploaded OPML')
    
    # Load cards data
    cards_data = load_cards_data(file_path if not using_uploaded else None)
    
    if not cards_data:
        return jsonify({"error": "No card data available"}), 500
    
    # Get display name for file
    display_filename = uploaded_filename if using_uploaded else get_clean_filename(file_path)
    
    # Return the data in JSON format
    return jsonify({
        "cards": cards_data,
        "current_file": display_filename,
        "using_uploaded": using_uploaded
    })

@app.route('/get_random_card')
def get_random_card():
    """API endpoint to get a random card for the flashcard tab."""
    # This is kept for backwards compatibility
    cards_data = load_cards_data()
    
    if not cards_data:
        return jsonify({"error": "No card data available"}), 500
    
    # Select a random card
    random_card = random.choice(cards_data)
    
    # Ensure the response includes the topic, term, and details
    return jsonify(random_card)

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload for non-JS clients or as fallback."""
    if 'file' not in request.files:
        flash('No file part', 'error')
        return redirect(url_for('index'))
    
    file = request.files['file']
    
    if file.filename == '':
        flash('No selected file', 'error')
        return redirect(url_for('index'))
    
    if file and file.filename.lower().endswith('.opml'):
        # Generate a unique filename for temporary storage
        temp_file_id = f"{uuid.uuid4()}.opml"
        temp_file_path = os.path.join(TEMP_FOLDER, temp_file_id)
        
        # Save the file to the temporary directory
        file.save(temp_file_path)
        
        # Store references in session (much smaller than the file content)
        session['temp_file_id'] = temp_file_id
        session['uploaded_filename'] = file.filename
        
        # Clear any previously selected file
        if 'current_opml' in session:
            session.pop('current_opml')
        
        flash(f'File uploaded successfully: {file.filename}', 'success')
        return redirect(url_for('viewer'))
    
    flash('Invalid file type. Please upload an OPML file.', 'error')
    return redirect(url_for('index'))

@app.route('/select_file', methods=['POST'])
def select_file():
    """Select an existing OPML file for non-JS clients or as fallback."""
    selected_file = request.form.get('file_path')
    
    # Clear any uploaded file references
    if 'temp_file_id' in session:
        # Remove the temporary file if it exists
        temp_file_path = os.path.join(TEMP_FOLDER, session['temp_file_id'])
        if os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
            except Exception as e:
                print(f"Error removing temp file: {e}")
        
        session.pop('temp_file_id')
    
    if 'uploaded_filename' in session:
        session.pop('uploaded_filename')
    
    if selected_file and os.path.exists(selected_file):
        session['current_opml'] = selected_file
        
        # Get clean filename for flash message
        clean_name = get_clean_filename(selected_file)
        flash(f'Now using: {clean_name}', 'success')
    else:
        flash('Selected file not found', 'error')
    
    return redirect(url_for('viewer'))

if __name__ == '__main__':
    app.run(debug=True)