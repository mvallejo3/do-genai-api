"""
Health check routes blueprint.
"""
from flask import Blueprint

health_bp = Blueprint('health', __name__)


@health_bp.route('/')
def health_check():
    """Health check endpoint."""
    return {'status': 'ok', 'message': 'DO GenAI API is running'}, 200

