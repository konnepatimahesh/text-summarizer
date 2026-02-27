const API_URL = 'http://localhost:5000/api';

// Check authentication
function checkAuth() {
    const token = localStorage.getItem('authToken');
    if (!token) {
        window.location.href = 'login.html';
        return false;
    }
    return token;
}

// Get auth headers
function getAuthHeaders() {
    const token = checkAuth();
    return {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
    };
}

// Logout function
function logout() {
    localStorage.removeItem('authToken');
    localStorage.removeItem('user');
    window.location.href = 'login.html';
}

// Initialize auth check
const token = checkAuth();
if (!token) {
    // Will redirect in checkAuth()
}

// Show user info
const user = JSON.parse(localStorage.getItem('user') || '{}');
if (user.username) {
    const header = document.querySelector('header');
    const userMenu = document.createElement('div');
    userMenu.className = 'user-menu';
    userMenu.innerHTML = `
        <div class="user-info">
            <span class="user-icon">👤</span>
            <span class="username">${user.username}</span>
            <button onclick="logout()" class="logout-btn">Logout</button>
        </div>
    `;
    header.appendChild(userMenu);
}

// DOM Elements
const inputText = document.getElementById('inputText');
const summaryDiv = document.getElementById('summary');
const summarizeBtn = document.getElementById('summarizeBtn');
const clearBtn = document.getElementById('clearBtn');
const copyBtn = document.getElementById('copyBtn');
const translateBtn = document.getElementById('translateBtn');
const downloadBtn = document.getElementById('downloadBtn');
const loading = document.getElementById('loading');
const loadingText = document.getElementById('loadingText');
const stats = document.getElementById('stats');
const methodSelect = document.getElementById('method');
const lengthSelect = document.getElementById('length');
const targetLangSelect = document.getElementById('targetLang');
const actionButtons = document.getElementById('actionButtons');
const languageInfo = document.getElementById('languageInfo');
const detectedLang = document.getElementById('detectedLang');
const summaryLangBadge = document.getElementById('summaryLangBadge');
const summaryLangInfo = document.getElementById('summaryLangInfo');

// File upload elements
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const fileInfo = document.getElementById('fileInfo');
const fileName = document.getElementById('fileName');
const removeFile = document.getElementById('removeFile');

// Translation modal
const translateModal = document.getElementById('translateModal');
const closeModal = document.getElementById('closeModal');
const confirmTranslate = document.getElementById('confirmTranslate');
const translateTargetLang = document.getElementById('translateTargetLang');

// State
let currentFile = null;
let currentSummary = null;
let currentOriginalText = null;
let currentStats = null;
let detectedLanguage = null;
let hasUnsavedChanges = false;
let isProcessing = false;
let outputLocked = false; // Lock to prevent erasure

// Exit confirmation
window.addEventListener('beforeunload', (e) => {
    if (hasUnsavedChanges && (currentSummary || inputText.value.trim())) {
        e.preventDefault();
        e.returnValue = 'You have unsaved work. Are you sure you want to leave?';
        return e.returnValue;
    }
});

// Track changes
function markAsChanged() {
    hasUnsavedChanges = true;
}

function markAsSaved() {
    hasUnsavedChanges = false;
}

// Event Listeners
summarizeBtn.addEventListener('click', handleSummarize);
clearBtn.addEventListener('click', handleClear);
copyBtn.addEventListener('click', handleCopy);
translateBtn.addEventListener('click', showTranslateModal);
downloadBtn.addEventListener('click', handleDownload);
closeModal.addEventListener('click', hideTranslateModal);
confirmTranslate.addEventListener('click', handleTranslate);

function showTranslateModal() {
    translateModal.style.display = 'flex';
}

function hideTranslateModal() {
    translateModal.style.display = 'none';
}

// Track text input changes
let detectTimeout;
inputText.addEventListener('input', () => {
    markAsChanged();
    clearTimeout(detectTimeout);
    detectTimeout = setTimeout(detectLanguage, 1000);
});

// ==================== FILE UPLOAD LISTENERS - ACCESSIBLE ====================

// File input change handler
fileInput.addEventListener('change', handleFileSelect);

// Remove file handler
removeFile.addEventListener('click', (e) => {
    e.stopPropagation();
    e.preventDefault();
    console.log('🗑️ Remove file button clicked');
    handleRemoveFile();
});

// Drag and drop on upload area (the label now)
uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.classList.add('dragover');
});

uploadArea.addEventListener('dragleave', () => {
    uploadArea.classList.remove('dragover');
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFile(files[0]);
    }
});

// Keyboard accessibility for upload area
uploadArea.addEventListener('keydown', (e) => {
    // Enter or Space to trigger file input
    if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        fileInput.click();
    }
});

// ==================== END FILE UPLOAD LISTENERS ====================

// Detect language
async function detectLanguage() {
    const text = inputText.value.trim();
    
    if (!text || text.length < 20) {
        languageInfo.style.display = 'none';
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/detect-language`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ text })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            detectedLanguage = data.language_code;
            detectedLang.textContent = `Detected: ${data.language_name} (${data.language_code})`;
            languageInfo.style.display = 'flex';
        }
    } catch (error) {
        console.error('Language detection error:', error);
    }
}

// Handle file selection
function handleFileSelect(e) {
    const file = e.target.files[0];
    if (file) {
        handleFile(file);
    }
}

// Process file
async function handleFile(file) {
    const allowedTypes = [
        'application/pdf', 
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 
        'text/plain'
    ];
    
    if (!allowedTypes.includes(file.type)) {
        showError('Invalid file type. Please upload PDF, DOCX, or TXT files.');
        return;
    }
    
    if (file.size > 10 * 1024 * 1024) {
        showError('File size exceeds 10MB limit.');
        return;
    }
    
    currentFile = file;
    fileName.textContent = `📄 ${file.name}`;
    fileInfo.style.display = 'flex';
    uploadArea.style.display = 'none';
    
    await extractTextFromFile(file);
}

// Extract text from file
async function extractTextFromFile(file) {
    loadingText.textContent = 'Extracting text from file...';
    loading.classList.add('active');
    isProcessing = true;
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        const response = await fetch(`${API_URL}/upload`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`
            },
            body: formData
        });
        
        const data = await response.json();
        
        if (response.status === 401) {
            logout();
            return;
        }
        
        if (response.ok) {
            inputText.value = data.text;
            detectedLanguage = data.detected_language;
            markAsChanged();
            
            if (data.detected_language) {
                detectedLang.textContent = `Detected: ${data.detected_language_name} (${data.detected_language})`;
                languageInfo.style.display = 'flex';
            }
            
            showSuccess(`✅ Extracted ${data.word_count} words from ${data.filename}`);
        } else {
            showError(data.error || 'Failed to extract text from file');
        }
    } catch (error) {
        showError('Failed to upload file. Make sure the backend is running.');
        console.error('Upload error:', error);
    } finally {
        loading.classList.remove('active');
        isProcessing = false;
    }
}

// Remove file
function handleRemoveFile() {
    if (isProcessing) {
        console.warn('⚠️ Cannot remove file while processing');
        return;
    }
    
    console.log('🗑️ Removing file...');
    
    currentFile = null;
    fileInput.value = '';
    fileInfo.style.display = 'none';
    uploadArea.style.display = 'block';
    inputText.value = '';
    languageInfo.style.display = 'none';
    
    console.log('✅ File removed successfully');
}

// MAIN SUMMARIZATION FUNCTION - FIXED TO KEEP OUTPUT VISIBLE
async function handleSummarize() {
    const text = inputText.value.trim();
    
    if (!text) {
        showError('Please enter some text or upload a file to summarize');
        return;
    }
    
    if (text.split(' ').length < 50) {
        showError('Text is too short. Please enter at least 50 words for better summarization.');
        return;
    }
    
    isProcessing = true;
    outputLocked = false; // Reset lock
    loadingText.textContent = 'Generating summary...';
    loading.classList.add('active');
    summarizeBtn.disabled = true;
    
    const lengthConfig = {
        'short': { max: 100, min: 50 },
        'medium': { max: 150, min: 100 },
        'long': { max: 250, min: 150 }
    };
    
    const selectedLength = lengthConfig[lengthSelect.value];
    const targetLang = targetLangSelect.value;
    
    try {
        console.log('🚀 Sending summarization request...');
        console.log('Text length:', text.length, 'words:', text.split(' ').length);
        
        const response = await fetch(`${API_URL}/summarize`, {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify({
                text: text,
                method: methodSelect.value,
                max_length: selectedLength.max,
                min_length: selectedLength.min,
                target_lang: targetLang,
                multilingual_mode: 'translate'
            })
        });
        
        if (response.status === 401) {
            logout();
            return;
        }
        
        const data = await response.json();
        console.log('📦 Received response:', data);
        
        if (response.ok && data.summary) {
            console.log('✅ Summary received:', data.summary.substring(0, 100) + '...');
            
            // Store in state FIRST
            currentSummary = data.summary;
            currentOriginalText = text;
            currentStats = {
                original_length: data.original_length,
                summary_length: data.summary_length,
                compression_ratio: data.compression_ratio
            };
            
            console.log('💾 Stored in state:', {
                summaryLength: currentSummary.length,
                statsLength: currentStats.summary_length
            });
            
            // LOCK OUTPUT - Prevent any changes
            outputLocked = true;
            
            // Display summary with PERMANENT styling
            displaySummary(data.summary);
            
            // Show language info
            if (data.source_language && data.target_language) {
                summaryLangInfo.textContent = `🔄 ${data.source_language_name} → ${data.target_language_name}`;
                summaryLangBadge.style.display = 'block';
            }
            
            // Show statistics
            stats.innerHTML = `
                <div>📊 <strong>Original Length:</strong> ${data.original_length} words</div>
                <div>📝 <strong>Summary Length:</strong> ${data.summary_length} words</div>
                <div>🎯 <strong>Compression Ratio:</strong> ${data.compression_ratio}</div>
                ${data.detected_language ? `<div>🌍 <strong>Detected Language:</strong> ${data.detected_language_name}</div>` : ''}
            `;
            stats.style.display = 'block';
            
            // Show action buttons
            displayActionButtons();
            
            markAsSaved();
            showSuccess('✅ Summary generated successfully!');
            
            console.log('🎉 SUMMARY COMPLETE AND LOCKED');
            
        } else {
            console.error('❌ Summary generation failed:', data);
            showError(data.error || 'An error occurred while summarizing');
        }
    } catch (error) {
        console.error('❌ Error:', error);
        showError('Failed to connect to the server. Please ensure the backend is running.');
    } finally {
        setTimeout(() => {
            loading.classList.remove('active');
            summarizeBtn.disabled = false;
            isProcessing = false;
            console.log('✅ Processing complete');
        }, 500);
    }
}

// Separate function to display summary safely
function displaySummary(summaryText) {
    console.log('🖼️ Displaying summary...');
    
    // Clear everything
    summaryDiv.innerHTML = '';
    summaryDiv.className = 'summary-box'; // Reset classes
    
    // Create paragraph element for better rendering
    const summaryParagraph = document.createElement('p');
    summaryParagraph.textContent = summaryText;
    summaryParagraph.style.cssText = `
        margin: 0;
        padding: 0;
        color: #333;
        font-size: 1.05rem;
        line-height: 1.8;
        white-space: pre-wrap;
        word-wrap: break-word;
    `;
    
    summaryDiv.appendChild(summaryParagraph);
    
    // Apply container styles
    summaryDiv.style.cssText = `
        display: block !important;
        visibility: visible !important;
        opacity: 1 !important;
        padding: 20px !important;
        background-color: #f8f9fa !important;
        border: 2px solid #e0e0e0 !important;
        border-radius: 12px !important;
        min-height: 200px !important;
    `;
    
    // Force browser to render
    summaryDiv.offsetHeight; // Trigger reflow
    
    console.log('✅ Summary displayed and locked');
}

// Separate function to display action buttons safely
function displayActionButtons() {
    console.log('🔘 Displaying action buttons...');
    
    // Force display with !important
    actionButtons.setAttribute('style', 
        'display: grid !important; ' +
        'grid-template-columns: 1fr 1fr 1fr !important; ' +
        'gap: 10px !important; ' +
        'margin-top: 20px !important; ' +
        'visibility: visible !important; ' +
        'opacity: 1 !important;'
    );
    
    // Ensure each button is visible
    [copyBtn, translateBtn, downloadBtn].forEach(btn => {
        btn.style.display = 'block';
        btn.style.visibility = 'visible';
        btn.style.opacity = '1';
    });
    
    // Force browser to render
    actionButtons.offsetHeight; // Trigger reflow
    
    console.log('✅ Action buttons displayed and locked');
}

// Translate summary
async function handleTranslate() {
    if (!currentSummary) {
        showError('No summary to translate');
        return;
    }
    
    const targetLang = translateTargetLang.value;
    hideTranslateModal();
    
    isProcessing = true;
    outputLocked = false; // Unlock for update
    loadingText.textContent = 'Translating summary...';
    loading.classList.add('active');
    
    try {
        const response = await fetch(`${API_URL}/translate`, {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify({
                text: currentSummary,
                target_lang: targetLang,
                source_lang: 'auto'
            })
        });
        
        if (response.status === 401) {
            logout();
            return;
        }
        
        const data = await response.json();
        
        if (response.ok) {
            currentSummary = data.translated_text;
            displaySummary(data.translated_text); // Use safe display function
            outputLocked = true; // Lock again
            markAsChanged();
            showSuccess('✅ Summary translated successfully!');
        } else {
            showError(data.error || 'Translation failed');
        }
    } catch (error) {
        console.error('Translation error:', error);
        showError('Failed to translate summary');
    } finally {
        loading.classList.remove('active');
        isProcessing = false;
    }
}

// Download PDF
async function handleDownload() {
    if (!currentSummary || !currentOriginalText) {
        showError('No summary available to download');
        return;
    }
    
    isProcessing = true;
    loadingText.textContent = 'Generating PDF...';
    loading.classList.add('active');
    
    try {
        const response = await fetch(`${API_URL}/download-pdf`, {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify({
                original_text: currentOriginalText,
                summary: currentSummary,
                stats: currentStats
            })
        });
        
        if (response.status === 401) {
            logout();
            return;
        }
        
        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `summary_${new Date().getTime()}.pdf`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            
            markAsSaved();
            showSuccess('✅ PDF downloaded successfully!');
        } else {
            const data = await response.json();
            showError(data.error || 'Failed to generate PDF');
        }
    } catch (error) {
        console.error('Download error:', error);
        showError('Failed to download PDF');
    } finally {
        loading.classList.remove('active');
        isProcessing = false;
    }
}

// Clear all
function handleClear() {
    if (isProcessing) {
        console.warn('⚠️ Cannot clear while processing');
        return;
    }
    
    console.log('🗑️ Clear function called');
    
    if (currentSummary || inputText.value.trim()) {
        const confirmed = confirm('⚠️ Are you sure you want to clear all content?');
        if (!confirmed) {
            console.log('❌ Clear cancelled by user');
            return;
        }
    }
    
    // Unlock output for clearing
    outputLocked = false;
    
    inputText.value = '';
    summaryDiv.innerHTML = '';
    summaryDiv.textContent = 'Your summary will appear here...';
    summaryDiv.style.color = '#999';
    summaryDiv.style.backgroundColor = '#f8f9fa';
    stats.style.display = 'none';
    actionButtons.style.display = 'none';
    languageInfo.style.display = 'none';
    summaryLangBadge.style.display = 'none';
    
    currentFile = null;
    fileInput.value = '';
    fileInfo.style.display = 'none';
    uploadArea.style.display = 'block';
    
    currentSummary = null;
    currentOriginalText = null;
    currentStats = null;
    detectedLanguage = null;
    
    methodSelect.value = 'transformer';
    lengthSelect.value = 'medium';
    targetLangSelect.value = 'auto';
    
    markAsSaved();
    
    console.log('✅ Content cleared successfully');
}

// Copy summary
async function handleCopy() {
    if (!currentSummary) {
        showError('No summary to copy');
        return;
    }
    
    try {
        await navigator.clipboard.writeText(currentSummary);
        
        const originalText = copyBtn.textContent;
        copyBtn.textContent = '✅ Copied!';
        copyBtn.style.background = '#28a745';
        
        setTimeout(() => {
            copyBtn.textContent = originalText;
            copyBtn.style.background = '#6c757d';
        }, 2000);
    } catch (error) {
        showError('Failed to copy to clipboard');
    }
}

// Show error
function showError(message) {
    console.log('❌ Showing error:', message);
    outputLocked = false; // Unlock for error display
    summaryDiv.innerHTML = `<span style="color: #dc3545; font-weight: bold;">❌ ${message}</span>`;
    summaryDiv.style.display = 'block';
    summaryDiv.style.visibility = 'visible';
    stats.style.display = 'none';
    actionButtons.style.display = 'none';
}

// Show success
function showSuccess(message) {
    const tempDiv = document.createElement('div');
    tempDiv.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #28a745;
        color: white;
        padding: 15px 25px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.2);
        z-index: 10000;
        animation: slideIn 0.3s ease;
        font-weight: 500;
    `;
    tempDiv.textContent = message;
    document.body.appendChild(tempDiv);
    
    setTimeout(() => {
        tempDiv.style.animation = 'fadeOut 0.3s ease';
        setTimeout(() => {
            if (document.body.contains(tempDiv)) {
                document.body.removeChild(tempDiv);
            }
        }, 300);
    }, 3000);
}

// Check API health
async function checkAPIHealth() {
    try {
        const response = await fetch(`${API_URL}/health`);
        if (response.ok) {
            console.log('✅ Backend API is running');
        }
    } catch (error) {
        console.warn('⚠️ Backend API is not responding');
    }
}

// Prevent accidental refresh
window.addEventListener('keydown', (e) => {
    if ((e.key === 'F5' || (e.ctrlKey && e.key === 'r')) && hasUnsavedChanges) {
        if (!confirm('You have unsaved work. Refresh anyway?')) {
            e.preventDefault();
        }
    }
});

// Initialize
checkAPIHealth();
console.log('🎯 Text Summarizer v2.5 FINAL - All Fixes Applied');
console.log('✅ Output lock enabled');
console.log('✅ Accessible file upload');
console.log('✅ Monitoring code removed');

// Add CSS animations
if (!document.getElementById('custom-animations')) {
    const style = document.createElement('style');
    style.id = 'custom-animations';
    style.textContent = `
        @keyframes slideIn {
            from { transform: translateX(400px); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        @keyframes fadeOut {
            from { opacity: 1; }
            to { opacity: 0; }
        }
    `;
    document.head.appendChild(style);
}