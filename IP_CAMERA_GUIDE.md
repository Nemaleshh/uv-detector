# IP Camera Streaming Setup Guide

## Overview
Stream video from your phone/camera to the detection backend via IPv4.

## Two Methods

### Method 1: Python Streaming Script (Recommended)
Best for continuous monitoring and reliability

**Step 1: Start Backend**
```bash
cd antigravity-python
python app.py
```

**Step 2: Get Phone IP Camera URL**
- iPhone: Use "Codeshot" or similar app
- Android: Use "IP Webcam" app (free)
  - Install from Google Play
  - Start server (usually http://192.168.x.x:8080/video)
  - Note the URL

**Step 3: Run Streaming Script**
```bash
python ip_camera_stream.py \
  --camera-url "http://192.168.1.100:8080/video" \
  --vehicle-id "VIN123" \
  --backend-url "http://localhost:5000" \
  --interval 5
```

**Parameters:**
- `--camera-url`: IP camera stream URL
- `--vehicle-id`: Vehicle identification number
- `--backend-url`: Flask API URL (default: localhost:5000)
- `--interval`: Send frame every N frames (default: 5)

**Controls:**
- Press `q` to quit
- Press `c` to manually capture frame

**Example Output:**
```
==================================================
  Starting IP Camera Stream Detection
==================================================
Camera URL: http://192.168.1.100:8080/video
Backend URL: http://localhost:5000
Vehicle ID: VIN123
Send frame every 5 frames
==================================================

[Frame 5] Sending to backend for detection...
[Result] NO OIL LEAK - OK
[Confidence] 0.0%
[Regions] 0 detected
```

---

### Method 2: Web UI (Browser)
Use the frontend web interface

**Step 1: Open Frontend**
```
http://localhost:8000
```
(or your machine IP for phone access)

**Step 2: Fill in Details**
1. Enter Vehicle ID
2. Click "Register" in QR Scanner tab
3. Switch to "Detection" tab

**Step 3: Enter IP Camera URL**
- In "Detection" tab
- Paste camera URL: `http://192.168.x.x:8080/video`
- Click "Test Connection"

**Step 4: Start Streaming**
- Click "Start Camera"
- Canvas will show live feed
- Click "Capture Frame" to analyze
- Results display instantly

---

## Finding Your Phone's IP Camera URL

### Android - IP Webcam App
1. Install "IP Webcam" from Google Play Store
2. Open app → Allow permissions
3. Tap "Start server"
4. URL appears: `http://192.168.x.x:8080/video`

### iPhone - Using Codeshot or Streaming App
1. Install streaming app (or use built-in screen mirroring)
2. Enable video streaming
3. Get URL from app (usually shows on screen)

### Network Requirements
- Phone and computer on **same WiFi network**
- Not blocked by firewall
- IPv4 address visible (usually 192.168.x.x or 10.0.x.x)

---

## Troubleshooting

**"Cannot open IP camera stream"**
- Check camera URL is correct
- Test in browser: `http://camera-url` should show video
- Check firewall allows connection
- Restart camera app

**"Cannot connect to backend"**
- Ensure Flask is running: `python app.py`
- Check backend URL is correct
- If using phone, use computer's IP: `http://192.168.x.x:5000`

**"Connection timeout"**
- Check WiFi connection
- Verify phone and computer on same network
- Try ping: `ping 192.168.x.x`

**"CORS error in browser"**
- IP camera doesn't support CORS
- Use Python script instead (Method 1)
- Or disable CORS in browser (development only)

---

## Performance Tips

**Frame Rate Adjustment**
```bash
# Slower (less CPU usage)
python ip_camera_stream.py ... --interval 10

# Faster (more CPU usage)
python ip_camera_stream.py ... --interval 2
```

**Resolution**
- Default: 640x480
- Edit `detection_engine.py` to change

**Network**
- Use 5GHz WiFi for faster streaming
- Bring devices closer to router
- Minimize background apps

---

## Workflow Example

```bash
# Terminal 1: Backend
cd C:\...\antigravity-python
python app.py

# Terminal 2: IP Camera Stream
python ip_camera_stream.py \
  --camera-url "http://192.168.1.105:8080/video" \
  --vehicle-id "CAR001" \
  --interval 3

# Output:
# [*] Connecting to IP camera: http://192.168.1.105:8080/video
# [✓] Camera connected successfully!
# [*] Registering vehicle: CAR001
# [✓] Vehicle registered: CAR001
# 
# [Frame 3] Sending to backend for detection...
# [Result] NO OIL LEAK - OK
# [Confidence] 0.0%
# [Regions] 0 detected
```

---

## API Flow

```
Phone IP Camera
       ↓
IP Camera Stream (URL exposed via app)
       ↓
Python Script / Web UI
       ↓
Capture Frame → Convert to Base64
       ↓
POST to /api/detect-leak
       ↓
Flask Backend (OpenCV Processing)
       ↓
Detection Result (JSON)
       ↓
Display to User
```

---

## Quick Start Command

```bash
python ip_camera_stream.py --camera-url "http://192.168.1.100:8080/video" --vehicle-id "VIN001"
```

Replace `192.168.1.100` with your phone's actual IP address!
