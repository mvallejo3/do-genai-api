"""
DigitalOcean Spaces uploader service for uploading files to Spaces buckets.
"""

import os
from typing import Optional, List, Dict, Any
from pathlib import Path
import boto3
import botocore.config
from botocore.exceptions import ClientError


class Spaces:
    """Uploads files to DigitalOcean Spaces."""
    
    def __init__(
        self,
        bucket_name: str = os.getenv('SPACES_BUCKET_NAME', 'do-genai-api'),
        region: str = os.getenv('SPACES_REGION', 'tor1'),
        access_key: Optional[str] = None,
        secret_key: Optional[str] = None,
        endpoint_url: Optional[str] = None,
        api_token: Optional[str] = None
    ):
        """
        Initialize Spaces Uploader.
        
        Args:
            bucket_name: Name of the Spaces bucket (default: 'do-genai-api')
            region: DigitalOcean region (default: 'tor1')
            access_key: Spaces access key (defaults to SPACES_KEY env var)
            secret_key: Spaces secret key (defaults to SPACES_SECRET env var)
            endpoint_url: Custom endpoint URL (defaults to region-based URL)
            api_token: DigitalOcean API token for re-indexing (defaults to DIGITALOCEAN_API_TOKEN env var)
        """
        self.bucket_name = bucket_name
        self.region = region
        
        # Get credentials from parameters or environment variables
        self.access_key = access_key or os.getenv('SPACES_KEY')
        self.secret_key = secret_key or os.getenv('SPACES_SECRET')
        
        if not self.access_key or not self.secret_key:
            raise ValueError(
                "Spaces credentials not found. Set SPACES_KEY and SPACES_SECRET "
                "environment variables or pass them as parameters."
            )
        
        # Get API token for DigitalOcean API calls (optional, only needed for re-indexing)
        self.api_token = api_token or os.getenv('DIGITALOCEAN_API_TOKEN')
        
        # Construct endpoint URL if not provided
        if endpoint_url is None:
            endpoint_url = f'https://{region}.digitaloceanspaces.com'
        
        # Create S3 client configured for DigitalOcean Spaces
        self.client = boto3.client(
            's3',
            endpoint_url=endpoint_url,
            config=botocore.config.Config(s3={'addressing_style': 'virtual'}),
            region_name=region,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key
        )
    
    def upload_file(
        self,
        file_path: str,
        folder: str = '',
        object_name: Optional[str] = None,
        acl: str = 'private'
    ) -> str:
        """
        Upload a file to DigitalOcean Spaces.
        
        Args:
            file_path: Local path to the file to upload
            folder: Folder/path prefix in the bucket (default: 'csv-exports')
            object_name: Name for the object in Spaces. If None, uses filename from file_path
            acl: Access control level ('private', 'public-read', etc.)
        
        Returns:
            The full key/path of the uploaded object in Spaces
        
        Raises:
            FileNotFoundError: If the file doesn't exist
            ClientError: If the upload fails
        """
        file_path_obj = Path(file_path)
        
        if not file_path_obj.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Determine object name
        if object_name is None:
            object_name = file_path_obj.name
        
        # Construct full key with folder prefix
        key = f"{folder}/{object_name}" if folder else object_name
        
        try:
            # Upload file
            with open(file_path, 'rb') as file_data:
                self.client.put_object(
                    Bucket=self.bucket_name,
                    Key=key,
                    Body=file_data,
                    ACL=acl
                )
            
            return key
            
        except ClientError as e:
            raise RuntimeError(f"Failed to upload file to Spaces: {str(e)}")
    
    def list_files(
        self,
        prefix: str = '',
        max_keys: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        List files in the DigitalOcean Spaces bucket.
        
        Args:
            prefix: Prefix to filter objects by (e.g., folder path). Defaults to empty string.
            max_keys: Maximum number of keys to return. If None, returns all keys.
        
        Returns:
            List of dictionaries containing file information:
            - Key: The object key/path
            - LastModified: Last modified timestamp
            - Size: File size in bytes
            - ETag: Entity tag for the object
        
        Raises:
            ClientError: If the list operation fails
        """
        files = []
        paginator = self.client.get_paginator('list_objects_v2')
        
        pagination_config = {}
        if max_keys:
            pagination_config['MaxItems'] = max_keys
        
        try:
            page_iterator = paginator.paginate(
                Bucket=self.bucket_name,
                Prefix=prefix,
                **pagination_config
            )
            
            for page in page_iterator:
                if 'Contents' in page:
                    for obj in page['Contents']:
                        files.append({
                            'Key': obj['Key'],
                            'LastModified': obj['LastModified'],
                            'Size': obj['Size'],
                            'ETag': obj['ETag']
                        })
            
            return files
            
        except ClientError as e:
            raise RuntimeError(f"Failed to list files in Spaces: {str(e)}")
    
    def upload_files(
        self,
        file_paths: List[str],
        folder: str = '',
        acl: str = 'private'
    ) -> List[Dict[str, Any]]:
        """
        Upload multiple files to DigitalOcean Spaces in one go.
        
        Args:
            file_paths: List of local paths to files to upload
            folder: Folder/path prefix in the bucket (default: '')
            acl: Access control level ('private', 'public-read', etc.)
        
        Returns:
            List of dictionaries containing upload results:
            - file_path: Original local file path
            - key: The full key/path of the uploaded object in Spaces
            - success: Boolean indicating if upload was successful
            - error: Error message if upload failed (None if successful)
        
        Raises:
            FileNotFoundError: If any file doesn't exist
        """
        results = []
        
        # Validate all files exist first
        for file_path in file_paths:
            file_path_obj = Path(file_path)
            if not file_path_obj.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
        
        # Upload each file
        for file_path in file_paths:
            file_path_obj = Path(file_path)
            object_name = file_path_obj.name
            
            # Construct full key with folder prefix
            key = f"{folder}/{object_name}" if folder else object_name
            
            try:
                # Upload file
                with open(file_path, 'rb') as file_data:
                    self.client.put_object(
                        Bucket=self.bucket_name,
                        Key=key,
                        Body=file_data,
                        ACL=acl
                    )
                
                results.append({
                    'file_path': file_path,
                    'key': key,
                    'success': True,
                    'error': None
                })
                
            except ClientError as e:
                results.append({
                    'file_path': file_path,
                    'key': key,
                    'success': False,
                    'error': str(e)
                })
        
        return results
    
    def delete_file(self, key: str) -> bool:
        """
        Delete a single file from DigitalOcean Spaces.
        
        Args:
            key: The key/path of the object to delete in Spaces
        
        Returns:
            True if deletion was successful
        
        Raises:
            RuntimeError: If the deletion fails
        """
        try:
            self.client.delete_object(
                Bucket=self.bucket_name,
                Key=key
            )
            return True
            
        except ClientError as e:
            raise RuntimeError(f"Failed to delete file from Spaces: {str(e)}")
    
    def delete_files(self, keys: List[str]) -> List[Dict[str, Any]]:
        """
        Delete multiple files from DigitalOcean Spaces in one go.
        
        Args:
            keys: List of keys/paths of objects to delete in Spaces
        
        Returns:
            List of dictionaries containing deletion results:
            - key: The key/path of the object
            - success: Boolean indicating if deletion was successful
            - error: Error message if deletion failed (None if successful)
        """
        if not keys:
            return []
        
        results = []
        
        # S3 delete_objects can handle up to 1000 objects per request
        # Split into batches if needed
        batch_size = 1000
        for i in range(0, len(keys), batch_size):
            batch = keys[i:i + batch_size]
            
            # Prepare objects for deletion
            objects_to_delete = [{'Key': key} for key in batch]
            
            try:
                response = self.client.delete_objects(
                    Bucket=self.bucket_name,
                    Delete={
                        'Objects': objects_to_delete,
                        'Quiet': False  # Return deleted objects in response
                    }
                )
                
                # Track successfully deleted objects
                deleted_keys = {obj['Key'] for obj in response.get('Deleted', [])}
                
                # Track errors
                errors = {err['Key']: err['Message'] for err in response.get('Errors', [])}
                
                # Build results for this batch
                for key in batch:
                    if key in deleted_keys:
                        results.append({
                            'key': key,
                            'success': True,
                            'error': None
                        })
                    elif key in errors:
                        results.append({
                            'key': key,
                            'success': False,
                            'error': errors[key]
                        })
                    else:
                        # Shouldn't happen, but handle edge case
                        results.append({
                            'key': key,
                            'success': False,
                            'error': 'Unknown error during deletion'
                        })
                        
            except ClientError as e:
                # If the entire batch fails, mark all as failed
                for key in batch:
                    results.append({
                        'key': key,
                        'success': False,
                        'error': str(e)
                    })
        
        return results
    
    def create_bucket(
        self,
        bucket_name: str,
        region: Optional[str] = None,
        acl: str = 'private'
    ) -> bool:
        """
        Create a new bucket in DigitalOcean Spaces.
        
        Args:
            bucket_name: Name of the bucket to create (must be globally unique)
            region: DigitalOcean region for the bucket. If None, uses self.region
            acl: Access control level ('private', 'public-read', etc.)
        
        Returns:
            True if bucket creation was successful
        
        Raises:
            RuntimeError: If the bucket creation fails
            ValueError: If bucket name is invalid
        """
        if not bucket_name:
            raise ValueError("Bucket name cannot be empty")
        
        try:
            # Create bucket
            # Note: The bucket will be created in the region specified by the client's endpoint URL
            # If a different region is needed, create a new Spaces instance with that region
            confirmation = self.client.create_bucket(
                Bucket=bucket_name,
                ACL=acl,
                CreateBucketConfiguration={
                    'LocationConstraint': region if region else self.region
                }
            )
            
            return confirmation
            
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', '')
            if error_code == 'BucketAlreadyExists':
                raise RuntimeError(f"Bucket '{bucket_name}' already exists")
            elif error_code == 'BucketAlreadyOwnedByYou':
                raise RuntimeError(f"Bucket '{bucket_name}' is already owned by you")
            else:
                raise RuntimeError(f"Failed to create bucket '{bucket_name}': {str(e)}")
    
    def delete_bucket(self, bucket_name: str) -> bool:
        """
        Delete a bucket from DigitalOcean Spaces.
        
        Args:
            bucket_name: Name of the bucket to delete
        
        Returns:
            True if bucket deletion was successful
        
        Raises:
            RuntimeError: If the bucket deletion fails
            ValueError: If bucket name is invalid
        """
        if not bucket_name:
            raise ValueError("Bucket name cannot be empty")
        
        try:
            # Delete bucket (must be empty first)
            self.client.delete_bucket(Bucket=bucket_name)
            return True
            
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', '')
            if error_code == 'NoSuchBucket':
                raise RuntimeError(f"Bucket '{bucket_name}' does not exist")
            elif error_code == 'BucketNotEmpty':
                raise RuntimeError(f"Bucket '{bucket_name}' is not empty. Delete all objects first.")
            else:
                raise RuntimeError(f"Failed to delete bucket '{bucket_name}': {str(e)}")
    
    def get_bucket_info(self, bucket_name: str) -> Dict[str, Any]:
        """
        Get information about a bucket in DigitalOcean Spaces.
        
        Args:
            bucket_name: Name of the bucket to get information for
        
        Returns:
            Dictionary containing bucket information:
            - Name: Bucket name
            - CreationDate: When the bucket was created
            - Location: Region where the bucket is located
        
        Raises:
            RuntimeError: If the bucket information retrieval fails
            ValueError: If bucket name is invalid
        """
        if not bucket_name:
            raise ValueError("Bucket name cannot be empty")
        
        try:
            # Get bucket location
            location_response = self.client.get_bucket_location(Bucket=bucket_name)
            
            # Get bucket ACL (access control list)
            try:
                acl_response = self.client.get_bucket_acl(Bucket=bucket_name)
                owner = acl_response.get('Owner', {})
            except ClientError:
                owner = {}
            
            # Try to get bucket creation date by listing objects
            # Note: S3/Spaces doesn't provide creation date directly, so we'll use the first object's date
            # or return None if bucket is empty
            creation_date = None
            try:
                objects = self.client.list_objects_v2(Bucket=bucket_name, MaxKeys=1)
                if 'Contents' in objects and len(objects['Contents']) > 0:
                    creation_date = objects['Contents'][0]['LastModified']
            except ClientError:
                pass
            
            return {
                'Name': bucket_name,
                'Location': location_response.get('LocationConstraint', self.region),
                'CreationDate': creation_date,
                'Owner': owner
            }
            
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', '')
            if error_code == 'NoSuchBucket':
                raise RuntimeError(f"Bucket '{bucket_name}' does not exist")
            else:
                raise RuntimeError(f"Failed to get bucket information for '{bucket_name}': {str(e)}")
    
    def list_buckets(self) -> List[Dict[str, Any]]:
        """
        List all buckets in DigitalOcean Spaces.
        
        Returns:
            List of dictionaries containing bucket information:
            - Name: Bucket name
            - CreationDate: When the bucket was created
            - Location: Region where the bucket is located
        
        Raises:
            RuntimeError: If the bucket listing fails
        """
        try:
            response = self.client.list_buckets()
            # buckets = []
            
            # for bucket in response.get('Buckets', []):
            #     bucket_name = bucket['Name']
            #     # Get location for each bucket
            #     try:
            #         # Create a temporary client to get bucket location
            #         # Note: We need to check each bucket's location
            #         location_response = self.client.get_bucket_location(Bucket=bucket_name)
            #         location = location_response.get('LocationConstraint', 'unknown')
            #     except ClientError:
            #         location = 'unknown'
                
            #     buckets.append({
            #         'Name': bucket_name,
            #         'CreationDate': bucket.get('CreationDate'),
            #         'Location': location
            #     })
            
            return response
            
        except ClientError as e:
            raise RuntimeError(f"Failed to list buckets: {str(e)}")