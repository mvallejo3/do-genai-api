"""
Bucket routes blueprint.
"""
from flask import Blueprint, request
from middleware.decorators import handle_response
from services.Spaces import Spaces

buckets_bp = Blueprint('buckets', __name__, url_prefix='/api/buckets')


@buckets_bp.route('', methods=['GET'])
@handle_response
def list_buckets():
    """
    List all buckets in DigitalOcean Spaces.
    
    Returns:
        JSON response with list of all buckets and their metadata
    """
    spaces = Spaces()
    buckets = spaces.list_buckets()
    
    return buckets


@buckets_bp.route('', methods=['POST'])
@handle_response
def create_bucket():
    """
    Create a new bucket in DigitalOcean Spaces.
    
    Request body (JSON):
        name (str, required): Name of the bucket to create (must be globally unique)
        region (str, optional): DigitalOcean region for the bucket (defaults to SPACES_REGION env var or 'tor1')
    
    Returns:
        JSON response confirming bucket creation
    """
    data = request.get_json()
    
    if not data:
        raise ValueError("Request body must be provided")
    
    name = data.get('name')
    region = data.get('region')
    
    # Validate required field
    if not name or not isinstance(name, str) or not name.strip():
        raise ValueError("Bucket name is required and cannot be empty")
    
    # Create Spaces instance with the specified region (or use default)
    # The bucket will be created in the region specified by the Spaces client's endpoint URL
    spaces = Spaces(region=region) if region else Spaces()
    
    # Create the bucket (region is determined by the Spaces client's endpoint URL)
    confirmation = spaces.create_bucket(bucket_name=name, region=region)

    if not confirmation:
        raise RuntimeError("Failed to create bucket in DigitalOcean Spaces - no response received")
    
    return {
        'message': 'Bucket created successfully',
    }


@buckets_bp.route('/<name>', methods=['GET'])
@handle_response
def get_bucket(name):
    """
    Get information about a specific bucket in DigitalOcean Spaces.
    
    Path parameters:
        name (str, required): Name of the bucket to get information for
    
    Returns:
        JSON response with bucket information
    """
    if not name or not isinstance(name, str) or not name.strip():
        raise ValueError("Bucket name cannot be empty")
    
    spaces = Spaces()
    bucket_info = spaces.get_bucket_info(bucket_name=name)
    
    return bucket_info


@buckets_bp.route('/<name>', methods=['DELETE'])
@handle_response
def delete_bucket(name):
    """
    Delete a bucket from DigitalOcean Spaces.
    
    Path parameters:
        name (str, required): Name of the bucket to delete
    
    Returns:
        JSON response confirming bucket deletion
    
    Note:
        The bucket must be empty before it can be deleted.
    """
    if not name or not isinstance(name, str) or not name.strip():
        raise ValueError("Bucket name cannot be empty")
    
    spaces = Spaces()
    spaces.delete_bucket(bucket_name=name)
    
    return {
        'message': 'Bucket deleted successfully',
        'bucket_name': name
    }

