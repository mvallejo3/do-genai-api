"""
Decorators for handling API responses and errors.
"""
from functools import wraps
from flask import jsonify


def handle_response(func):
    """
    Decorator to handle standard error responses for API endpoints.
    
    Wraps the route handler and provides consistent error handling:
    - ValueError -> 400 Bad Request
    - RuntimeError -> 500 Internal Server Error
    - Exception -> 500 Internal Server Error
    
    The decorated function should return a dict with the success data.
    The decorator will wrap it in the standard response format.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            return jsonify({
                'status': 'success',
                **result
            }), 200
            
        except ValueError as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 400
            
        except RuntimeError as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500
            
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': f'An unexpected error occurred: {str(e)}'
            }), 500
    
    return wrapper

