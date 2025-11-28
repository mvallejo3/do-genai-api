"""
Databases service for managing DigitalOcean databases (OpenSearch).
"""

from typing import MutableMapping, Any

from .base import DigitalOceanAPI

JSON = MutableMapping[str, Any]


class Databases(DigitalOceanAPI):
    """Service class for managing DigitalOcean OpenSearch databases."""
    
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

