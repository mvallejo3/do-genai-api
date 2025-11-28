"""
Agent routes blueprint.
"""
from flask import Blueprint, request
from middleware.decorators import handle_response
from services.do_api import Agents, KnowledgeBases, APIKeys

agents_bp = Blueprint('agents', __name__, url_prefix='/api/agents')


@agents_bp.route('', methods=['GET'])
@handle_response
def list_agents():
    """
    List all AI Agents saved in the database.
    
    Returns:
        JSON response with a list of all agents
    """
    agents_service = Agents()
    agents = agents_service.list_agents()
    return agents


@agents_bp.route('', methods=['POST'])
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
    try:
        # Creat a new agent in DigitalOcean
        agents_service = Agents()
        
        # Build optional parameters dict only with values that exist
        optional_params = {}
        if model:
            optional_params['model_uuid'] = model
        if workspace:
            optional_params['workspace_uuid'] = workspace
        if region:
            optional_params['region'] = region
        if project_id:
            optional_params['project_id'] = project_id
        
        do_agent_response = agents_service.create_agent(
            name=name,
            description=description,
            instructions=instructions,
            **optional_params
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


@agents_bp.route('/<id>', methods=['GET'])
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
    agents_service = Agents()
    agent = agents_service.get_agent(id)
    
    if not agent:
        raise ValueError(f"Agent with ID '{id}' not found")
    
    return agent


@agents_bp.route('/<id>', methods=['DELETE'])
@handle_response
def delete_agent(id):
    """
    Delete an AI Agent.
    
    Path parameters:
        id (str, required): The ID of the agent to delete
    
    Returns:
        JSON response confirming deletion
    """
    if not id or not isinstance(id, str) or not id.strip():
        raise ValueError("Agent ID cannot be empty")
    
    agents_service = Agents()
    agent = agents_service.get_agent(id)
    
    if not agent and not agent['agent']:
        raise ValueError(f"Agent with ID '{id}' not found")
    print(f"Deleting agent with UUID: {agent['agent']['uuid']}")
    response = agents_service.delete_agent(agent['agent']['uuid'])
    return response


@agents_bp.route('/<id>/api-keys', methods=['GET'])
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
    
    api_keys_service = APIKeys()
    api_keys = api_keys_service.list_agent_api_keys(agent_uuid=id)
    
    return api_keys


@agents_bp.route('/<id>/api-keys', methods=['POST'])
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
    
    api_keys_service = APIKeys()
    api_key = api_keys_service.create_agent_api_key(agent_uuid=id, name=name)
    
    return api_key


@agents_bp.route('/<id>/attach-knowledgebase', methods=['POST'])
@handle_response
def attach_agent_knowledge_base(id):
    """
    Attach a knowledge base to an agent.
    
    Path parameters:
        id (str, required): The ID/UUID of the agent
    
    Request body (JSON):
        knowledge_base_uuid (str, required): UUID of the knowledge base to attach
    
    Returns:
        JSON response confirming the knowledge base attachment
    """
    if not id or not isinstance(id, str) or not id.strip():
        raise ValueError("Agent ID cannot be empty")
    
    data = request.get_json()
    
    if not data:
        raise ValueError("Request body must be provided")
    
    knowledge_base_uuid = data.get('knowledge_base_uuid')
    
    if not knowledge_base_uuid or not isinstance(knowledge_base_uuid, str) or not knowledge_base_uuid.strip():
        raise ValueError("knowledge_base_uuid is required and cannot be empty")
    
    # Verify agent exists
    agents_service = Agents()
    agent = agents_service.get_agent(id)
    
    if not agent:
        raise ValueError(f"Agent with ID '{id}' not found")
    
    # Verify knowledge base exists
    kb_service = KnowledgeBases()
    knowledge_base = kb_service.get_knowledge_base(knowledge_base_uuid)
    
    if not knowledge_base:
        raise ValueError(f"Knowledge base with ID '{knowledge_base_uuid}' not found")
    
    # Attach knowledge base to agent
    result = agents_service.attach_knowledge_base(
        agent_uuid=id,
        knowledge_base_uuid=knowledge_base_uuid
    )
    
    return {
        'message': 'Knowledge base attached to agent successfully',
        'agent_id': id,
        'knowledge_base_uuid': knowledge_base_uuid,
        'result': result
    }

