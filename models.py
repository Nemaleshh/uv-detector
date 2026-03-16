from datetime import datetime
from enum import Enum

class VehicleStatus(Enum):
    """Vehicle inspection status"""
    PENDING = "pending"
    PASSED = "passed"
    FAILED = "failed"

# Database models using Flask-SQLAlchemy
class Vehicle:
    """Vehicle record"""
    def __init__(self, win_number, entry_time=None):
        self.win_number = win_number
        self.entry_time = entry_time or datetime.now()
        self.exit_time = None
        self.status = VehicleStatus.PENDING.value
        self.total_leaks = 0
        self.images_captured = 0
    
    def to_dict(self):
        return {
            'win_number': self.win_number,
            'entry_time': self.entry_time.isoformat(),
            'exit_time': self.exit_time.isoformat() if self.exit_time else None,
            'status': self.status,
            'total_leaks': self.total_leaks,
            'images_captured': self.images_captured
        }

class LeakReport:
    """Oil leak detection report"""
    def __init__(self, vehicle_id, image_path, leak_detected, confidence=0.0):
        self.vehicle_id = vehicle_id
        self.image_path = image_path
        self.leak_detected = leak_detected
        self.confidence = confidence
        self.timestamp = datetime.now()
        self.description = ""
    
    def to_dict(self):
        return {
            'vehicle_id': self.vehicle_id,
            'image_path': self.image_path,
            'leak_detected': self.leak_detected,
            'confidence': self.confidence,
            'timestamp': self.timestamp.isoformat(),
            'description': self.description
        }

class Statistics:
    """Dashboard statistics"""
    @staticmethod
    def get_stats(vehicles, reports):
        """Calculate statistics from vehicles and reports"""
        total_vehicles = len(vehicles)
        total_leaks = sum(1 for r in reports if r.leak_detected)
        passed = sum(1 for v in vehicles if v.status == VehicleStatus.PASSED.value)
        failed = sum(1 for v in vehicles if v.status == VehicleStatus.FAILED.value)
        
        pass_rate = (passed / total_vehicles * 100) if total_vehicles > 0 else 0
        
        return {
            'total_vehicles': total_vehicles,
            'total_passed': passed,
            'total_failed': failed,
            'total_leaks': total_leaks,
            'pass_rate': round(pass_rate, 2),
            'leak_percentage': round(total_leaks / total_vehicles * 100, 2) if total_vehicles > 0 else 0
        }
