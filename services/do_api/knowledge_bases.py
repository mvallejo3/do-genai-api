"""
Knowledge Bases service for managing DigitalOcean AI knowledge bases.
"""

from typing import Optional, List
from typing import MutableMapping, Any

from .base import DigitalOceanAPI

JSON = MutableMapping[str, Any]


class KnowledgeBases(DigitalOceanAPI):
    """Service class for managing DigitalOcean AI knowledge bases."""
    
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
            "project_id": self.DEFAULT_PROJECT_UUID,
            "embedding_model_uuid": "22652c2a-79ed-11ef-bf8f-4e013e2ddde4",
            "database_id": "eb400988-68af-4ad6-ad15-ab91b7e85625",
            "datasources": [{
                "spaces_data_source": {
                    "bucket_name": 'roami-bot',
                    "region": self.DEFAULT_REGION
                }
            }]
        }
        if description:
            body["description"] = description
        
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

