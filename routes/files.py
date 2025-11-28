"""
File management routes blueprint.
"""
import os
import tempfile
from pathlib import Path
from flask import Blueprint, request
from middleware.decorators import handle_response
from services.Spaces import Spaces

files_bp = Blueprint('files', __name__, url_prefix='/api/files')


@files_bp.route('', methods=['GET'])
@handle_response
def list_files():
    """
    List files in the knowledge base bucket.
    
    Query parameters:
        prefix (str, optional): Prefix to filter objects by (e.g., folder path)
        max_keys (int, optional): Maximum number of keys to return
    
    Returns:
        JSON response with list of files and their metadata
    """
    prefix = request.args.get('prefix', '')
    max_keys = request.args.get('max_keys', type=int)
    
    kb = Spaces()
    files = kb.list_files(prefix=prefix, max_keys=max_keys)
    
    return {
        'files': files,
        'count': len(files)
    }


@files_bp.route('', methods=['POST'])
@handle_response
def upload_file():
    """
    Upload one or more files to the knowledge base bucket.
    
    Request:
        multipart/form-data with:
            file (file, required): One or more files to upload (can be multiple files with same field name)
        Query parameters:
            folder (str, optional): Folder/path prefix in the bucket (default: '')
    
    Returns:
        JSON response with upload details for all files including their keys
    """
    # Get all files from request (supports single or multiple files)
    files = request.files.getlist('file')
    
    # Check if any files were provided
    if not files or len(files) == 0:
        raise ValueError("No files provided. Please include at least one 'file' field in the request.")
    
    # Filter out empty file entries
    valid_files = [f for f in files if f.filename and f.filename.strip()]
    
    if not valid_files:
        raise ValueError("No valid files selected. Please provide at least one file with a filename.")
    
    # Get optional folder parameter
    folder = request.args.get('folder', '')
    
    # Initialize KnowledgeBase
    kb = Spaces()
    
    # Track temporary files for cleanup
    temp_paths = []
    results = []
    
    try:
        # Process each file
        for file in valid_files:
            temp_file = None
            temp_path = None
            
            try:
                # Save uploaded file to temporary location
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename or '').suffix)
                temp_path = temp_file.name
                temp_paths.append(temp_path)
                file.save(temp_path)
                temp_file.close()
                
                # Upload to Spaces using KnowledgeBase
                key = kb.upload_file(
                    file_path=temp_path,
                    folder=folder,
                    object_name=file.filename
                )
                
                results.append({
                    'filename': file.filename,
                    'key': key,
                    'success': True,
                    'error': None
                })
                
            except Exception as e:
                # Track failed uploads but continue with other files
                results.append({
                    'filename': file.filename,
                    'key': None,
                    'success': False,
                    'error': str(e)
                })
        
        # Determine overall success message
        successful = sum(1 for r in results if r['success'])
        total = len(results)
        
        if successful == total:
            message = f'All {total} file(s) uploaded successfully'
        elif successful > 0:
            message = f'{successful} of {total} file(s) uploaded successfully'
        else:
            message = 'No files were uploaded successfully'
        
        return {
            'message': message,
            'results': results,
            'successful': successful,
            'failed': total - successful,
            'total': total,
            'folder': folder if folder else None
        }
        
    finally:
        # Clean up all temporary files
        for temp_path in temp_paths:
            if temp_path and os.path.exists(temp_path):
                try:
                    os.unlink(temp_path)
                except Exception:
                    pass  # Ignore errors during cleanup


@files_bp.route('', methods=['DELETE'])
@handle_response
def delete_file():
    """
    Delete a file from the knowledge base bucket.
    
    Query parameters:
        key (str, required): The key/path of the file to delete in Spaces
    
    Returns:
        JSON response confirming deletion
    """
    key = request.args.get('key')
    
    if not key:
        raise ValueError("Query parameter 'key' is required")
    
    if not isinstance(key, str) or not key.strip():
        raise ValueError("Key cannot be empty")
    
    kb = Spaces()
    kb.delete_file(key)
    
    return {
        'message': 'File deleted successfully',
        'key': key
    }

