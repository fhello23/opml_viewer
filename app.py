# app.py
from flask import Flask, render_template, jsonify
import random
from collections import defaultdict # Import defaultdict
from opml_parser import parse_opml

app = Flask(__name__)

# Load the flat data list when the app starts (needed for flashcards)
CARDS_DATA = parse_opml('ttos.opml')

@app.route('/')
def index():
    """Renders the main page with both tabs."""
    if not CARDS_DATA:
        # Handle case where parsing failed or returned empty
        return "Error: Could not load card data. Check OPML file and parser.", 500

    # --- Group cards by topic for the Browse tab ---
    grouped_cards_by_topic = defaultdict(list)
    for card in CARDS_DATA:
        # Append a dictionary containing only term and details to the topic's list
        grouped_cards_by_topic[card['topic']].append({
            'term': card['term'],
            'details': card['details']
        })
    # Convert defaultdict back to a regular dict for easier template handling (optional)
    grouped_cards_dict = dict(grouped_cards_by_topic)
    # -------------------------------------------------

    # Pass the *grouped* data to the template for the browse tab
    return render_template('index.html', grouped_cards=grouped_cards_dict) # Pass grouped data

@app.route('/get_random_card')
def get_random_card():
    """API endpoint to get a random card for the flashcard tab."""
    # This endpoint still uses the original flat CARDS_DATA list
    if not CARDS_DATA:
        return jsonify({"error": "No card data available"}), 500
    # Select a random card from the original flat list
    random_card = random.choice(CARDS_DATA)
    # Ensure the response includes the topic, term, and details
    return jsonify(random_card)

if __name__ == '__main__':
    app.run(debug=True)