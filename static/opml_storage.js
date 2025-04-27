// Handle client-side OPML parsing and browser storage

// Storage keys
const STORAGE_KEYS = {
    CURRENT_FILE: 'opml_viewer_current_file',
    UPLOADED_FILE: 'opml_viewer_uploaded_file',
    UPLOADED_FILENAME: 'opml_viewer_uploaded_filename',
    PARSED_DATA: 'opml_viewer_parsed_data'
};

// OPML Parser (client-side implementation)
class OPMLParser {
    constructor() {
        this.domParser = new DOMParser();
    }

    parseOPML(xmlContent) {
        try {
            // Parse XML content
            const xmlDoc = this.domParser.parseFromString(xmlContent, "text/xml");
            
            // Check for parsing errors
            const parseError = xmlDoc.querySelector("parsererror");
            if (parseError) {
                console.error("XML parsing error:", parseError.textContent);
                return { error: "Failed to parse OPML file" };
            }
            
            // Extract cards from the OPML structure
            return this._extractCards(xmlDoc);
        } catch (error) {
            console.error("Error parsing OPML:", error);
            return { error: error.message };
        }
    }
    
    _cleanText(text) {
        if (!text) return "";
        return text.replace(/\s+/g, ' ').trim();
    }
    
    _getDetailsRecursive(outlineElement, depth = 0) {
        const details = [];
        const indent = "  ".repeat(depth);
        const elementText = this._cleanText(outlineElement.getAttribute('text'));
        
        if (elementText) {
            details.push(`${indent}- ${elementText}`);
        }
        
        const childOutlines = outlineElement.querySelectorAll(`:scope > outline`);
        childOutlines.forEach(child => {
            details.push(...this._getDetailsRecursive(child, depth + 1));
        });
        
        return details;
    }
    
    _extractCards(xmlDoc) {
        const cards = [];
        const body = xmlDoc.querySelector('body');
        
        if (!body) {
            return { error: "Invalid OPML structure: missing body element" };
        }
        
        // Get all top-level outlines (topics)
        const topicOutlines = body.querySelectorAll(':scope > outline');
        
        topicOutlines.forEach(topicOutline => {
            const topicText = this._cleanText(topicOutline.getAttribute('text'));
            
            // Get all second-level outlines (terms)
            const termOutlines = topicOutline.querySelectorAll(':scope > outline');
            
            termOutlines.forEach(termOutline => {
                const termText = this._cleanText(termOutline.getAttribute('text'));
                
                // Check if this term has child outlines (details)
                const hasDetails = termOutline.querySelector('outline') !== null;
                
                if (hasDetails) {
                    const rawDetails = [];
                    const detailOutlines = termOutline.querySelectorAll(':scope > outline');
                    
                    detailOutlines.forEach(detailOutline => {
                        rawDetails.push(...this._getDetailsRecursive(detailOutline, 0));
                    });
                    
                    const detailsList = rawDetails.filter(d => d && d !== '-');
                    
                    if (termText && detailsList.length > 0) {
                        cards.push({
                            topic: topicText,
                            term: termText,
                            details: detailsList
                        });
                    }
                }
            });
        });
        
        return { cards };
    }
}

// Storage Manager
class StorageManager {
    constructor() {
        this.parser = new OPMLParser();
    }
    
    // Save uploaded file
    saveUploadedFile(fileContent, fileName) {
        try {
            // Parse the OPML content first to validate
            const result = this.parser.parseOPML(fileContent);
            
            if (result.error) {
                return { success: false, error: result.error };
            }
            
            // Store the parsed data
            localStorage.setItem(STORAGE_KEYS.PARSED_DATA, JSON.stringify(result));
            
            // Store file info
            localStorage.setItem(STORAGE_KEYS.UPLOADED_FILE, fileContent);
            localStorage.setItem(STORAGE_KEYS.UPLOADED_FILENAME, fileName);
            localStorage.setItem(STORAGE_KEYS.CURRENT_FILE, 'uploaded');
            
            return { success: true, data: result };
        } catch (error) {
            console.error("Error saving file to localStorage:", error);
            return { success: false, error: error.message };
        }
    }
    
    // Clear uploaded file
    clearUploadedFile() {
        localStorage.removeItem(STORAGE_KEYS.UPLOADED_FILE);
        localStorage.removeItem(STORAGE_KEYS.UPLOADED_FILENAME);
        localStorage.removeItem(STORAGE_KEYS.PARSED_DATA);
        localStorage.removeItem(STORAGE_KEYS.CURRENT_FILE);
    }
    
    // Check if we have an uploaded file
    hasUploadedFile() {
        return localStorage.getItem(STORAGE_KEYS.UPLOADED_FILE) !== null;
    }
    
    // Get uploaded filename
    getUploadedFilename() {
        return localStorage.getItem(STORAGE_KEYS.UPLOADED_FILENAME);
    }
    
    // Get current file type ('uploaded' or 'db')
    getCurrentFileType() {
        return localStorage.getItem(STORAGE_KEYS.CURRENT_FILE);
    }
    
    // Set current file type to DB file
    selectDbFile(dbFileName) {
        this.clearUploadedFile();
        localStorage.setItem(STORAGE_KEYS.CURRENT_FILE, 'db:' + dbFileName);
    }
    
    // Get the parsed data
    getParsedData() {
        const data = localStorage.getItem(STORAGE_KEYS.PARSED_DATA);
        return data ? JSON.parse(data) : null;
    }
}

// Initialize the storage manager
const opmlStorage = new StorageManager();

// Export for use in other scripts
window.opmlStorage = opmlStorage; 