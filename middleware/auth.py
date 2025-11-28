"""
Authentication middleware for API requests.
"""
import os
from flask import jsonify, request


def require_auth():
    """
    Middleware to require Bearer token authentication for all requests.
    
    Checks for Authorization header with format: Bearer <token>
    Returns 401 Unauthorized if token is missing or invalid.
    """
    API_BEARER_TOKEN = os.getenv('API_BEARER_TOKEN')

    if not API_BEARER_TOKEN:
        return jsonify({
            'status': 'error',
            'message': 'API_BEARER_TOKEN environment variable is required'
        }), 500

    # Skip authentication for OPTIONS requests (CORS preflight)
    if request.method == 'OPTIONS':
        return None
    
    auth_header = request.headers.get('Authorization')
    
    if not auth_header:
        return jsonify({
            'status': 'error',
            'message': 'Authorization header is required'
        }), 401
    
    # Check if header starts with "Bearer "
    if not auth_header.startswith('Bearer '):
        return jsonify({
            'status': 'error',
            'message': 'Authorization header must start with "Bearer "'
        }), 401
    
    # Extract token from header
    token = auth_header[7:]  # Remove "Bearer " prefix
    
    # Validate token matches API_BEARER_TOKEN
    if token != API_BEARER_TOKEN:
        return jsonify({
            'status': 'error',
            'message': 'Invalid authentication token'
        }), 401
    
    return None

