"""
DigitalOcean GenAI service for managing agents, knowledge bases, models, and workspaces.
"""

import os
from typing import Optional, List, Dict, Any
from pydo import Client

from typing import MutableMapping  # type: ignore  # pylint: disable=ungrouped-imports
JSON = MutableMapping[str, Any]

DEFAULT_MODEL_UUID = os.getenv('DEFAULT_MODEL_UUID', '')
DEFAULT_PROJECT_UUID = os.getenv('DEFAULT_PROJECT_UUID', '')
DEFAULT_WORKSPACE_UUID = os.getenv('DEFAULT_WORKSPACE_UUID', '')
DEFAULT_REGION = os.getenv('DEFAULT_REGION', os.getenv('SPACES_REGION', 'tor1'))

class DigitalOceanGenAI:
    """
    Service class for managing DigitalOcean GenAI resources including:
    - Workspaces
    - Agents
    - Knowledge Bases
    - Models
    - API Keys
    - Indexing Jobs
    - Databases (OpenSearch)
    """
    
    def __init__(self, api_token: Optional[str] = None):
        """
        Initialize DigitalOcean GenAI client.
        
        Args:
            api_token: DigitalOcean API token (defaults to DIGITALOCEAN_API_TOKEN env var)
        
        Raises:
            ValueError: If API token is not provided and not found in environment
        """
        if not DEFAULT_WORKSPACE_UUID or not DEFAULT_MODEL_UUID or not DEFAULT_REGION:
            raise ValueError("DEFAULT_WORKSPACE_UUID, DEFAULT_MODEL_UUID, and DEFAULT_REGION must be set in the environment variables")
        
        self.api_token = api_token or os.getenv('DIGITALOCEAN_API_TOKEN')
        
        if not self.api_token:
            raise ValueError(
                "DigitalOcean API token not found. Set DIGITALOCEAN_API_TOKEN "
                "environment variable or pass api_token parameter."
            )
        
        self.client = Client(token=self.api_token)
    
    # ==================== Workspace Methods ====================
    
    def create_workspace(
        self,
        name: str,
        description: Optional[str] = None
    ) -> JSON:
        """
        Create a new workspace.
        
        Args:
            name: Name of the workspace
            description: Optional description of the workspace
        
        Returns:
            Dictionary containing workspace details
        """
        body = {"name": name}
        if description:
            body["description"] = description
        
        response = self.client.genai.create_workspace(body=body)
        return response
    
    def get_workspace(self, workspace_uuid: str = DEFAULT_WORKSPACE_UUID) -> JSON:
        """
        Retrieve an existing workspace.
        
        Args:
            workspace_uuid: UUID of the workspace
        
        Returns:
            Dictionary containing workspace details
        """
        response = self.client.genai.get_workspace(workspace_uuid=workspace_uuid)
        return response
    
    def list_workspaces(self) -> JSON:
        """
        List all workspaces.
        
        Returns:
            Dictionary containing list of workspaces
        """
        response = self.client.genai.list_workspaces()
        return response
    
    def update_workspace(
        self,
        workspace_uuid: str = DEFAULT_WORKSPACE_UUID,
        name: Optional[str] = None,
        description: Optional[str] = None
    ) -> JSON:
        """
        Update a workspace.
        
        Args:
            workspace_uuid: UUID of the workspace
            name: Optional new name
            description: Optional new description
        
        Returns:
            Dictionary containing updated workspace details
        """
        body = {}
        if name is not None:
            body["name"] = name
        if description is not None:
            body["description"] = description
        
        response = self.client.genai.update_workspace(
            workspace_uuid=workspace_uuid,
            body=body
        )
        return response
    
    def delete_workspace(self, workspace_uuid: str = DEFAULT_WORKSPACE_UUID) -> JSON:
        """
        Delete a workspace.
        
        Args:
            workspace_uuid: UUID of the workspace to delete
        
        Returns:
            Dictionary containing deletion result
        """
        response = self.client.genai.delete_workspace(workspace_uuid=workspace_uuid)
        return response
    
    # ==================== Agent Methods ====================
    
    def create_agent(
        self,
        name: str,
        model_uuid: str = DEFAULT_MODEL_UUID,
        workspace_uuid: str = DEFAULT_WORKSPACE_UUID,
        region: str = DEFAULT_REGION,
        description: Optional[str] = None,
        instructions: Optional[str] = None,
        project_id: Optional[str] = DEFAULT_PROJECT_UUID,
        **kwargs
    ) -> JSON:
        """
        Create a new agent.
        
        Args:
            name: Name of the agent
            model_uuid: UUID of the model to use
            workspace_uuid: UUID of the workspace
            region: Region where the agent will be deployed (default: 'tor1')
            description: Optional description
            instructions: Optional system instructions
            **kwargs: Additional agent configuration options
        
        Returns:
            Dictionary containing agent details
        
        Raises:
            RuntimeError: If agent creation fails with detailed error message
        """
        body = {
            "name": name,
            "model_uuid": model_uuid,
            "workspace_uuid": workspace_uuid,
            "region": region,
            "project_id": project_id
        }
        
        if description:
            body["description"] = description
        if instructions:
            body["instruction"] = instructions
        
        # Add any additional kwargs
        body.update(kwargs)
        
        try:
            response = self.client.genai.create_agent(body=body)
            return response
        except Exception as e:
            # Extract detailed error information
            error_msg = f"Failed to create agent '{name}'"
            
            # Try to extract gRPC error details
            error_str = str(e)
            code = getattr(e, 'code', None)
            details = getattr(e, 'details', None)
            
            if code:
                error_msg += f" (code: {code})"
            if details:
                error_msg += f" - {details}"
            elif error_str:
                error_msg += f" - {error_str}"
            
            # Add context about the request
            error_msg += f" | Workspace UUID: {workspace_uuid}, Model UUID: {model_uuid}, Region: {region}"
            
            raise RuntimeError(error_msg) from e
    
    def get_agent(self, agent_uuid: str) -> JSON:
        """
        Retrieve an existing agent.
        
        Args:
            agent_uuid: UUID of the agent
        
        Returns:
            Dictionary containing agent details
        """
        response = self.client.genai.get_agent(uuid=agent_uuid)
        return response
    
    def list_agents(
        self,
        workspace_uuid: Optional[str] = None,
        anthropic_key_uuid: Optional[str] = None,
        openai_key_uuid: Optional[str] = None
    ) -> JSON:
        """
        List agents. Can filter by workspace, Anthropic key, or OpenAI key.
        
        Args:
            workspace_uuid: Optional workspace UUID to filter by
            anthropic_key_uuid: Optional Anthropic key UUID to filter by
            openai_key_uuid: Optional OpenAI key UUID to filter by
        
        Returns:
            Dictionary containing list of agents
        """
        if workspace_uuid:
            response = self.client.genai.list_agents_by_workspace(
                workspace_uuid=workspace_uuid
            )
        elif anthropic_key_uuid:
            response = self.client.genai.list_agents_by_anthropic_key(
                uuid=anthropic_key_uuid
            )
        elif openai_key_uuid:
            response = self.client.genai.list_agents_by_openai_key(
                uuid=openai_key_uuid
            )
        else:
            response = self.client.genai.list_agents()
        
        return response
    
    def update_agent(
        self,
        agent_uuid: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        instructions: Optional[str] = None,
        model_uuid: Optional[str] = None,
        **kwargs
    ) -> JSON:
        """
        Update an agent.
        
        Args:
            agent_uuid: UUID of the agent
            name: Optional new name
            description: Optional new description
            instructions: Optional new instructions
            model_uuid: Optional new model UUID
            **kwargs: Additional update options
        
        Returns:
            Dictionary containing updated agent details
        """
        body = {}
        if name is not None:
            body["name"] = name
        if description is not None:
            body["description"] = description
        if instructions is not None:
            body["instructions"] = instructions
        if model_uuid is not None:
            body["model_uuid"] = model_uuid
        
        body.update(kwargs)
        
        response = self.client.genai.update_agent(
            uuid=agent_uuid,
            body=body
        )
        return response
    
    def delete_agent(self, agent_uuid: str) -> JSON:
        """
        Delete an agent.
        
        Args:
            agent_uuid: UUID of the agent to delete
        
        Returns:
            Dictionary containing deletion result
        """
        response = self.client.genai.delete_agent(uuid=agent_uuid)
        return response
    
    def get_agent_children(self, agent_uuid: str) -> JSON:
        """
        View agent routes (child agents).
        
        Args:
            agent_uuid: UUID of the agent
        
        Returns:
            Dictionary containing agent routes
        """
        response = self.client.genai.get_agent_children(uuid=agent_uuid)
        return response
    
    def get_agent_usage(
        self,
        agent_uuid: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> JSON:
        """
        Get agent usage statistics.
        
        Args:
            agent_uuid: UUID of the agent
            start_date: Optional start date (ISO format)
            end_date: Optional end date (ISO format)
        
        Returns:
            Dictionary containing usage statistics
        """
        params = {}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        
        response = self.client.genai.get_agent_usage(
            agent_uuid=agent_uuid,
            **params
        )
        return response
    
    def list_agent_versions(self, agent_uuid: str) -> JSON:
        """
        List versions of an agent.
        
        Args:
            agent_uuid: UUID of the agent
        
        Returns:
            Dictionary containing list of agent versions
        """
        response = self.client.genai.list_agent_versions(uuid=agent_uuid)
        return response
    
    def rollback_to_agent_version(
        self,
        agent_uuid: str,
        version: int
    ) -> JSON:
        """
        Rollback an agent to a specific version.
        
        Args:
            agent_uuid: UUID of the agent
            version: Version number to rollback to
        
        Returns:
            Dictionary containing updated agent details
        """
        body = {"version": version}
        response = self.client.genai.rollback_to_agent_version(
            uuid=agent_uuid,
            body=body
        )
        return response
    
    def attach_knowledge_base(
        self,
        agent_uuid: str,
        knowledge_base_uuid: str
    ) -> JSON:
        """
        Attach a knowledge base to an agent.
        
        Args:
            agent_uuid: UUID of the agent
            knowledge_base_uuid: UUID of the knowledge base
        
        Returns:
            Dictionary containing attachment result
        """
        response = self.client.genai.attach_knowledge_base(
            agent_uuid=agent_uuid,
            knowledge_base_uuid=knowledge_base_uuid,
        )
        return response
    
    def attach_knowledge_bases(
        self,
        agent_uuid: str,
        knowledge_base_uuids: List[str]
    ) -> JSON:
        """
        Attach multiple knowledge bases to an agent.
        
        Args:
            agent_uuid: UUID of the agent
            knowledge_base_uuids: List of knowledge base UUIDs
        
        Returns:
            Dictionary containing attachment result
        """
        body = {"knowledge_base_uuids": knowledge_base_uuids}
        response = self.client.genai.attach_knowledge_bases(
            agent_uuid=agent_uuid,
            body=body
        )
        return response
    
    def detach_knowledge_base(
        self,
        agent_uuid: str,
        knowledge_base_uuid: str
    ) -> JSON:
        """
        Detach a knowledge base from an agent.
        
        Args:
            agent_uuid: UUID of the agent
            knowledge_base_uuid: UUID of the knowledge base
        
        Returns:
            Dictionary containing detachment result
        """
        body = {"knowledge_base_uuid": knowledge_base_uuid}
        response = self.client.genai.detach_knowledge_base(
            agent_uuid=agent_uuid,
            knowledge_base_uuid=knowledge_base_uuid,
            body=body
        )
        return response
    
    def attach_agent(
        self,
        agent_uuid: str,
        child_agent_uuid: str,
        route: str
    ) -> JSON:
        """
        Add an agent route to an agent.
        
        Args:
            agent_uuid: UUID of the parent agent
            child_agent_uuid: UUID of the child agent
            route: Route path for the child agent
        
        Returns:
            Dictionary containing attachment result
        """
        body = {
            "agent_uuid": child_agent_uuid,
            "route": route
        }
        response = self.client.genai.attach_agent(
            parent_agent_uuid=agent_uuid,
            child_agent_uuid=child_agent_uuid,
            route=route,
            body=body
        )
        return response
    
    def detach_agent(
        self,
        agent_uuid: str,
        child_agent_uuid: str
    ) -> JSON:
        """
        Delete an agent route from an agent.
        
        Args:
            agent_uuid: UUID of the parent agent
            child_agent_uuid: UUID of the child agent to detach
        
        Returns:
            Dictionary containing detachment result
        """
        body = {"agent_uuid": child_agent_uuid}
        response = self.client.genai.detach_agent(
            parent_agent_uuid=agent_uuid,
            child_agent_uuid=child_agent_uuid,
            body=body
        )
        return response
    
    def update_agent_deployment_visibility(
        self,
        agent_uuid: str,
        is_public: bool
    ) -> JSON:
        """
        Update agent deployment visibility (public/private).
        
        Args:
            agent_uuid: UUID of the agent
            is_public: Whether the agent should be publicly accessible
        
        Returns:
            Dictionary containing updated agent details
        """
        body = {"is_public": is_public}
        response = self.client.genai.update_agent_deployment_visibility(
            uuid=agent_uuid,
            body=body
        )
        return response
    
    def update_agents_workspace(
        self,
        agent_uuids: List[str],
        workspace_uuid: str = DEFAULT_WORKSPACE_UUID
    ) -> JSON:
        """
        Move agents to a different workspace.
        
        Args:
            agent_uuids: List of agent UUIDs to move
            workspace_uuid: UUID of the target workspace
        
        Returns:
            Dictionary containing update result
        """
        body = {
            "agent_uuids": agent_uuids,
            "workspace_uuid": workspace_uuid
        }
        response = self.client.genai.update_agents_workspace(
            agent_uuids=agent_uuids,
            workspace_uuid=workspace_uuid,
            body=body
        )
        return response
    
    def attach_agent_function(
        self,
        agent_uuid: str,
        function_uuid: str,
        route: str
    ) -> JSON:
        """
        Add a function route to an agent.
        
        Args:
            agent_uuid: UUID of the agent
            function_uuid: UUID of the function
            route: Route path for the function
        
        Returns:
            Dictionary containing attachment result
        """
        body = {
            "function_uuid": function_uuid,
            "route": route
        }
        response = self.client.genai.attach_agent_function(
            agent_uuid=agent_uuid,
            body=body
        )
        return response
    
    def update_agent_function(
        self,
        agent_uuid: str,
        function_uuid: str,
        route: Optional[str] = None
    ) -> JSON:
        """
        Update a function route for an agent.
        
        Args:
            agent_uuid: UUID of the agent
            function_uuid: UUID of the function
            route: Optional new route path
        
        Returns:
            Dictionary containing updated function route details
        """
        body = {}
        if route is not None:
            body["route"] = route
        
        response = self.client.genai.update_agent_function(
            agent_uuid=agent_uuid,
            function_uuid=function_uuid,
            body=body
        )
        return response
    
    def detach_agent_function(
        self,
        agent_uuid: str,
        function_uuid: str
    ) -> JSON:
        """
        Delete a function route for an agent.
        
        Args:
            agent_uuid: UUID of the agent
            function_uuid: UUID of the function to detach
        
        Returns:
            Dictionary containing detachment result
        """
        body = {"function_uuid": function_uuid}
        response = self.client.genai.detach_agent_function(
            agent_uuid=agent_uuid,
            function_uuid=function_uuid,
            body=body
        )
        return response
    
    def update_attached_agent(
        self,
        agent_uuid: str,
        child_agent_uuid: str,
        route: Optional[str] = None
    ) -> JSON:
        """
        Update an agent route for an agent.
        
        Args:
            agent_uuid: UUID of the parent agent
            child_agent_uuid: UUID of the child agent
            route: Optional new route path
        
        Returns:
            Dictionary containing updated agent route details
        """
        body = {}
        if route is not None:
            body["route"] = route
        
        response = self.client.genai.update_attached_agent(
            parent_agent_uuid=agent_uuid,
            child_agent_uuid=child_agent_uuid,
            body=body
        )
        return response
    
    # ==================== Knowledge Base Methods ====================
    
    def create_knowledge_base(
        self,
        name: str,
        description: Optional[str] = None,
        **kwargs
    ) -> JSON:
        """
        Create a new knowledge base.
        
        Args:
            name: Name of the knowledge base
            description: Optional description
            **kwargs: Additional knowledge base configuration options
        
        Returns:
            Dictionary containing knowledge base details
        """
        body = {
            "name": name,
            "project_id": DEFAULT_PROJECT_UUID,
            "embedding_model_uuid": "22652c2a-79ed-11ef-bf8f-4e013e2ddde4",
            "database_id": "eb400988-68af-4ad6-ad15-ab91b7e85625",
            "datasources": [{
                "spaces_data_source": {
                    "bucket_name": 'roami-bot',
                    # "item_path": '',
                    "region": DEFAULT_REGION
                }
            }]
        }
        if description:
            body["description"] = description
        
        # if "embedding_model_uuid" in kwargs:
        #     body["embedding_model_uuid"] = kwargs["embedding_model_uuid"]
        # else:
        #     body["embedding_model_uuid"] = "22652c2a-79ed-11ef-bf8f-4e013e2ddde4"

        body.update(kwargs)
        
        response = self.client.genai.create_knowledge_base(body=body)
        return response
    
    def get_knowledge_base(self, knowledge_base_uuid: str) -> JSON:
        """
        Retrieve an existing knowledge base.
        
        Args:
            knowledge_base_uuid: UUID of the knowledge base
        
        Returns:
            Dictionary containing knowledge base details
        """
        response = self.client.genai.get_knowledge_base(
            uuid=knowledge_base_uuid
        )
        return response
    
    def list_knowledge_bases(self) -> JSON:
        """
        List all knowledge bases.
        
        Returns:
            Dictionary containing list of knowledge bases
        """
        response = self.client.genai.list_knowledge_bases()
        return response
    
    def update_knowledge_base(
        self,
        knowledge_base_uuid: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        **kwargs
    ) -> JSON:
        """
        Update a knowledge base.
        
        Args:
            knowledge_base_uuid: UUID of the knowledge base
            name: Optional new name
            description: Optional new description
            **kwargs: Additional update options
        
        Returns:
            Dictionary containing updated knowledge base details
        """
        body = {}
        if name is not None:
            body["name"] = name
        if description is not None:
            body["description"] = description
        
        body.update(kwargs)
        
        response = self.client.genai.update_knowledge_base(
            uuid=knowledge_base_uuid,
            body=body
        )
        return response
    
    def delete_knowledge_base(self, knowledge_base_uuid: str) -> JSON:
        """
        Delete a knowledge base.
        
        Args:
            knowledge_base_uuid: UUID of the knowledge base to delete
        
        Returns:
            Dictionary containing deletion result
        """
        response = self.client.genai.delete_knowledge_base(
            uuid=knowledge_base_uuid
        )
        return response
    
    def create_knowledge_base_data_source(
        self,
        knowledge_base_uuid: str,
        url: Optional[str] = None,
        **kwargs
    ) -> JSON:
        """
        Add a data source to a knowledge base.
        
        Args:
            knowledge_base_uuid: UUID of the knowledge base
            url: Optional URL for the data source
            **kwargs: Additional data source configuration options
        
        Returns:
            Dictionary containing data source details
        """
        body = {}
        if url:
            body["url"] = url
        
        body.update(kwargs)
        
        response = self.client.genai.create_knowledge_base_data_source(
            knowledge_base_uuid=knowledge_base_uuid,
            body=body
        )
        return response
    
    def list_knowledge_base_data_sources(
        self,
        knowledge_base_uuid: str
    ) -> JSON:
        """
        List data sources for a knowledge base.
        
        Args:
            knowledge_base_uuid: UUID of the knowledge base
        
        Returns:
            Dictionary containing list of data sources
        """
        response = self.client.genai.list_knowledge_base_data_sources(
            knowledge_base_uuid=knowledge_base_uuid
        )
        return response
    
    def delete_knowledge_base_data_source(
        self,
        knowledge_base_uuid: str,
        data_source_uuid: str
    ) -> JSON:
        """
        Delete a data source from a knowledge base.
        
        Args:
            knowledge_base_uuid: UUID of the knowledge base
            data_source_uuid: UUID of the data source to delete
        
        Returns:
            Dictionary containing deletion result
        """
        response = self.client.genai.delete_knowledge_base_data_source(
            knowledge_base_uuid=knowledge_base_uuid,
            data_source_uuid=data_source_uuid
        )
        return response
    
    def create_indexing_job(
        self,
        knowledge_base_uuid: str,
        data_source_uuids: Optional[List[str]] = None
    ) -> JSON:
        """
        Start an indexing job for a knowledge base.
        
        Args:
            knowledge_base_uuid: UUID of the knowledge base
            data_source_uuids: Optional list of data source UUIDs to index.
                             If None, all data sources will be indexed.
        
        Returns:
            Dictionary containing indexing job details
        """
        body = {
            "knowledge_base_uuid": knowledge_base_uuid,
            "data_source_uuids": data_source_uuids
        }
        
        response = self.client.genai.create_indexing_job(body=body)
        return response
    
    def get_indexing_job(self, indexing_job_uuid: str) -> JSON:
        """
        Retrieve status of an indexing job.
        
        Args:
            indexing_job_uuid: UUID of the indexing job
        
        Returns:
            Dictionary containing indexing job status
        """
        response = self.client.genai.get_indexing_job(
            uuid=indexing_job_uuid
        )
        return response
    
    def list_indexing_jobs(
        self,
        knowledge_base_uuid: Optional[str] = None
    ) -> JSON:
        """
        List indexing jobs. Can filter by knowledge base.
        
        Args:
            knowledge_base_uuid: Optional knowledge base UUID to filter by
        
        Returns:
            Dictionary containing list of indexing jobs
        """
        if knowledge_base_uuid:
            response = self.client.genai.list_indexing_jobs_by_knowledge_base(
                knowledge_base_uuid=knowledge_base_uuid
            )
        else:
            response = self.client.genai.list_indexing_jobs()
        
        return response
    
    def cancel_indexing_job(self, indexing_job_uuid: str) -> JSON:
        """
        Cancel an indexing job.
        
        Args:
            indexing_job_uuid: UUID of the indexing job to cancel
        
        Returns:
            Dictionary containing cancellation result
        """
        response = self.client.genai.cancel_indexing_job(
            uuid=indexing_job_uuid
        )
        return response
    
    def create_scheduled_indexing(
        self,
        knowledge_base_uuid: str,
        schedule: str,
        **kwargs
    ) -> JSON:
        """
        Create scheduled indexing for a knowledge base.
        
        Args:
            knowledge_base_uuid: UUID of the knowledge base
            schedule: Cron expression for the schedule
            **kwargs: Additional scheduling options
        
        Returns:
            Dictionary containing scheduled indexing details
        """
        body = {
            "knowledge_base_uuid": knowledge_base_uuid,
            "schedule": schedule
        }
        body.update(kwargs)
        
        response = self.client.genai.create_scheduled_indexing(body=body)
        return response
    
    def get_scheduled_indexing(
        self,
        knowledge_base_uuid: str
    ) -> JSON:
        """
        Get scheduled indexing for a knowledge base.
        
        Args:
            knowledge_base_uuid: UUID of the knowledge base
        
        Returns:
            Dictionary containing scheduled indexing details
        """
        response = self.client.genai.get_scheduled_indexing(
            knowledge_base_uuid=knowledge_base_uuid
        )
        return response
    
    def delete_scheduled_indexing(
        self,
        knowledge_base_uuid: str
    ) -> JSON:
        """
        Delete scheduled indexing for a knowledge base.
        
        Args:
            knowledge_base_uuid: UUID of the knowledge base
        
        Returns:
            Dictionary containing deletion result
        """
        response = self.client.genai.delete_scheduled_indexing(
            uuid=knowledge_base_uuid
        )
        return response
    
    # ==================== Model Methods ====================
    
    def list_models(
        self,
        usecases: Optional[List[str]] = [],
        public_only: bool = True
    ) -> JSON:
        """
        List available models.
        
        Args:
            usecases: Optional list of use cases to filter by
            public_only: Whether to show only public models (default: True)
        
        Returns:
            Dictionary containing list of models
        """
        params = {
            "public_only": public_only,
            "usecases": usecases
        }
        response = self.client.genai.list_models(params=params)
        return response
    
    def list_datacenter_regions(self) -> JSON:
        """
        List available datacenter regions.
        
        Returns:
            Dictionary containing list of regions
        """
        response = self.client.genai.list_datacenter_regions()
        return response
    
    # ==================== Database Methods ====================
    
    def list_opensearch_databases(self) -> JSON:
        """
        List all OpenSearch databases from DigitalOcean.
        
        Returns:
            Dictionary containing list of OpenSearch databases
        """
        response = self.client.databases.list_clusters()
        
        # Filter to only return OpenSearch databases
        if 'databases' in response:
            opensearch_databases = [
                db for db in response['databases']
                if db.get('engine', '').lower() == 'opensearch'
            ]
            return {
                'databases': opensearch_databases,
                'count': len(opensearch_databases)
            }
        
        # If response structure is different, return as-is but filter
        if isinstance(response, list):
            opensearch_databases = [
                db for db in response
                if db.get('engine', '').lower() == 'opensearch'
            ]
            return {
                'databases': opensearch_databases,
                'count': len(opensearch_databases)
            }
        
        # Return filtered response
        return response
    
    # ==================== API Key Methods ====================
    
    def create_agent_api_key(
        self,
        agent_uuid: str,
        name: str
    ) -> JSON:
        """
        Create an API key for an agent.
        
        Args:
            agent_uuid: UUID of the agent
            name: Name for the API key
        
        Returns:
            Dictionary containing API key details (including the key itself)
        """
        body = {"name": name}
        response = self.client.genai.create_agent_api_key(
            agent_uuid=agent_uuid,
            body=body
        )
        return response
    
    def list_agent_api_keys(self, agent_uuid: str) -> JSON:
        """
        List API keys for an agent.
        
        Args:
            agent_uuid: UUID of the agent
        
        Returns:
            Dictionary containing list of API keys
        """
        response = self.client.genai.list_agent_api_keys(agent_uuid=agent_uuid)
        return response
    
    def update_agent_api_key(
        self,
        agent_uuid: str,
        api_key_uuid: str,
        name: Optional[str] = None
    ) -> JSON:
        """
        Update an API key for an agent.
        
        Args:
            agent_uuid: UUID of the agent
            api_key_uuid: UUID of the API key
            name: Optional new name
        
        Returns:
            Dictionary containing updated API key details
        """
        body = {}
        if name is not None:
            body["name"] = name
        
        response = self.client.genai.update_agent_api_key(
            agent_uuid=agent_uuid,
            api_key_uuid=api_key_uuid,
            body=body
        )
        return response
    
    def delete_agent_api_key(
        self,
        agent_uuid: str,
        api_key_uuid: str
    ) -> JSON:
        """
        Delete an API key for an agent.
        
        Args:
            agent_uuid: UUID of the agent
            api_key_uuid: UUID of the API key to delete
        
        Returns:
            Dictionary containing deletion result
        """
        response = self.client.genai.delete_agent_api_key(
            agent_uuid=agent_uuid,
            api_key_uuid=api_key_uuid
        )
        return response
    
    def regenerate_agent_api_key(
        self,
        agent_uuid: str,
        api_key_uuid: str
    ) -> JSON:
        """
        Regenerate an API key for an agent.
        
        Args:
            agent_uuid: UUID of the agent
            api_key_uuid: UUID of the API key to regenerate
        
        Returns:
            Dictionary containing new API key details
        """
        response = self.client.genai.regenerate_agent_api_key(
            agent_uuid=agent_uuid,
            api_key_uuid=api_key_uuid
        )
        return response
    
    def create_model_api_key(
        self,
        name: str,
        model_uuid: str = DEFAULT_MODEL_UUID
    ) -> JSON:
        """
        Create an API key for a model.
        
        Args:
            name: Name for the API key
            model_uuid: UUID of the model
        
        Returns:
            Dictionary containing API key details
        """
        body = {
            "name": name,
            "model_uuid": model_uuid
        }
        response = self.client.genai.create_model_api_key(body=body)
        return response
    
    def list_model_api_keys(self) -> JSON:
        """
        List all model API keys.
        
        Returns:
            Dictionary containing list of model API keys
        """
        response = self.client.genai.list_model_api_keys()
        return response
    
    def update_model_api_key(
        self,
        api_key_uuid: str,
        name: Optional[str] = None
    ) -> JSON:
        """
        Update a model API key.
        
        Args:
            api_key_uuid: UUID of the API key
            name: Optional new name
        
        Returns:
            Dictionary containing updated API key details
        """
        body = {}
        if name is not None:
            body["name"] = name
        
        response = self.client.genai.update_model_api_key(
            api_key_uuid=api_key_uuid,
            body=body
        )
        return response
    
    def delete_model_api_key(self, api_key_uuid: str) -> JSON:
        """
        Delete a model API key.
        
        Args:
            api_key_uuid: UUID of the API key to delete
        
        Returns:
            Dictionary containing deletion result
        """
        response = self.client.genai.delete_model_api_key(
            api_key_uuid=api_key_uuid
        )
        return response
    
    def regenerate_model_api_key(self, api_key_uuid: str) -> JSON:
        """
        Regenerate a model API key.
        
        Args:
            api_key_uuid: UUID of the API key to regenerate
        
        Returns:
            Dictionary containing new API key details
        """
        response = self.client.genai.regenerate_model_api_key(
            api_key_uuid=api_key_uuid
        )
        return response
    
    def create_openai_api_key(
        self,
        name: str,
        api_key: str
    ) -> JSON:
        """
        Create an OpenAI API key.
        
        Args:
            name: Name for the API key
            api_key: The OpenAI API key value
        
        Returns:
            Dictionary containing API key details
        """
        body = {
            "name": name,
            "api_key": api_key
        }
        response = self.client.genai.create_openai_api_key(body=body)
        return response
    
    def list_openai_api_keys(self) -> JSON:
        """
        List all OpenAI API keys.
        
        Returns:
            Dictionary containing list of OpenAI API keys
        """
        response = self.client.genai.list_openai_api_keys()
        return response
    
    def get_openai_api_key(self, api_key_uuid: str) -> JSON:
        """
        Get an OpenAI API key.
        
        Args:
            api_key_uuid: UUID of the API key
        
        Returns:
            Dictionary containing API key details
        """
        response = self.client.genai.get_openai_api_key(api_key_uuid=api_key_uuid)
        return response
    
    def update_openai_api_key(
        self,
        api_key_uuid: str,
        name: Optional[str] = None,
        api_key: Optional[str] = None
    ) -> JSON:
        """
        Update an OpenAI API key.
        
        Args:
            api_key_uuid: UUID of the API key
            name: Optional new name
            api_key: Optional new API key value
        
        Returns:
            Dictionary containing updated API key details
        """
        body = {}
        if name is not None:
            body["name"] = name
        if api_key is not None:
            body["api_key"] = api_key
        
        response = self.client.genai.update_openai_api_key(
            api_key_uuid=api_key_uuid,
            body=body
        )
        return response
    
    def delete_openai_api_key(self, api_key_uuid: str) -> JSON:
        """
        Delete an OpenAI API key.
        
        Args:
            api_key_uuid: UUID of the API key to delete
        
        Returns:
            Dictionary containing deletion result
        """
        response = self.client.genai.delete_openai_api_key(
            api_key_uuid=api_key_uuid
        )
        return response
    
    def create_anthropic_api_key(
        self,
        name: str,
        api_key: str
    ) -> JSON:
        """
        Create an Anthropic API key.
        
        Args:
            name: Name for the API key
            api_key: The Anthropic API key value
        
        Returns:
            Dictionary containing API key details
        """
        body = {
            "name": name,
            "api_key": api_key
        }
        response = self.client.genai.create_anthropic_api_key(body=body)
        return response
    
    def list_anthropic_api_keys(self) -> JSON:
        """
        List all Anthropic API keys.
        
        Returns:
            Dictionary containing list of Anthropic API keys
        """
        response = self.client.genai.list_anthropic_api_keys()
        return response
    
    def get_anthropic_api_key(self, api_key_uuid: str) -> JSON:
        """
        Get an Anthropic API key.
        
        Args:
            api_key_uuid: UUID of the API key
        
        Returns:
            Dictionary containing API key details
        """
        response = self.client.genai.get_anthropic_api_key(
            api_key_uuid=api_key_uuid
        )
        return response
    
    def update_anthropic_api_key(
        self,
        api_key_uuid: str,
        name: Optional[str] = None,
        api_key: Optional[str] = None
    ) -> JSON:
        """
        Update an Anthropic API key.
        
        Args:
            api_key_uuid: UUID of the API key
            name: Optional new name
            api_key: Optional new API key value
        
        Returns:
            Dictionary containing updated API key details
        """
        body = {}
        if name is not None:
            body["name"] = name
        if api_key is not None:
            body["api_key"] = api_key
        
        response = self.client.genai.update_anthropic_api_key(
            api_key_uuid=api_key_uuid,
            body=body
        )
        return response
    
    def delete_anthropic_api_key(self, api_key_uuid: str) -> JSON:
        """
        Delete an Anthropic API key.
        
        Args:
            api_key_uuid: UUID of the API key to delete
        
        Returns:
            Dictionary containing deletion result
        """
        response = self.client.genai.delete_anthropic_api_key(
            api_key_uuid=api_key_uuid
        )
        return response

