"""
Main application entry point for DO GenAI API.
"""
import os
import tempfile
from pathlib import Path
from services.do_genai import DigitalOceanGenAI
# from typing import Any

# Add the project root to Python path so imports work correctly
# This is needed when running via uWSGI or other WSGI servers
# project_root = Path(__file__).parent.absolute()
# if str(project_root) not in sys.path:
#     sys.path.insert(0, str(project_root))

from functools import wraps
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from services.Spaces import Spaces

# Load environment variables
load_dotenv()

# API Bearer Token for authentication
API_BEARER_TOKEN = os.getenv('API_BEARER_TOKEN')

def require_auth():
    """
    Middleware to require Bearer token authentication for all requests.
    
    Checks for Authorization header with format: Bearer <token>
    Returns 401 Unauthorized if token is missing or invalid.
    """

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


def create_app() -> Flask:
    """
    Application factory pattern for creating Flask app instances.
    
    Returns:
        Flask: Configured Flask application instance
    """

    if not API_BEARER_TOKEN:
        raise ValueError("API_BEARER_TOKEN environment variable is required")

    app = Flask(__name__)
    
    # Load configuration from environment variables
    app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Register authentication middleware - requires Bearer token for all requests
    app.before_request(require_auth)
    
    # Register blueprints/routes here as they are created
    # Example: app.register_blueprint(api_bp)
    
    @app.route('/')
    def health_check():
        """Health check endpoint."""
        return {'status': 'ok', 'message': 'DO GenAI API is running'}, 200

    @app.route('/api/files', methods=['GET'])
    @handle_response
    def list_files():
        """
        List files in the knowledge base bucket.
        
        Query parameters:
            prefix (str, optional): Prefix to filter objects by (e.g., folder path)
            max_keys (int, optional): Maximum number of keys to return
        
        Returns:
            JSON response with list of files and their metadata
        """
        prefix = request.args.get('prefix', '')
        max_keys = request.args.get('max_keys', type=int)
        
        kb = Spaces()
        files = kb.list_files(prefix=prefix, max_keys=max_keys)
        
        return {
            'files': files,
            'count': len(files)
        }
    
    @app.route('/api/files', methods=['POST'])
    @handle_response
    def upload_file():
        """
        Upload one or more files to the knowledge base bucket.
        
        Request:
            multipart/form-data with:
                file (file, required): One or more files to upload (can be multiple files with same field name)
            Query parameters:
                folder (str, optional): Folder/path prefix in the bucket (default: '')
        
        Returns:
            JSON response with upload details for all files including their keys
        """
        # Get all files from request (supports single or multiple files)
        files = request.files.getlist('file')
        
        # Check if any files were provided
        if not files or len(files) == 0:
            raise ValueError("No files provided. Please include at least one 'file' field in the request.")
        
        # Filter out empty file entries
        valid_files = [f for f in files if f.filename and f.filename.strip()]
        
        if not valid_files:
            raise ValueError("No valid files selected. Please provide at least one file with a filename.")
        
        # Get optional folder parameter
        folder = request.args.get('folder', '')
        
        # Initialize KnowledgeBase
        kb = Spaces()
        
        # Track temporary files for cleanup
        temp_paths = []
        results = []
        
        try:
            # Process each file
            for file in valid_files:
                temp_file = None
                temp_path = None
                
                try:
                    # Save uploaded file to temporary location
                    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename or '').suffix)
                    temp_path = temp_file.name
                    temp_paths.append(temp_path)
                    file.save(temp_path)
                    temp_file.close()
                    
                    # Upload to Spaces using KnowledgeBase
                    key = kb.upload_file(
                        file_path=temp_path,
                        folder=folder,
                        object_name=file.filename
                    )
                    
                    results.append({
                        'filename': file.filename,
                        'key': key,
                        'success': True,
                        'error': None
                    })
                    
                except Exception as e:
                    # Track failed uploads but continue with other files
                    results.append({
                        'filename': file.filename,
                        'key': None,
                        'success': False,
                        'error': str(e)
                    })
            
            # Determine overall success message
            successful = sum(1 for r in results if r['success'])
            total = len(results)
            
            if successful == total:
                message = f'All {total} file(s) uploaded successfully'
            elif successful > 0:
                message = f'{successful} of {total} file(s) uploaded successfully'
            else:
                message = 'No files were uploaded successfully'
            
            return {
                'message': message,
                'results': results,
                'successful': successful,
                'failed': total - successful,
                'total': total,
                'folder': folder if folder else None
            }
            
        finally:
            # Clean up all temporary files
            for temp_path in temp_paths:
                if temp_path and os.path.exists(temp_path):
                    try:
                        os.unlink(temp_path)
                    except Exception:
                        pass  # Ignore errors during cleanup
    
    @app.route('/api/files', methods=['DELETE'])
    @handle_response
    def delete_file():
        """
        Delete a file from the knowledge base bucket.
        
        Query parameters:
            key (str, required): The key/path of the file to delete in Spaces
        
        Returns:
            JSON response confirming deletion
        """
        key = request.args.get('key')
        
        if not key:
            raise ValueError("Query parameter 'key' is required")
        
        if not isinstance(key, str) or not key.strip():
            raise ValueError("Key cannot be empty")
        
        kb = Spaces()
        kb.delete_file(key)
        
        return {
            'message': 'File deleted successfully',
            'key': key
        }
    
    @app.route('/api/knowledgebase', methods=['POST'])
    @handle_response
    def create_knowledge_base():
        """
        Create a new knowledge base.
        
        Request body (JSON):
            name (str, required): Name of the knowledge base
            description (str, optional): Description of the knowledge base
        
        Returns:
            JSON response with the created knowledge base details
        """
        data = request.get_json()
        
        if not data:
            raise ValueError("Request body must be provided")
        
        name = data.get('name')
        description = data.get('description', '')
        
        # Validate required field
        if not name or not isinstance(name, str) or not name.strip():
            raise ValueError("Knowledge base name is required and cannot be empty")
        
        do_genai = DigitalOceanGenAI()
        result = do_genai.create_knowledge_base(
            name=name,
            description=description if description else ''
            # Set default embedding model
        )
        
        if not result:
            raise RuntimeError("Failed to create knowledge base in DigitalOcean - no response received")
        
        return result
    
    @app.route('/api/knowledgebase/reindex', methods=['POST'])
    @handle_response
    def reindex_knowledgebase():
        """
        Trigger a re-indexing job for the knowledge base.
        
        Request body (JSON):
            knowledge_base_uuid (str, required): UUID of the knowledge base to re-index
            data_source_uuids (list[str], optional): List of data source UUIDs to re-index.
                                                    If not provided, all data sources will be re-indexed.
        
        Returns:
            JSON response with indexing job details from DigitalOcean API
        """
        data = request.get_json()
        
        if not data or 'knowledge_base_uuid' not in data:
            raise ValueError("Request body must include a 'knowledge_base_uuid' field")
        
        knowledge_base_uuid = data['knowledge_base_uuid']
        data_source_uuids = data.get('data_source_uuids')
        
        if not knowledge_base_uuid or not isinstance(knowledge_base_uuid, str) or not knowledge_base_uuid.strip():
            raise ValueError("knowledge_base_uuid cannot be empty")
        
        # Validate data_source_uuids if provided
        if data_source_uuids is not None:
            if not isinstance(data_source_uuids, list):
                raise ValueError("data_source_uuids must be a list")
            if not all(isinstance(uuid, str) and uuid.strip() for uuid in data_source_uuids):
                raise ValueError("All items in data_source_uuids must be non-empty strings")
        
        do_genai = DigitalOceanGenAI()
        result = do_genai.create_indexing_job(
            knowledge_base_uuid=knowledge_base_uuid,
            data_source_uuids=data_source_uuids
        )
        
        return {
            'message': 'Re-indexing job created successfully',
            'job': result
        }
    
    @app.route('/api/agents/<id>', methods=['GET'])
    @handle_response
    def get_agent(id):
        """
        Get a specific AI Agent by ID from the database.
        
        Path parameters:
            id (str, required): The ID of the agent to retrieve
        
        Returns:
            JSON response with agent details
        """
        if not id or not isinstance(id, str) or not id.strip():
            raise ValueError("Agent ID cannot be empty")
        
        # Grab agent from digital ocean
        do_genai = DigitalOceanGenAI()
        agent = do_genai.get_agent(id)
        
        if not agent:
            raise ValueError(f"Agent with ID '{id}' not found")
        
        return agent
    
    @app.route('/api/agents/<id>/api-keys', methods=['GET'])
    @handle_response
    def list_agent_api_keys(id):
        """
        List API keys for a specific AI Agent.
        
        Path parameters:
            id (str, required): The ID/UUID of the agent
        
        Returns:
            JSON response with list of API keys for the agent
        """
        if not id or not isinstance(id, str) or not id.strip():
            raise ValueError("Agent ID cannot be empty")
        
        do_genai = DigitalOceanGenAI()
        api_keys = do_genai.list_agent_api_keys(agent_uuid=id)
        
        return api_keys
    
    @app.route('/api/agents/<id>/api-keys', methods=['POST'])
    @handle_response
    def create_agent_api_key(id):
        """
        Create a new API key for a specific AI Agent.
        
        Path parameters:
            id (str, required): The ID/UUID of the agent
        
        Request body (JSON):
            name (str, required): Name for the API key
        
        Returns:
            JSON response with the created API key details (including the key itself)
        """
        if not id or not isinstance(id, str) or not id.strip():
            raise ValueError("Agent ID cannot be empty")
        
        data = request.get_json()
        
        if not data:
            raise ValueError("Request body must be provided")
        
        name = data.get('name')
        
        if not name or not isinstance(name, str) or not name.strip():
            raise ValueError("API key name is required and cannot be empty")
        
        do_genai = DigitalOceanGenAI()
        api_key = do_genai.create_agent_api_key(agent_uuid=id, name=name)
        
        return api_key
    
    @app.route('/api/agents', methods=['GET'])
    @handle_response
    def list_agents():
        """
        List all AI Agents saved in the database.
        
        Returns:
            JSON response with a list of all agents
        """
        do_genai = DigitalOceanGenAI()
        agents = do_genai.list_agents()
        return agents
    
    @app.route('/api/agents', methods=['POST'])
    @handle_response
    def create_agent():
        """
        Create a new AI Agent and save it to the database.
        
        Request body (JSON):
            name (str, required): Name of the agent
            description (str, optional): Description of the agent
            instructions (str, optional): Instructions for the agent
            model (str, optional): Model UUID
            workspace (str, optional): Workspace UUID
            region (str, optional): Region
            project_id (str, optional): Project ID
        
        Returns:
            JSON response with the created agent's ID and details
        """
        data = request.get_json()
        
        if not data:
            raise ValueError("Request body must be provided")
        
        # Extract fields from request (using camelCase as provided by user)
        name = data.get('name')
        description = data.get('description', '')
        instructions = data.get('instructions')
        model = data.get('model')
        workspace = data.get('workspace')
        region = data.get('region')
        project_id = data.get('project_id')
        
        # Validate required field
        if not name or not isinstance(name, str) or not name.strip():
            raise ValueError("Agent name is required and cannot be empty")
        if not instructions or not isinstance(instructions, str) or not instructions.strip():
            raise ValueError("Agent instructions are required and cannot be empty")

        # Create the agent in DigitalOcean (optional - don't fail if this fails)
        do_agent = None
        try:
            # Creat a new agent in DigitalOcean
            do_genai = DigitalOceanGenAI()
            do_agent_response = do_genai.create_agent(
                name=name,
                description=description,
                instructions=instructions,
                # model_uuid=model,
                # workspace_uuid=workspace,
                # region=region,
                # project_id=project_id
            )

            if not do_agent_response:
                raise RuntimeError("Failed to create agent in DigitalOcean - no response received")
            
            return do_agent_response

        except Exception as e:
            # Log the error but don't fail the request - so we can still create the agent in the database
            error_msg = str(e)
            # Extract more details from gRPC errors if available
            details = getattr(e, 'details', None)
            code = getattr(e, 'code', None)
            if details:
                error_msg += f" - Details: {details}"
            if code:
                error_msg += f" - Code: {code}"
            response_data = {
                'message': 'Agent creation failed',
                'error': error_msg
            }
            return response_data
    
    @app.route('/api/agents/<id>', methods=['DELETE'])
    @handle_response
    def delete_agent(id):
        if not id or not isinstance(id, str) or not id.strip():
            raise ValueError("Agent ID cannot be empty")
        
        do_genai = DigitalOceanGenAI()
        agent = do_genai.get_agent(id)
        
        if not agent and not agent['agent']:
            raise ValueError(f"Agent with ID '{id}' not found")
        print(f"Deleting agent with UUID: {agent['agent']['uuid']}")
        response = do_genai.delete_agent(agent['agent']['uuid'])
        return response

    @app.route('/api/models', methods=['GET'])
    @handle_response
    def list_models():
        """
        List available models from DigitalOcean GenAI.
        
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
        
        do_genai = DigitalOceanGenAI()
        result = do_genai.list_models(usecases=usecases, public_only=public_only)

        return result
    
    @app.route('/api/buckets', methods=['POST'])
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
    
    @app.route('/api/buckets', methods=['GET'])
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
    
    @app.route('/api/buckets/<name>', methods=['GET'])
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
    
    @app.route('/api/buckets/<name>', methods=['DELETE'])
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
    
    return app


# Create app instance for uWSGI and other WSGI servers
app = create_app()

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8080))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)
