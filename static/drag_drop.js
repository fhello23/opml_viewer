// Handle drag and drop functionality for OPML files

document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const uploadForm = document.getElementById('upload-form');
    const uploadStatus = document.getElementById('upload-status');
    const browseButton = document.querySelector('#drop-zone button');

    // Handle drag events
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone?.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    // Highlight drop zone when item is dragged over it
    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone?.addEventListener(eventName, highlight, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone?.addEventListener(eventName, unhighlight, false);
    });

    function highlight() {
        dropZone.classList.add('border-blue-500', 'bg-blue-50');
    }

    function unhighlight() {
        dropZone.classList.remove('border-blue-500', 'bg-blue-50');
    }

    // Handle dropped files
    dropZone?.addEventListener('drop', handleDrop, false);
    
    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        
        if (files.length) {
            fileInput.files = files;
            handleFiles(files);
        }
    }

    function handleFiles(files) {
        const file = files[0];
        
        // Check if file is an OPML file
        if (!file.name.toLowerCase().endsWith('.opml')) {
            if (uploadStatus) {
                uploadStatus.textContent = 'Error: Please upload an OPML file (.opml)';
                uploadStatus.classList.add('text-red-600');
                uploadStatus.classList.remove('text-green-600', 'hidden');
            }
            return;
        }
        
        // Read the file content
        const reader = new FileReader();
        
        reader.onload = function(e) {
            const fileContent = e.target.result;
            
            // Use our client-side storage
            if (window.opmlStorage) {
                const result = window.opmlStorage.saveUploadedFile(fileContent, file.name);
                
                if (result.success) {
                    if (uploadStatus) {
                        uploadStatus.textContent = `File "${file.name}" processed successfully!`;
                        uploadStatus.classList.add('text-green-600');
                        uploadStatus.classList.remove('text-red-600', 'hidden');
                    }
                    
                    // Redirect to viewer page
                    setTimeout(() => {
                        window.location.href = '/viewer';
                    }, 500);
                } else {
                    if (uploadStatus) {
                        uploadStatus.textContent = `Error: ${result.error || 'Failed to parse OPML file'}`;
                        uploadStatus.classList.add('text-red-600');
                        uploadStatus.classList.remove('text-green-600', 'hidden');
                    }
                }
            } else {
                // Fallback if storage API is not available
                if (uploadStatus) {
                    uploadStatus.textContent = `File "${file.name}" selected. Uploading...`;
                    uploadStatus.classList.remove('hidden');
                }
                
                // Submit the form (old behavior)
                if (uploadForm) uploadForm.submit();
            }
        };
        
        reader.onerror = function() {
            if (uploadStatus) {
                uploadStatus.textContent = 'Error reading file';
                uploadStatus.classList.add('text-red-600');
                uploadStatus.classList.remove('text-green-600', 'hidden');
            }
        };
        
        reader.readAsText(file);
    }

    // Handle file input change
    fileInput?.addEventListener('change', function() {
        if (this.files.length) {
            handleFiles(this.files);
        }
    });

    // Click on drop zone to trigger file input
    dropZone?.addEventListener('click', (e) => {
        // Only trigger if not clicking on the button itself
        if (e.target !== browseButton && !browseButton?.contains(e.target)) {
            fileInput.click();
        }
    });
    
    // Make browse button work
    browseButton?.addEventListener('click', (e) => {
        e.preventDefault();
        fileInput.click();
    });
    
    // Handle select from database
    const dbSelector = document.querySelector('form[action="/select_file"]');
    const dbRadios = document.querySelectorAll('input[name="file_path"]');
    
    dbRadios.forEach(radio => {
        radio?.addEventListener('change', function() {
            // Store selection in local storage
            if (window.opmlStorage) {
                const fileName = this.parentElement.querySelector('span').textContent.trim();
                window.opmlStorage.selectDbFile(fileName);
            }
        });
    });
    
    dbSelector?.addEventListener('submit', function(e) {
        if (window.opmlStorage) {
            // Client-side selection is already saved
            e.preventDefault();
            window.location.href = '/viewer';
        }
        // Otherwise let the form submit normally
    });
    
    // Check if we should pre-select based on local storage
    const currentFile = window.opmlStorage?.getCurrentFileType();
    if (currentFile && currentFile.startsWith('db:')) {
        const fileName = currentFile.substring(3);
        dbRadios.forEach(radio => {
            const radioLabel = radio.parentElement.querySelector('span').textContent.trim();
            if (radioLabel === fileName) {
                radio.checked = true;
            }
        });
    }
}); 