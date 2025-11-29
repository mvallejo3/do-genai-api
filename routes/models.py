"""
Model routes blueprint.
"""
from flask import Blueprint, request
from middleware.decorators import handle_response
from services.do_api import Models

models_bp = Blueprint('models', __name__, url_prefix='/api/models')


@models_bp.route('', methods=['GET'])
@handle_response
def list_models():
    """
    List available models from DigitalOcean AI.
    
    Query parameters:
        usecases (str, optional): Comma-separated list of use cases to filter by
        public_only (bool, optional): Whether to show only public models (default: True)
    
    Returns:
        JSON response with list of available models
    """
    # Parse usecases query parameter (comma-separated string)
    usecases_param = request.args.get('usecases')
    usecases = ['MODEL_USECASE_AGENT']
    if usecases_param:
        usecases = [uc.strip() for uc in usecases_param.split(',') if uc.strip()]
    
    # Parse public_only query parameter (defaults to True)
    public_only_param = request.args.get('public_only', 'false')
    public_only = public_only_param.lower() in ('true', '1', 'yes')
    
    models_service = Models()
    result = models_service.list_models(usecases=usecases, public_only=public_only)

    return result

