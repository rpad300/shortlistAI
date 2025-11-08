"""
Supabase Storage service for file uploads.

Handles uploading and managing files (CVs, job postings, etc.) in Supabase storage buckets.
"""

import os
from typing import Optional, Tuple
from uuid import uuid4
from datetime import datetime
from database import get_supabase_client
import logging

logger = logging.getLogger(__name__)


class SupabaseStorageService:
    """
    Service for managing file storage in Supabase.
    """
    
    def __init__(self):
        """Initialize storage service with Supabase client."""
        self.client = get_supabase_client()
        
        # Bucket names
        self.cv_bucket = "cvs"
        self.job_posting_bucket = "job-postings"
        
        # Ensure buckets exist (TODO: create if not exist)
    
    async def upload_cv(
        self,
        file_content: bytes,
        filename: str,
        candidate_id: str
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Upload CV file to storage.
        
        Args:
            file_content: Binary content of the file
            filename: Original filename
            candidate_id: ID of the candidate
            
        Returns:
            Tuple of (success, file_url, error_message)
        """
        try:
            # Generate unique filename
            file_extension = os.path.splitext(filename)[1]
            unique_filename = f"{candidate_id}/{uuid4()}{file_extension}"
            
            # Upload to Supabase storage
            result = self.client.storage.from_(self.cv_bucket).upload(
                path=unique_filename,
                file=file_content,
                file_options={"content-type": self._get_content_type(file_extension)}
            )
            
            # Get public URL
            file_url = self.client.storage.from_(self.cv_bucket).get_public_url(unique_filename)
            
            logger.info(f"CV uploaded successfully: {unique_filename}")
            return True, file_url, None
            
        except Exception as e:
            logger.error(f"Failed to upload CV: {e}")
            return False, None, str(e)
    
    async def upload_job_posting(
        self,
        file_content: bytes,
        filename: str,
        job_posting_id: str
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Upload job posting file to storage.
        
        Args:
            file_content: Binary content of the file
            filename: Original filename
            job_posting_id: ID of the job posting
            
        Returns:
            Tuple of (success, file_url, error_message)
        """
        try:
            file_extension = os.path.splitext(filename)[1]
            unique_filename = f"{job_posting_id}/{uuid4()}{file_extension}"
            
            result = self.client.storage.from_(self.job_posting_bucket).upload(
                path=unique_filename,
                file=file_content,
                file_options={"content-type": self._get_content_type(file_extension)}
            )
            
            file_url = self.client.storage.from_(self.job_posting_bucket).get_public_url(unique_filename)
            
            logger.info(f"Job posting uploaded successfully: {unique_filename}")
            return True, file_url, None
            
        except Exception as e:
            logger.error(f"Failed to upload job posting: {e}")
            return False, None, str(e)
    
    def _get_content_type(self, file_extension: str) -> str:
        """
        Get content type for file extension.
        
        Args:
            file_extension: File extension (e.g., '.pdf')
            
        Returns:
            MIME type string
        """
        content_types = {
            ".pdf": "application/pdf",
            ".doc": "application/msword",
            ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            ".txt": "text/plain"
        }
        return content_types.get(file_extension.lower(), "application/octet-stream")
    
    async def delete_file(self, bucket: str, filepath: str) -> bool:
        """
        Delete file from storage.
        
        Args:
            bucket: Bucket name
            filepath: Path to file in bucket
            
        Returns:
            True if deleted successfully
        """
        try:
            self.client.storage.from_(bucket).remove([filepath])
            logger.info(f"File deleted: {bucket}/{filepath}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete file: {e}")
            return False


# Global storage service instance
_storage_service: Optional[SupabaseStorageService] = None


def get_storage_service() -> SupabaseStorageService:
    """
    Get global storage service instance.
    
    Returns:
        SupabaseStorageService singleton
    """
    global _storage_service
    if _storage_service is None:
        _storage_service = SupabaseStorageService()
    return _storage_service

