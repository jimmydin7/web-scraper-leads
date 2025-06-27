
let scrapingInterval = null;
let isScrapingActive = false;
let keywords = [];
let places = [];

const scrapeForm = document.getElementById('scrapeForm');
const startBtn = document.getElementById('startBtn');
const statusSection = document.getElementById('statusSection');
const resultsSection = document.getElementById('resultsSection');
const statusBadge = document.getElementById('statusBadge');
const statusText = document.getElementById('statusText');
const progressFill = document.getElementById('progressFill');
const progressText = document.getElementById('progressText');
const foundCount = document.getElementById('foundCount');
const statusMessage = document.getElementById('statusMessage');
const resultsTableBody = document.getElementById('resultsTableBody');
const downloadExcel = document.getElementById('downloadExcel');
const downloadTxt = document.getElementById('downloadTxt');
const copyClipboard = document.getElementById('copyClipboard');

const keywordContainer = document.getElementById('keywordContainer');
const keywordInput = document.getElementById('keywordInput');
const keywordsHidden = document.getElementById('keywords');

const placeContainer = document.getElementById('placeContainer');
const placeInput = document.getElementById('placeInput');
const placesHidden = document.getElementById('places');


document.addEventListener('DOMContentLoaded', function() {
    scrapeForm.addEventListener('submit', handleFormSubmit);
    downloadExcel.addEventListener('click', handleDownloadExcel);
    downloadTxt.addEventListener('click', handleDownloadTxt);
    copyClipboard.addEventListener('click', handleCopyClipboard);
    
    // Keyword input functionality
    keywordInput.addEventListener('keydown', handleKeywordInput);
    keywordInput.addEventListener('blur', handleKeywordBlur);
    keywordContainer.addEventListener('click', focusKeywordInput);
    
    // Place input functionality
    placeInput.addEventListener('keydown', handlePlaceInput);
    placeInput.addEventListener('blur', handlePlaceBlur);
    placeContainer.addEventListener('click', focusPlaceInput);
});


function focusKeywordInput(e) {
    if (e.target === keywordContainer) {
        keywordInput.focus();
    }
}


function handleKeywordInput(e) {
    const value = keywordInput.value.trim();
    

    if ((e.key === ' ' || e.key === 'Enter' || e.key === ',' || e.key === 'Tab') && value) {
        e.preventDefault();
        addKeyword(value);
        keywordInput.value = '';
    }
    

    if (e.key === 'Backspace' && !keywordInput.value && keywords.length > 0) {
        removeKeyword(keywords.length - 1);
    }
}


function handleKeywordBlur() {
    const value = keywordInput.value.trim();
    if (value) {
        addKeyword(value);
        keywordInput.value = '';
    }
}


function addKeyword(keyword) {

    keyword = keyword.toLowerCase().replace(/[^a-zA-Z0-9\s]/g, '').trim();
    

    if (!keyword || keywords.includes(keyword)) {
        return;
    }
    
    keywords.push(keyword);
    updateKeywordDisplay();
    updateHiddenInput();
}

// Remove a keyword
function removeKeyword(index) {
    if (index >= 0 && index < keywords.length) {
        keywords.splice(index, 1);
        updateKeywordDisplay();
        updateHiddenInput();
    }
}

// Update the visual display of keywords
function updateKeywordDisplay() {
    // Remove existing bubbles
    const existingBubbles = keywordContainer.querySelectorAll('.keyword-bubble');
    existingBubbles.forEach(bubble => bubble.remove());
    
    // Add bubbles for each keyword
    keywords.forEach((keyword, index) => {
        const bubble = document.createElement('div');
        bubble.className = 'keyword-bubble';
        bubble.innerHTML = `
            <span>${keyword}</span>
            <div class="remove-keyword" onclick="removeKeyword(${index})">×</div>
        `;
        
        // Insert before the input
        keywordContainer.insertBefore(bubble, keywordInput);
    });
    
    // Update placeholder
    if (keywords.length === 0) {
        keywordInput.placeholder = 'Type keywords and press space or enter...';
    } else {
        keywordInput.placeholder = 'Add more keywords...';
    }
}

// Update the hidden input with keywords
function updateHiddenInput() {
    keywordsHidden.value = keywords.join(' ');
}

// Focus the place input when container is clicked
function focusPlaceInput(e) {
    if (e.target === placeContainer) {
        placeInput.focus();
    }
}

// Handle place input
function handlePlaceInput(e) {
    const value = placeInput.value.trim();
    if ((e.key === ' ' || e.key === 'Enter' || e.key === ',' || e.key === 'Tab') && value) {
        e.preventDefault();
        addPlace(value);
        placeInput.value = '';
    }
    if (e.key === 'Backspace' && !placeInput.value && places.length > 0) {
        removePlace(places.length - 1);
    }
}

// Handle place input blur
function handlePlaceBlur() {
    const value = placeInput.value.trim();
    if (value) {
        addPlace(value);
        placeInput.value = '';
    }
}

// Add a place bubble
function addPlace(place) {
    place = place.toLowerCase().replace(/[^a-zA-Z0-9\s]/g, '').trim();
    if (!place || places.includes(place)) {
        return;
    }
    places.push(place);
    updatePlaceDisplay();
    updatePlacesHiddenInput();
}

// Remove a place
function removePlace(index) {
    if (index >= 0 && index < places.length) {
        places.splice(index, 1);
        updatePlaceDisplay();
        updatePlacesHiddenInput();
    }
}

// Update the visual display of places
function updatePlaceDisplay() {
    const existingBubbles = placeContainer.querySelectorAll('.keyword-bubble');
    existingBubbles.forEach(bubble => bubble.remove());
    places.forEach((place, index) => {
        const bubble = document.createElement('div');
        bubble.className = 'keyword-bubble';
        bubble.innerHTML = `
            <span>${place}</span>
            <div class="remove-keyword" onclick="removePlace(${index})">×</div>
        `;
        placeContainer.insertBefore(bubble, placeInput);
    });
    if (places.length === 0) {
        placeInput.placeholder = 'Type locations and press space or enter...';
    } else {
        placeInput.placeholder = 'Add more locations...';
    }
}

// Update the hidden input with places
function updatePlacesHiddenInput() {
    placesHidden.value = places.join(' ');
}

// Handle form submission
async function handleFormSubmit(e) {
    e.preventDefault();
    
    if (isScrapingActive) {
        return;
    }
    
    if (keywords.length === 0 || places.length === 0) {
        alert('Please add at least one keyword and one location.');
        return;
    }
    
    // Start scraping
    try {
        startBtn.disabled = true;
        startBtn.innerHTML = `
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21 12a9 9 0 11-6.219-8.56"/>
            </svg>
            Starting...
        `;
        
        const response = await fetch('/start_scraping', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                keywords: keywords.join(' '),
                places: places
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            isScrapingActive = true;
            statusSection.style.display = 'block';
            resultsSection.style.display = 'none';
            
            // Start polling for status updates
            startStatusPolling();
        } else {
            throw new Error(data.error || 'Failed to start scraping');
        }
        
    } catch (error) {
        console.error('Error starting scraping:', error);
        alert(`Error: ${error.message}`);
        resetForm();
    }
}

// Start polling for status updates
function startStatusPolling() {
    if (scrapingInterval) {
        clearInterval(scrapingInterval);
    }
    
    scrapingInterval = setInterval(async () => {
        try {
            const response = await fetch('/scraping_status');
            const status = await response.json();
            
            updateStatusDisplay(status);
            
            if (!status.active) {
                clearInterval(scrapingInterval);
                scrapingInterval = null;
                isScrapingActive = false;
                
                if (status.stage === 'complete') {
                    showResults(status.results);
                } else if (status.stage === 'error') {
                    alert(`Scraping failed: ${status.message}`);
                }
                
                resetForm();
            }
            
        } catch (error) {
            console.error('Error polling status:', error);
            clearInterval(scrapingInterval);
            scrapingInterval = null;
            isScrapingActive = false;
            resetForm();
        }
    }, 2000); // Poll every 2 seconds
}

// Update status display
function updateStatusDisplay(status) {
    // Update status text and badge
    let statusColor = '#3b82f6';
    let statusDisplayText = 'Processing...';
    
    switch (status.stage) {
        case 'initializing':
            statusDisplayText = 'Initializing...';
            statusColor = '#f59e0b';
            break;
        case 'starting_browser':
            statusDisplayText = 'Starting Browser...';
            statusColor = '#f59e0b';
            break;
        case 'captcha':
            statusDisplayText = 'Waiting for CAPTCHA';
            statusColor = '#ef4444';
            break;
        case 'scraping':
            statusDisplayText = 'Scraping in Progress';
            statusColor = '#3b82f6';
            break;
        case 'complete':
            statusDisplayText = 'Complete';
            statusColor = '#10b981';
            break;
        case 'error':
            statusDisplayText = 'Error';
            statusColor = '#ef4444';
            break;
    }
    
    statusText.textContent = statusDisplayText;
    statusBadge.querySelector('.status-dot').style.backgroundColor = statusColor;
    
    // Update progress
    progressFill.style.width = `${status.progress}%`;
    progressText.textContent = `${status.progress}%`;
    foundCount.textContent = `${status.total_found} leads found`;
    
    // Update message
    statusMessage.textContent = status.message || 'Processing...';
    
    // Update message color based on stage
    statusMessage.style.borderLeftColor = statusColor;
}

// Show results
function showResults(results) {
    resultsSection.style.display = 'block';
    
    // Clear existing results
    resultsTableBody.innerHTML = '';
    
    // Populate results table
    results.forEach((result, index) => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${index + 1}</td>
            <td>${result.domain}</td>
            <td>${result.email || '-'}</td>
            <td><span class="status-active">Active</span></td>
        `;
        resultsTableBody.appendChild(row);
    });
    
    // Scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth' });
}

// Reset form to initial state
function resetForm() {
    startBtn.disabled = false;
    startBtn.innerHTML = `
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polygon points="5,3 19,12 5,21 5,3"/>
        </svg>
        Start Lead Generation
    `;
}

// Handle Excel download
function handleDownloadExcel() {
    window.open('/download_excel', '_blank');
}

// Handle text download
function handleDownloadTxt() {
    window.open('/download_txt', '_blank');
}

// Handle copy to clipboard
async function handleCopyClipboard() {
    try {
        const response = await fetch('/get_results_text');
        const data = await response.json();
        
        if (response.ok) {
            await navigator.clipboard.writeText(data.content);
            
            // Show success feedback
            const originalText = copyClipboard.innerHTML;
            copyClipboard.innerHTML = `
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polyline points="20,6 9,17 4,12"/>
                </svg>
                Copied!
            `;
            copyClipboard.classList.add('success-flash');
            
            setTimeout(() => {
                copyClipboard.innerHTML = originalText;
                copyClipboard.classList.remove('success-flash');
            }, 2000);
            
        } else {
            throw new Error(data.error || 'Failed to get results');
        }
        
    } catch (error) {
        console.error('Error copying to clipboard:', error);
        alert(`Error: ${error.message}`);
    }
}

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (scrapingInterval) {
        clearInterval(scrapingInterval);
    }
});

// Make removeKeyword and removePlace functions globally accessible
window.removeKeyword = removeKeyword;
window.removePlace = removePlace;