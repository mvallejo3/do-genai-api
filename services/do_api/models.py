"""
Models service for managing DigitalOcean GenAI models.
"""

from typing import Optional, List
from typing import MutableMapping, Any

from .base import DigitalOceanAPI

JSON = MutableMapping[str, Any]


class Models(DigitalOceanAPI):
    """Service class for managing DigitalOcean GenAI models."""
    
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

