"""
IP Camera Streaming to Backend
Connects to IP camera (phone/action cam) and streams frames to Flask backend
"""

import cv2
import requests
import base64
import argparse
from datetime import datetime

class IPCameraStreamer:
    def __init__(self, camera_url, backend_url, vehicle_id):
        """
        Args:
            camera_url: IP camera URL (e.g., http://192.168.1.100:8080/video)
            backend_url: Flask backend URL (e.g., http://localhost:5000)
            vehicle_id: Vehicle WIN number for registration
        """
        self.camera_url = camera_url
        self.backend_url = backend_url
        self.vehicle_id = vehicle_id
        self.cap = None
        self.frame_count = 0
        
    def connect_camera(self):
        """Connect to IP camera stream"""
        print(f"[*] Connecting to IP camera: {self.camera_url}")
        
        self.cap = cv2.VideoCapture(self.camera_url, cv2.CAP_FFMPEG)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        
        if not self.cap.isOpened():
            print("[ERROR] Cannot open IP camera stream")
            return False
        
        print("[✓] Camera connected successfully!")
        return True
    
    def register_vehicle(self):
        """Register vehicle with backend"""
        print(f"[*] Registering vehicle: {self.vehicle_id}")
        
        try:
            response = requests.post(
                f"{self.backend_url}/api/scan-qr",
                json={"win_number": self.vehicle_id},
                timeout=5
            )
            
            if response.status_code == 201:
                print(f"[✓] Vehicle registered: {self.vehicle_id}")
                return True
            else:
                print(f"[ERROR] Registration failed: {response.json()}")
                return False
                
        except Exception as e:
            print(f"[ERROR] Connection failed: {e}")
            return False
    
    def send_frame_to_backend(self, frame):
        """
        Capture frame and send to backend for detection
        Args:
            frame: OpenCV frame
        Returns:
            Detection result
        """
        try:
            # Encode frame to base64
            _, buffer = cv2.imencode('.jpg', frame)
            frame_base64 = base64.b64encode(buffer).decode('utf-8')
            
            # Send to backend
            response = requests.post(
                f"{self.backend_url}/api/detect-leak",
                json={
                    "win_number": self.vehicle_id,
                    "frame": frame_base64
                },
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                return result
            else:
                print(f"[ERROR] Detection failed: {response.json()}")
                return None
                
        except Exception as e:
            print(f"[ERROR] API error: {e}")
            return None
    
    def stream_and_detect(self, capture_interval=5):
        """
        Stream from IP camera and send frames to backend
        Args:
            capture_interval: Send frame to backend every N frames
        """
        if not self.connect_camera():
            return
        
        if not self.register_vehicle():
            return
        
        print("\n" + "="*50)
        print("  Starting IP Camera Stream Detection")
        print("="*50)
        print(f"Camera URL: {self.camera_url}")
        print(f"Backend URL: {self.backend_url}")
        print(f"Vehicle ID: {self.vehicle_id}")
        print(f"Send frame every {capture_interval} frames")
        print("\nPress 'q' to quit, 'c' to capture frame")
        print("="*50 + "\n")
        
        try:
            while True:
                ret, frame = self.cap.read()
                
                if not ret:
                    print("[ERROR] Failed to read frame. Reconnecting...")
                    self.connect_camera()
                    continue
                
                # Resize frame
                frame = cv2.resize(frame, (640, 480))
                
                self.frame_count += 1
                
                # Send frame to backend every N frames
                if self.frame_count % capture_interval == 0:
                    print(f"\n[Frame {self.frame_count}] Sending to backend for detection...")
                    
                    result = self.send_frame_to_backend(frame)
                    
                    if result:
                        leak_detected = result.get('leak_detected', False)
                        status = result.get('status', '')
                        confidence = result.get('confidence', 0)
                        
                        print(f"[Result] {status}")
                        print(f"[Confidence] {confidence * 100:.1f}%")
                        print(f"[Regions] {len(result.get('regions', []))} detected")
                        
                        # Draw on frame
                        color = (0, 0, 255) if leak_detected else (0, 255, 0)
                        cv2.putText(frame, status, (20, 40),
                                  cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
                
                # Display frame locally
                cv2.imshow("IP Camera Stream - UV Oil Detection", frame)
                
                # Key controls
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    print("\n[*] Stopping stream...")
                    break
                elif key == ord('c'):
                    # Manual capture
                    result = self.send_frame_to_backend(frame)
                    if result:
                        print(f"[Manual Capture] {result.get('status', '')}")
        
        except KeyboardInterrupt:
            print("\n[*] Interrupted by user")
        
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources"""
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
        print("[✓] Stream closed")

def main():
    parser = argparse.ArgumentParser(description='IP Camera Streaming to Oil Detection Backend')
    
    parser.add_argument('--camera-url', 
                       required=True,
                       help='IP camera URL (e.g., http://192.168.1.100:8080/video)')
    
    parser.add_argument('--backend-url',
                       default='http://localhost:5000',
                       help='Backend API URL (default: http://localhost:5000)')
    
    parser.add_argument('--vehicle-id',
                       required=True,
                       help='Vehicle WIN number (e.g., VIN123)')
    
    parser.add_argument('--interval',
                       type=int,
                       default=5,
                       help='Send frame to backend every N frames (default: 5)')
    
    args = parser.parse_args()
    
    streamer = IPCameraStreamer(
        camera_url=args.camera_url,
        backend_url=args.backend_url,
        vehicle_id=args.vehicle_id
    )
    
    streamer.stream_and_detect(capture_interval=args.interval)

if __name__ == '__main__':
    main()
