"""
Workspaces service for managing DigitalOcean AI workspaces.
"""

from typing import Optional
from typing import MutableMapping, Any

from .base import DigitalOceanAPI

JSON = MutableMapping[str, Any]


class Workspaces(DigitalOceanAPI):
    """Service class for managing DigitalOcean AI workspaces."""
    
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
    
    def get_workspace(self, workspace_uuid: Optional[str] = None) -> JSON:
        """
        Retrieve an existing workspace.
        
        Args:
            workspace_uuid: UUID of the workspace (defaults to DEFAULT_WORKSPACE_UUID)
        
        Returns:
            Dictionary containing workspace details
        """
        if workspace_uuid is None:
            workspace_uuid = self.DEFAULT_WORKSPACE_UUID
        
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
        workspace_uuid: Optional[str] = None,
        name: Optional[str] = None,
        description: Optional[str] = None
    ) -> JSON:
        """
        Update a workspace.
        
        Args:
            workspace_uuid: UUID of the workspace (defaults to DEFAULT_WORKSPACE_UUID)
            name: Optional new name
            description: Optional new description
        
        Returns:
            Dictionary containing updated workspace details
        """
        if workspace_uuid is None:
            workspace_uuid = self.DEFAULT_WORKSPACE_UUID
        
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
    
    def delete_workspace(self, workspace_uuid: Optional[str] = None) -> JSON:
        """
        Delete a workspace.
        
        Args:
            workspace_uuid: UUID of the workspace to delete (defaults to DEFAULT_WORKSPACE_UUID)
        
        Returns:
            Dictionary containing deletion result
        """
        if workspace_uuid is None:
            workspace_uuid = self.DEFAULT_WORKSPACE_UUID
        
        response = self.client.genai.delete_workspace(workspace_uuid=workspace_uuid)
        return response

