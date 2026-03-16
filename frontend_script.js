// API Configuration
const API_BASE_URL = 'http://localhost:5000';
// Change to your IP: 'http://192.168.x.x:5000'

let currentVehicleId = null;
let videoStream = null;
let canvas = null;
let canvasContext = null;

// Check API Health on page load
window.addEventListener('load', () => {
    checkAPIHealth();
    showPage('home');
});

// ==================== Page Navigation ====================
function showPage(pageName) {
    // Hide all pages
    document.querySelectorAll('.page').forEach(page => {
        page.classList.remove('active');
    });
    
    // Show selected page
    document.getElementById(pageName).classList.add('active');
    
    // Update active nav link
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
    });
    event?.target?.classList.add('active');
    
    // Load dashboard if dashboard page
    if (pageName === 'dashboard') {
        refreshDashboard();
    }
}

// ==================== API Health Check ====================
async function checkAPIHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/health`);
        const data = await response.json();
        document.getElementById('api-status').innerHTML = 
            `<span style="color: #2EC4B6;"><i class="fas fa-check-circle"></i> API Status: Connected</span>`;
    } catch (error) {
        document.getElementById('api-status').innerHTML = 
            `<span style="color: #FF006E;"><i class="fas fa-exclamation-circle"></i> API Status: Offline - Check backend</span>`;
        console.error('API Health Check Failed:', error);
    }
}

// ==================== QR Scanner Functions ====================
async function registerVehicle() {
    const vehicleId = document.getElementById('vehicleId').value.trim();
    
    if (!vehicleId) {
        showAlert('scanner', 'Please enter a vehicle ID', 'danger');
        return;
    }
    
    showLoader('scanner', true);
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/scan-qr`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ win_number: vehicleId })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            currentVehicleId = vehicleId;
            document.getElementById('detection-vehicle-id').value = vehicleId;
            
            document.getElementById('qr-vehicle-id').innerText = vehicleId;
            document.getElementById('qr-result').classList.add('show');
            
            showAlert('scanner', `✓ Vehicle ${vehicleId} registered successfully!`, 'success');
        } else {
            showAlert('scanner', data.error || 'Registration failed', 'danger');
        }
    } catch (error) {
        showAlert('scanner', `Error: ${error.message}`, 'danger');
    } finally {
        showLoader('scanner', false);
    }
}

// ==================== Detection Functions ====================
async function startCamera() {
    canvas = document.getElementById('videoCanvas');
    canvasContext = canvas.getContext('2d');
    
    try {
        videoStream = await navigator.mediaDevices.getUserMedia({ 
            video: { facingMode: 'environment' } 
        });
        
        const video = document.createElement('video');
        video.srcObject = videoStream;
        video.play();
        
        // Draw video to canvas continuously
        function drawVideo() {
            if (!videoStream) return;
            
            canvasContext.drawImage(video, 0, 0, canvas.width, canvas.height);
            requestAnimationFrame(drawVideo);
        }
        
        video.onloadedmetadata = () => {
            drawVideo();
            showAlert('detection', '✓ Camera started', 'success');
        };
        
    } catch (error) {
        showAlert('detection', `Camera error: ${error.message}`, 'danger');
    }
}

function stopCamera() {
    if (videoStream) {
        videoStream.getTracks().forEach(track => track.stop());
        videoStream = null;
        
        // Clear canvas
        if (canvas && canvasContext) {
            canvasContext.fillStyle = '#000';
            canvasContext.fillRect(0, 0, canvas.width, canvas.height);
        }
        
        showAlert('detection', 'Camera stopped', 'success');
    }
}

async function captureFrame() {
    const vehicleId = document.getElementById('detection-vehicle-id').value.trim();
    
    if (!vehicleId) {
        showAlert('detection', 'Please enter vehicle ID', 'danger');
        return;
    }
    
    if (!canvas) {
        showAlert('detection', 'Start camera first', 'danger');
        return;
    }
    
    showLoader('detection', true);
    
    try {
        // Get canvas data as base64
        const frameData = canvas.toDataURL('image/jpeg').split(',')[1];
        
        const response = await fetch(`${API_BASE_URL}/api/detect-leak`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                win_number: vehicleId,
                frame: frameData
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            displayDetectionResult(data);
        } else {
            showAlert('detection', data.error || 'Detection failed', 'danger');
        }
    } catch (error) {
        showAlert('detection', `Error: ${error.message}`, 'danger');
    } finally {
        showLoader('detection', false);
    }
}

function displayDetectionResult(data) {
    const resultDiv = document.getElementById('detection-result');
    const contentDiv = document.getElementById('result-content');
    
    let html = `
        <div class="alert-custom ${data.leak_detected ? 'danger' : 'success'}">
            <h5>${data.leak_detected ? '⚠️ LEAK DETECTED' : '✓ NO LEAK'}</h5>
            <p><strong>Status:</strong> ${data.status}</p>
            <p><strong>Confidence:</strong> ${(data.confidence * 100).toFixed(1)}%</p>
            <p><strong>Regions Found:</strong> ${data.regions.length}</p>
    `;
    
    if (data.regions.length > 0) {
        html += '<p><strong>Detection Details:</strong></p><ul>';
        data.regions.forEach((region, i) => {
            html += `<li>Region ${i+1}: Area ${region.area}px, Confidence ${(region.confidence * 100).toFixed(1)}%</li>`;
        });
        html += '</ul>';
    }
    
    if (data.image_path) {
        html += `<p><strong>Image Saved:</strong> ${data.image_path}</p>`;
    }
    
    html += `<p><small style="color: #888;">${new Date(data.timestamp).toLocaleTimeString()}</small></p></div>`;
    
    contentDiv.innerHTML = html;
    resultDiv.style.display = 'block';
    
    showAlert('detection', data.leak_detected ? 'Leak detected!' : 'No leak found', 
              data.leak_detected ? 'danger' : 'success');
}

async function generateReport() {
    const vehicleId = document.getElementById('detection-vehicle-id').value.trim();
    
    if (!vehicleId) {
        showAlert('detection', 'Please enter vehicle ID', 'danger');
        return;
    }
    
    showLoader('detection', true);
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/generate-report`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ win_number: vehicleId })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            displayReport(data);
            showAlert('detection', 'Report generated successfully!', 'success');
        } else {
            showAlert('detection', data.error || 'Report generation failed', 'danger');
        }
    } catch (error) {
        showAlert('detection', `Error: ${error.message}`, 'danger');
    } finally {
        showLoader('detection', false);
    }
}

function displayReport(reportData) {
    const resultDiv = document.getElementById('detection-result');
    const contentDiv = document.getElementById('result-content');
    
    const vehicle = reportData.vehicle;
    const status = vehicle.status;
    const details = reportData.details;
    
    let html = `
        <div class="report-item ${status}">
            <h5>Inspection Report</h5>
            <p><strong>Vehicle:</strong> ${vehicle.win_number}</p>
            <p><strong>Status:</strong> <span class="badge badge-${status === 'passed' ? 'success' : 'danger'}">${status.toUpperCase()}</span></p>
            <p><strong>Entry Time:</strong> ${new Date(vehicle.entry_time).toLocaleString()}</p>
            <p><strong>Exit Time:</strong> ${vehicle.exit_time ? new Date(vehicle.exit_time).toLocaleString() : 'N/A'}</p>
            <p><strong>Total Scans:</strong> ${reportData.total_scans}</p>
            <p><strong>Leaks Detected:</strong> ${reportData.leaks_detected}</p>
    `;
    
    if (details.length > 0) {
        html += '<p><strong>Scan Details:</strong></p><ul>';
        details.forEach((detail, i) => {
            const leakStatus = detail.leak_detected ? '⚠️ Leak' : '✓ OK';
            html += `<li>${leakStatus} - Confidence: ${(detail.confidence * 100).toFixed(1)}%</li>`;
        });
        html += '</ul>';
    }
    
    html += '</div>';
    
    contentDiv.innerHTML = html;
    resultDiv.style.display = 'block';
}

// ==================== Dashboard Functions ====================
async function refreshDashboard() {
    const loader = document.getElementById('dashboard-loader');
    const content = document.getElementById('dashboard-content');
    
    loader.style.display = 'block';
    content.style.display = 'none';
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/dashboard`);
        const data = await response.json();
        
        if (response.ok) {
            const stats = data.statistics;
            
            document.getElementById('total-vehicles').innerText = stats.total_vehicles;
            document.getElementById('total-passed').innerText = stats.total_passed;
            document.getElementById('total-failed').innerText = stats.total_failed;
            document.getElementById('pass-rate').innerText = stats.pass_rate + '%';
            document.getElementById('total-leaks').innerText = stats.total_leaks;
            document.getElementById('leak-percentage').innerText = stats.leak_percentage + '%';
            
            content.style.display = 'block';
        } else {
            showAlert('dashboard', 'Failed to load dashboard', 'danger');
        }
    } catch (error) {
        showAlert('dashboard', `Error: ${error.message}`, 'danger');
    } finally {
        loader.style.display = 'none';
    }
}

// ==================== UI Helpers ====================
function showAlert(pageId, message, type = 'info') {
    const alertDiv = document.getElementById(`${pageId}-alert`);
    alertDiv.className = `alert-custom ${type}`;
    alertDiv.innerHTML = message;
    alertDiv.style.display = 'block';
    
    // Auto-hide success alerts
    if (type === 'success') {
        setTimeout(() => {
            alertDiv.style.display = 'none';
        }, 3000);
    }
}

function showLoader(pageId, show = true) {
    const loader = document.getElementById(`${pageId}-loader`);
    loader.style.display = show ? 'block' : 'none';
}
