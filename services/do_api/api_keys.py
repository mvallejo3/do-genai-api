"""
API Keys service for managing DigitalOcean GenAI API keys.
"""

from typing import Optional
from typing import MutableMapping, Any

from .base import DigitalOceanAPI

JSON = MutableMapping[str, Any]


class APIKeys(DigitalOceanAPI):
    """Service class for managing DigitalOcean GenAI API keys."""
    
    # Agent API Keys
    
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
    
    # Model API Keys
    
    def create_model_api_key(
        self,
        name: str,
        model_uuid: Optional[str] = None
    ) -> JSON:
        """
        Create an API key for a model.
        
        Args:
            name: Name for the API key
            model_uuid: UUID of the model (defaults to DEFAULT_MODEL_UUID)
        
        Returns:
            Dictionary containing API key details
        """
        if model_uuid is None:
            model_uuid = self.DEFAULT_MODEL_UUID
        
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
    
    # OpenAI API Keys
    
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
    
    # Anthropic API Keys
    
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

