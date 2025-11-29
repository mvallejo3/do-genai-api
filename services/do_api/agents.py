"""
Agents service for managing DigitalOcean AI agents.
"""

from typing import Optional, List
from typing import MutableMapping, Any

from .base import DigitalOceanAPI

JSON = MutableMapping[str, Any]


class Agents(DigitalOceanAPI):
    """Service class for managing DigitalOcean AI agents."""
    
    def create_agent(
        self,
        name: str,
        model_uuid: Optional[str] = None,
        workspace_uuid: Optional[str] = None,
        region: Optional[str] = None,
        description: Optional[str] = None,
        instructions: Optional[str] = None,
        project_id: Optional[str] = None,
        **kwargs
    ) -> JSON:
        """
        Create a new agent.
        
        Args:
            name: Name of the agent
            model_uuid: UUID of the model to use (defaults to DEFAULT_MODEL_UUID)
            workspace_uuid: UUID of the workspace (defaults to DEFAULT_WORKSPACE_UUID)
            region: Region where the agent will be deployed (defaults to DEFAULT_REGION)
            description: Optional description
            instructions: Optional system instructions
            project_id: Optional project ID (defaults to DEFAULT_PROJECT_UUID)
            **kwargs: Additional agent configuration options
        
        Returns:
            Dictionary containing agent details
        
        Raises:
            RuntimeError: If agent creation fails with detailed error message
        """
        if model_uuid is None:
            model_uuid = self.DEFAULT_MODEL_UUID
        if workspace_uuid is None:
            workspace_uuid = self.DEFAULT_WORKSPACE_UUID
        if region is None:
            region = self.DEFAULT_REGION
        if project_id is None:
            project_id = self.DEFAULT_PROJECT_UUID
        
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
        workspace_uuid: Optional[str] = None
    ) -> JSON:
        """
        Move agents to a different workspace.
        
        Args:
            agent_uuids: List of agent UUIDs to move
            workspace_uuid: UUID of the target workspace (defaults to DEFAULT_WORKSPACE_UUID)
        
        Returns:
            Dictionary containing update result
        """
        if workspace_uuid is None:
            workspace_uuid = self.DEFAULT_WORKSPACE_UUID
        
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

