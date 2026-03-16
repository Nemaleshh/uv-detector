# UV Oil Leak Detection System - Backend API

Flask REST API for vehicle inspection and UV oil leak detection.

## Features
- QR code vehicle registration
- Real-time oil leak detection from camera frames
- Automatic report generation with detected images
- Dashboard with vehicle statistics
- CORS-enabled for frontend integration

## Project Structure
```
.
├── app.py                    # Flask application factory
├── config.py                 # Configuration classes
├── detection_engine.py       # OpenCV detection logic
├── models.py                 # Data models
├── routes.py                 # API endpoints
├── requirements.txt          # Python dependencies
├── Dockerfile               # Container image
├── runtime.txt              # Python version for Render
└── uploads/                 # Detected images directory
```

## Installation

### Local Development
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -r requirements.txt

# Run Flask app
export FLASK_ENV=development
python app.py
```

### Local Testing with IPv4 Camera
```bash
# Run the app
python app.py

# App will be available at http://localhost:5000 or http://192.168.x.x:5000
```

## API Endpoints

### Health Check
```
GET /api/health
```

### Register Vehicle (QR Scan)
```
POST /api/scan-qr
Content-Type: application/json

{
  "win_number": "VIN1234567890"
}
```

### Detect Oil Leak
```
POST /api/detect-leak
Content-Type: application/json

{
  "win_number": "VIN1234567890",
  "frame": "base64_encoded_image"
}
```

Response:
```json
{
  "leak_detected": true,
  "status": "UV OIL LEAK DETECTED - NOT OK",
  "image_path": "/uploads/leak_VIN1234567890_20240101_120000.jpg",
  "regions": [
    {
      "x": 100,
      "y": 150,
      "width": 200,
      "height": 150,
      "area": 30000,
      "confidence": 0.85
    }
  ],
  "confidence": 0.85,
  "timestamp": "2024-01-01T12:00:00.000000"
}
```

### Generate Final Report
```
POST /api/generate-report
Content-Type: application/json

{
  "win_number": "VIN1234567890"
}
```

### Get Dashboard Statistics
```
GET /api/dashboard
```

### Get Vehicle History
```
GET /api/vehicle/{win_number}
```

### Delete Vehicle (Testing)
```
DELETE /api/vehicle/{win_number}
```

## Configuration

Edit `config.py` to adjust:
- Detection sensitivity (MIN_CONTOUR_AREA, ASPECT_RATIO_MIN/MAX)
- HSV color range (HSV_LOWER, HSV_UPPER)
- Camera frame size and rate
- Database URL

## Environment Variables
```
FLASK_ENV=development          # development, testing, production
PORT=5000                       # Port to run on
DATABASE_URL=sqlite:///...     # Database URL
SECRET_KEY=your-secret-key     # Flask secret key
```

## Deployment to Render

1. Push code to GitHub
2. Create new Web Service on Render
3. Connect GitHub repository
4. Set environment variables:
   - `FLASK_ENV=production`
   - `SECRET_KEY=your-secret-key`
5. Render will auto-detect Python and build using Dockerfile

## Camera Integration

The frontend sends base64-encoded frames to `/api/detect-leak`:

```python
# Example: Capture and send frame from camera
import cv2
import base64
import requests

cap = cv2.VideoCapture(0)
ret, frame = cap.read()

# Encode frame as base64
_, buffer = cv2.imencode('.jpg', frame)
frame_base64 = base64.b64encode(buffer).decode()

# Send to API
response = requests.post('http://localhost:5000/api/detect-leak', json={
    'win_number': 'VIN123',
    'frame': frame_base64
})
```

## Local Testing Workflow

1. Start API: `python app.py`
2. Register vehicle: `curl -X POST http://localhost:5000/api/scan-qr -H "Content-Type: application/json" -d '{"win_number":"TEST001"}'`
3. Send frames with detection
4. Generate report when done
5. Check dashboard for statistics
