"""
Database routes blueprint.
"""
from flask import Blueprint
from middleware.decorators import handle_response
from services.do_api import Databases

databases_bp = Blueprint('databases', __name__, url_prefix='/api/opensearch-databases')


@databases_bp.route('', methods=['GET'])
@handle_response
def list_opensearch_databases():
    """
    List all OpenSearch databases from DigitalOcean.
    
    Returns:
        JSON response with list of all OpenSearch databases and their metadata
    """
    databases_service = Databases()
    databases = databases_service.list_opensearch_databases()
    
    return databases

