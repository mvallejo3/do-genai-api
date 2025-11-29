"""
Base class for DigitalOcean AI API services.
"""

import os
from typing import Optional
from pydo import Client


class DigitalOceanAPI:
    """
    Base class for DigitalOcean AI API services.
    
    Provides shared functionality including:
    - API client initialization
    - Default configuration values
    """
    
    # Default values from environment variables
    DEFAULT_MODEL_UUID = os.getenv('DEFAULT_MODEL_UUID', '')
    DEFAULT_PROJECT_UUID = os.getenv('DEFAULT_PROJECT_UUID', '')
    DEFAULT_WORKSPACE_UUID = os.getenv('DEFAULT_WORKSPACE_UUID', '')
    DEFAULT_REGION = os.getenv('DEFAULT_REGION', os.getenv('SPACES_REGION', 'tor1'))
    
    def __init__(self, api_token: Optional[str] = None):
        """
        Initialize DigitalOcean AI client.
        
        Args:
            api_token: DigitalOcean API token (defaults to DIGITALOCEAN_API_TOKEN env var)
        
        Raises:
            ValueError: If API token is not provided and not found in environment
        """
        if not self.DEFAULT_WORKSPACE_UUID or not self.DEFAULT_MODEL_UUID or not self.DEFAULT_REGION:
            raise ValueError("DEFAULT_WORKSPACE_UUID, DEFAULT_MODEL_UUID, and DEFAULT_REGION must be set in the environment variables")
        
        self.api_token = api_token or os.getenv('DIGITALOCEAN_API_TOKEN')
        
        if not self.api_token:
            raise ValueError(
                "DigitalOcean API token not found. Set DIGITALOCEAN_API_TOKEN "
                "environment variable or pass api_token parameter."
            )
        
        self.client = Client(token=self.api_token)

