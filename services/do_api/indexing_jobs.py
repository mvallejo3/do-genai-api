"""
Indexing Jobs service for managing DigitalOcean AI indexing jobs.
"""

from typing import Optional, List
from typing import MutableMapping, Any

from .base import DigitalOceanAPI

JSON = MutableMapping[str, Any]


class IndexingJobs(DigitalOceanAPI):
    """Service class for managing DigitalOcean AI indexing jobs."""
    
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

