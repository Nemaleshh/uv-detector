import cv2
import numpy as np
from datetime import datetime
import os
from config import Config

class OilLeakDetectionEngine:
    """Engine for detecting UV fluorescent oil leaks"""
    
    def __init__(self, config=None):
        self.config = config or Config()
        self.lower_hsv = np.array(self.config.HSV_LOWER)
        self.upper_hsv = np.array(self.config.HSV_UPPER)
        self.kernel = np.ones((5, 5), np.uint8)
        
    def detect_leak(self, frame):
        """
        Detect oil leak in a frame
        Args:
            frame: OpenCV frame (BGR format)
        Returns:
            dict with detection results
        """
        if frame is None:
            return {'leak_detected': False, 'error': 'Invalid frame'}
        
        # Resize frame
        frame = cv2.resize(frame, (self.config.FRAME_WIDTH, self.config.FRAME_HEIGHT))
        
        # Convert to HSV
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # Create mask for fluorescent oil
        oil_mask = cv2.inRange(hsv, self.lower_hsv, self.upper_hsv)
        
        # Morphological operations
        oil_mask = cv2.morphologyEx(oil_mask, cv2.MORPH_CLOSE, self.kernel, iterations=2)
        oil_mask = cv2.morphologyEx(oil_mask, cv2.MORPH_OPEN, self.kernel, iterations=1)
        
        # Find contours
        contours, _ = cv2.findContours(oil_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        leak_detected = False
        detected_regions = []
        
        for cnt in contours:
            area = cv2.contourArea(cnt)
            
            # Filter by minimum area
            if area < self.config.MIN_CONTOUR_AREA:
                continue
            
            x, y, w, h = cv2.boundingRect(cnt)
            aspect = w / float(h) if h > 0 else 0
            
            # Filter by aspect ratio
            if aspect < self.config.ASPECT_RATIO_MIN or aspect > self.config.ASPECT_RATIO_MAX:
                continue
            
            leak_detected = True
            detected_regions.append({
                'x': x,
                'y': y,
                'width': w,
                'height': h,
                'area': area,
                'confidence': min(1.0, area / 5000.0)  # Simple confidence metric
            })
            
            # Draw rectangle on frame
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
        
        # Add status text
        status = "UV OIL LEAK DETECTED - NOT OK" if leak_detected else "NO OIL LEAK - OK"
        color = (0, 0, 255) if leak_detected else (0, 255, 0)
        cv2.putText(frame, status, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
        
        return {
            'leak_detected': leak_detected,
            'status': status,
            'frame': frame,
            'mask': oil_mask,
            'regions': detected_regions,
            'timestamp': datetime.now().isoformat()
        }
    
    def save_detected_image(self, frame, vehicle_id, upload_folder):
        """
        Save detected leak image
        Args:
            frame: OpenCV frame with annotations
            vehicle_id: Vehicle identification number
            upload_folder: Path to save images
        Returns:
            Path to saved image
        """
        os.makedirs(upload_folder, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"leak_{vehicle_id}_{timestamp}.jpg"
        filepath = os.path.join(upload_folder, filename)
        
        cv2.imwrite(filepath, frame)
        return filepath
