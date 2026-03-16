from flask import Blueprint, request, jsonify
from datetime import datetime
from detection_engine import OilLeakDetectionEngine
from models import Vehicle, LeakReport, VehicleStatus, Statistics
from config import Config
import cv2
import base64
import numpy as np
import os

# Create blueprint
api = Blueprint('api', __name__, url_prefix='/api')

# In-memory storage (replace with database in production)
vehicles = {}
reports = []
engine = OilLeakDetectionEngine()

@api.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    }), 200

@api.route('/scan-qr', methods=['POST'])
def scan_qr():
    """
    Record vehicle entry via QR code scan
    Request body: { "win_number": "VIN123" }
    """
    try:
        data = request.get_json()
        win_number = data.get('win_number')
        
        if not win_number:
            return jsonify({'error': 'win_number is required'}), 400
        
        # Create vehicle record
        vehicle = Vehicle(win_number)
        vehicles[win_number] = vehicle
        
        return jsonify({
            'message': 'Vehicle registered',
            'vehicle': vehicle.to_dict()
        }), 201
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/detect-leak', methods=['POST'])
def detect_leak():
    """
    Detect oil leak in frame
    Request body: { "win_number": "VIN123", "frame": "base64_encoded_image" }
    """
    try:
        data = request.get_json()
        win_number = data.get('win_number')
        frame_data = data.get('frame')
        
        if not win_number or not frame_data:
            return jsonify({'error': 'win_number and frame are required'}), 400
        
        if win_number not in vehicles:
            return jsonify({'error': 'Vehicle not found'}), 404
        
        # Decode base64 frame
        frame_bytes = base64.b64decode(frame_data)
        nparr = np.frombuffer(frame_bytes, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # Detect leak
        result = engine.detect_leak(frame)
        
        if result['leak_detected']:
            vehicles[win_number].total_leaks += 1
        
        vehicles[win_number].images_captured += 1
        
        # Save frame if leak detected
        image_path = None
        if result['leak_detected']:
            image_path = engine.save_detected_image(
                result['frame'],
                win_number,
                Config.UPLOAD_FOLDER
            )
        
        # Create report
        report = LeakReport(
            win_number,
            image_path,
            result['leak_detected'],
            confidence=max([r['confidence'] for r in result['regions']], default=0.0)
        )
        reports.append(report)
        
        return jsonify({
            'leak_detected': result['leak_detected'],
            'status': result['status'],
            'image_path': image_path,
            'regions': result['regions'],
            'confidence': report.confidence,
            'timestamp': result['timestamp']
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/generate-report', methods=['POST'])
def generate_report():
    """
    Generate final inspection report for vehicle
    Request body: { "win_number": "VIN123" }
    """
    try:
        data = request.get_json()
        win_number = data.get('win_number')
        
        if not win_number:
            return jsonify({'error': 'win_number is required'}), 400
        
        if win_number not in vehicles:
            return jsonify({'error': 'Vehicle not found'}), 404
        
        vehicle = vehicles[win_number]
        vehicle.exit_time = datetime.now()
        
        # Determine status
        vehicle_reports = [r for r in reports if r.vehicle_id == win_number]
        leak_found = any(r.leak_detected for r in vehicle_reports)
        vehicle.status = VehicleStatus.FAILED.value if leak_found else VehicleStatus.PASSED.value
        
        # Generate report
        report_data = {
            'vehicle': vehicle.to_dict(),
            'total_scans': len(vehicle_reports),
            'leaks_detected': sum(1 for r in vehicle_reports if r.leak_detected),
            'details': [r.to_dict() for r in vehicle_reports]
        }
        
        return jsonify(report_data), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/dashboard', methods=['GET'])
def dashboard():
    """
    Get dashboard statistics
    """
    try:
        stats = Statistics.get_stats(list(vehicles.values()), reports)
        
        return jsonify({
            'statistics': stats,
            'recent_vehicles': [v.to_dict() for v in list(vehicles.values())[-10:]],
            'timestamp': datetime.now().isoformat()
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/vehicle/<win_number>', methods=['GET'])
def get_vehicle(win_number):
    """
    Get vehicle history and reports
    """
    try:
        if win_number not in vehicles:
            return jsonify({'error': 'Vehicle not found'}), 404
        
        vehicle = vehicles[win_number]
        vehicle_reports = [r.to_dict() for r in reports if r.vehicle_id == win_number]
        
        return jsonify({
            'vehicle': vehicle.to_dict(),
            'reports': vehicle_reports
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/vehicle/<win_number>', methods=['DELETE'])
def delete_vehicle(win_number):
    """
    Delete vehicle record (for testing only)
    """
    try:
        if win_number in vehicles:
            del vehicles[win_number]
            global reports
            reports = [r for r in reports if r.vehicle_id != win_number]
            return jsonify({'message': 'Vehicle deleted'}), 200
        
        return jsonify({'error': 'Vehicle not found'}), 404
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
