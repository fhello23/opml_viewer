# ✨ OPML Viewer & Flashcard Fun ✨

Tired of your awesome [SimpleMind](https://simplemind.eu/) mind maps just sitting there? Want to turn those brilliant outlines into interactive study sessions? 🧠➡️📚

This nifty little web app lets you:

1.  **Upload** your OPML files (exported from SimpleMind or similar apps).
2.  **View** the content in a clean, browseable format, organized by topic.
3.  **Generate** random flashcards from your notes to test your knowledge!

It's perfect for students, lifelong learners, or anyone who loves organizing thoughts in outlines and wants a quick way to review them.

## 🚀 Features

* **Easy Upload:** Drag-and-drop your `.opml` file right onto the landing page, or browse to select it.
* **Database Mode:** Pre-load OPML files into the `ttos/` folder for quick selection.
* **Client-Side Power:** Uploaded files are parsed and stored *in your browser* (using localStorage) for speedy access during your session. No constant server back-and-forth for viewing!
* **Browse View:** See your OPML structure clearly, with topics and expandable terms/details.
* **Flashcard Mode:** Get random "cards" (terms) from your OPML, with a button to reveal the details. Great for quick revision!
* **Clean Interface:** Built with Flask and styled with Tailwind CSS for a smooth experience.

## 🤔 How it Works (Simplified)

1.  **Choose Your File:** On the landing page, you either upload a new OPML file or select one from the server's `ttos/` directory.
2.  **Client-Side Magic (Uploads):** If you upload, JavaScript reads the file, parses the OPML structure, and stores the data (and the original file content) in your browser's local storage.
3.  **Server Assistance (Database):** If you select a server file, the app remembers your choice.
4.  **Viewer Page:** This page loads. JavaScript first checks local storage for data (if you uploaded). If not found, it asks the Flask backend (`/get_opml_data`) for the data corresponding to your selected file (either the temporary uploaded one or the server one).
5.  **Display:** The data is displayed in either the "Browse Content" or "Random Flashcards" tab.

## 📸 Screenshot Placeholder

## 🛠️ Setup & Run Locally

Want to run this on your own machine? Easy peasy!

1.  **Clone the Repository:**
    ```bash
    git clone <your-repo-url>
    cd ttos_ped # Or whatever your repo folder is called
    ```
2.  **Create a Virtual Environment (Recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate # On Windows use `venv\Scripts\activate`
    ```
3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Prepare the "Database" (Optional but Recommended):**
    * Create a folder named `ttos` in the project's root directory.
    * Place any `.opml` files you want to access via the "Use from Database" option inside this `ttos` folder.
5.  **Run the Flask App:**
    ```bash
    flask run
    ```
    (Or `python app.py` if you prefer)
6.  **Open Your Browser:** Navigate to `http://127.0.0.1:5000` (or the address shown in your terminal).

## 🖱️ How to Use

1.  Visit the landing page.
2.  **Option A (Upload):** Drag your `.opml` file onto the drop zone or click "Browse Files" to select it. It will be processed, and you'll land on the viewer page.
3.  **Option B (Database):** If you added files to the `ttos` folder, select one from the list under "Use from Database" and click "Select and Continue".
4.  On the viewer page:
    * Click the **"Browse Content"** tab to see your notes organized by topic. Click on terms to expand/collapse details.
    * Click the **"Random Flashcards"** tab to start studying. Click "Show Details" to see the info, and "Next Card" for a new one.

## 💻 Tech Stack

* **Backend:** Python, Flask
* **Frontend:** HTML, Tailwind CSS, Vanilla JavaScript
* **Parsing:** Python's `xml.etree.ElementTree` (backend), basic DOMParser (client-side JS)
* **Deployment:** Configured for Gunicorn (see `Procfile`)

## ⚠️ Important Disclaimer

The primary goal of this tool is educational review.

**IMPORTANT:** The information contained in OPML files viewed with this tool (especially those from the "database") is for **educational purposes only**. It should **NEVER** be trusted for real-life situations without verification. Medical, financial, or other critical information *must* always be confirmed with reliable, primary sources.

## 💡 Future Ideas

* Search functionality within the browse view.
* Different flashcard modes (e.g., spaced repetition hints).
* Ability to edit notes directly? (Might be complex).
* Export flashcards to other formats (Anki?).
* Themes!

Enjoy turning your outlines into knowledge! ✨