"""
Knowledge base routes blueprint.
"""
from flask import Blueprint, request
from middleware.decorators import handle_response
from services.do_api import KnowledgeBases, IndexingJobs

knowledge_bases_bp = Blueprint('knowledge_bases', __name__, url_prefix='/api/knowledgebase')


@knowledge_bases_bp.route('', methods=['GET'])
@handle_response
def list_knowledge_bases():
    """
    List all knowledge bases.
    
    Returns:
        JSON response with a list of all knowledge bases
    """
    kb_service = KnowledgeBases()
    knowledge_bases = kb_service.list_knowledge_bases()
    return knowledge_bases


@knowledge_bases_bp.route('', methods=['POST'])
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
    
    kb_service = KnowledgeBases()
    result = kb_service.create_knowledge_base(
        name=name,
        description=description if description else None
    )
    
    if not result:
        raise RuntimeError("Failed to create knowledge base in DigitalOcean - no response received")
    
    return result


@knowledge_bases_bp.route('/<id>', methods=['GET'])
@handle_response
def get_knowledge_base(id):
    """
    Get a specific knowledge base by ID from DigitalOcean.
    
    Path parameters:
        id (str, required): The ID/UUID of the knowledge base to retrieve
    
    Returns:
        JSON response with knowledge base details
    """
    if not id or not isinstance(id, str) or not id.strip():
        raise ValueError("Knowledge base ID cannot be empty")
    
    kb_service = KnowledgeBases()
    knowledge_base = kb_service.get_knowledge_base(id)
    
    if not knowledge_base:
        raise ValueError(f"Knowledge base with ID '{id}' not found")
    
    data_sources = kb_service.list_knowledge_base_data_sources(knowledge_base_uuid=id)
    if not data_sources:
        raise ValueError(f"Data sources not found for knowledge base with ID '{id}'")
    
    knowledge_base['data_sources'] = data_sources['knowledge_base_data_sources']
    
    return knowledge_base


@knowledge_bases_bp.route('/<id>', methods=['DELETE'])
@handle_response
def delete_knowledge_base(id):
    """
    Delete a knowledge base from DigitalOcean.
    
    Path parameters:
        id (str, required): The ID/UUID of the knowledge base to delete
    
    Returns:
        JSON response confirming knowledge base deletion
    """
    if not id or not isinstance(id, str) or not id.strip():
        raise ValueError("Knowledge base ID cannot be empty")
    
    kb_service = KnowledgeBases()
    # Verify knowledge base exists before deleting
    knowledge_base = kb_service.get_knowledge_base(id)
    
    if not knowledge_base:
        raise ValueError(f"Knowledge base with ID '{id}' not found")
    
    response = kb_service.delete_knowledge_base(id)
    return response


@knowledge_bases_bp.route('/<id>/datasources', methods=['GET'])
@handle_response
def list_data_sources(id):
    """
    Get a specific data source by UUID from DigitalOcean.
    
    Path parameters:
        id (str, required): The ID/UUID of the knowledge base to retrieve
    
    Returns:
        JSON response with data source details
    """
    if not id or not isinstance(id, str) or not id.strip():
        raise ValueError("Knowledge base ID cannot be empty")
    
    kb_service = KnowledgeBases()
    data_sources = kb_service.list_knowledge_base_data_sources(knowledge_base_uuid=id)
    return data_sources


@knowledge_bases_bp.route('/reindex', methods=['POST'])
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
    
    indexing_service = IndexingJobs()
    result = indexing_service.create_indexing_job(
        knowledge_base_uuid=knowledge_base_uuid,
        data_source_uuids=data_source_uuids
    )
    
    return {
        'message': 'Re-indexing job created successfully',
        'job': result
    }

