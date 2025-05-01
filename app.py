# app.py
from flask import Flask, render_template, jsonify, request, redirect, url_for, session, flash
import random
import os
import glob
import uuid
import shutil
import tempfile
import logging
from datetime import datetime, timedelta
from collections import defaultdict
from werkzeug.utils import secure_filename
from opml_parser import parse_opml

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Needed for session
# Ensure session cookies persist
app.config['SESSION_PERMANENT'] = True

# Configuration
TTOS_FOLDER = 'ttos'
TEMP_FOLDER = os.path.join(tempfile.gettempdir(), 'opml_viewer_uploads')

# Ensure temp folder exists
os.makedirs(TEMP_FOLDER, exist_ok=True)

# Function to get available OPML files (only from ttos folder)
def get_available_opml_files():
    # Get files only from ttos folder
    ttos_files = glob.glob(f"{TTOS_FOLDER}/*.opml")
    
    # Sort files to ensure consistent ordering
    # Prioritize Pediatría P1.opml for testing if it exists
    ttos_files.sort()
    
    # Move Pediatría to the end for testing
    for i, file_path in enumerate(ttos_files):
        if "Pediatría" in file_path:
            ttos_files.append(ttos_files.pop(i))
            break
    
    logger.debug(f"Available files: {ttos_files}")
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
                logger.debug(f"Removed old temp file: {file_path}")
            except Exception as e:
                logger.error(f"Error removing temp file: {e}")

# Load cards data based on file path
def load_cards_data(file_path=None):
    logger.debug(f"Loading cards data with file_path: {file_path}")
    
    if not file_path:
        # Check if there's a temporary uploaded file
        temp_file_id = session.get('temp_file_id')
        logger.debug(f"Temp file ID from session: {temp_file_id}")
        
        if temp_file_id:
            temp_file_path = os.path.join(TEMP_FOLDER, temp_file_id)
            if os.path.exists(temp_file_path):
                logger.debug(f"Loading from temp file: {temp_file_path}")
                return parse_opml(temp_file_path)
            else:
                logger.warning(f"Temp file not found: {temp_file_path}")
                if 'temp_file_id' in session:
                    session.pop('temp_file_id')
        
        # Otherwise use selected file from ttos folder
        file_path = session.get('current_opml')
        logger.debug(f"Current OPML from session: {file_path}")
        
        available_files = get_available_opml_files()
        if not file_path and available_files:
            # Default to first available file if none selected
            file_path = available_files[0]
            logger.debug(f"Using default file: {file_path}")
            # Store this default in the session
            session['current_opml'] = file_path
            # Force save session
            session.modified = True
    
    if file_path:
        # Verify file exists
        if os.path.exists(file_path):
            logger.debug(f"Loading from file: {file_path}")
            return parse_opml(file_path)
        else:
            logger.warning(f"Selected file doesn't exist: {file_path}")
            if 'current_opml' in session:
                session.pop('current_opml')
            
            # Try to load a default file instead
            available_files = get_available_opml_files()
            if available_files:
                logger.debug(f"Falling back to first available file: {available_files[0]}")
                session['current_opml'] = available_files[0]
                session.modified = True
                return parse_opml(available_files[0])
    
    return []

@app.route('/')
def index():
    """Renders the landing page."""
    # Clean up old temporary files
    cleanup_temp_files()
    
    # Get list of available OPML files from ttos folder
    available_files = get_available_opml_files()
    
    # Set default file in session if not already set
    if not session.get('current_opml') and available_files:
        session['current_opml'] = available_files[0]
        logger.debug(f"Setting default file in session: {available_files[0]}")
        session.modified = True
    
    # Log current session state
    logger.debug(f"Session on index page: {dict(session)}")
    
    # Show landing page
    return render_template('landing.html', available_files=available_files)

@app.route('/viewer')
def viewer():
    """Renders the viewer which will load data via JavaScript."""
    # Ensure we have a file selected if available
    available_files = get_available_opml_files()
    logger.debug(f"Session before viewer: {dict(session)}")
    
    if not session.get('current_opml') and not session.get('temp_file_id') and available_files:
        session['current_opml'] = available_files[0]
        logger.debug(f"Setting default file in viewer: {available_files[0]}")
        session.modified = True
        
    # Simplified viewer route - client will request data via AJAX
    return render_template('index.html')

@app.route('/get_opml_data')
def get_opml_data():
    """API endpoint to get OPML data for the client-side app."""
    # Get file path from session or find default
    file_path = session.get('current_opml')
    logger.debug(f"Current OPML file from session: {file_path}")
    
    using_uploaded = 'temp_file_id' in session
    uploaded_filename = session.get('uploaded_filename', 'Uploaded OPML')
    
    # Load cards data
    cards_data = load_cards_data(file_path if not using_uploaded else None)
    
    if not cards_data:
        logger.error("No card data available for file path: {}".format(file_path))
        return jsonify({"error": "No card data available"}), 500
    
    # Get display name for file
    display_filename = uploaded_filename if using_uploaded else get_clean_filename(file_path)
    logger.debug(f"Display filename: {display_filename}")
    
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
        
        # Clear entire session first to avoid conflicts
        session.clear()
        
        # Store references in session (much smaller than the file content)
        session['temp_file_id'] = temp_file_id
        session['uploaded_filename'] = file.filename
        logger.debug(f"Uploaded file: {file.filename}, temp ID: {temp_file_id}")
        session.modified = True
        
        flash(f'File uploaded successfully: {file.filename}', 'success')
        return redirect(url_for('viewer'))
    
    flash('Invalid file type. Please upload an OPML file.', 'error')
    return redirect(url_for('index'))

@app.route('/select_file_direct')
def select_file_direct():
    """Direct file selection via GET request for debugging."""
    selected_file = request.args.get('file')
    logger.debug(f"Direct file selection: {selected_file}")
    
    # Clear the session completely
    session.clear()
    
    if selected_file and os.path.exists(selected_file):
        # Set the new file path directly
        session['current_opml'] = selected_file
        logger.debug(f"Direct set current_opml to: {selected_file}")
        session.modified = True
        
        # Get clean filename for flash message
        clean_name = get_clean_filename(selected_file)
        flash(f'Now using: {clean_name}', 'success')
    else:
        flash('Selected file not found', 'error')
        logger.error(f"Selected file not found: {selected_file}")
    
    # Log the session state after selection
    logger.debug(f"Session after direct selection: {dict(session)}")
    
    return redirect(url_for('viewer'))

@app.route('/select_file', methods=['POST'])
def select_file():
    """Select an existing OPML file for non-JS clients or as fallback."""
    selected_file = request.form.get('file_path')
    logger.debug(f"Selected file from form: {selected_file}")
    
    # Clear the entire session first to prevent any conflicts
    session.clear()
    
    if selected_file and os.path.exists(selected_file):
        # Set the new file
        session['current_opml'] = selected_file
        logger.debug(f"Set current_opml in session to: {selected_file}")
        session.modified = True
        
        # Get clean filename for flash message
        clean_name = get_clean_filename(selected_file)
        flash(f'Now using: {clean_name}', 'success')
    else:
        flash('Selected file not found', 'error')
        logger.error(f"Selected file not found: {selected_file}")
    
    # Log the session state after selection
    logger.debug(f"Session after file selection: {dict(session)}")
    
    return redirect(url_for('viewer'))

@app.route('/clear_storage')
def clear_storage():
    """Helper route to completely clear session and force file reselection."""
    session.clear()
    logger.debug("Cleared session completely")
    flash('Storage cleared. Please select a file again.', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)