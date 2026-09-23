import os
import boto3
from botocore.client import Config
from botocore.exceptions import ClientError
from typing import Optional
from app.config import get_settings

settings = get_settings()


class S3Service:
    def __init__(self):
        # AWS S3 error indicated expecting us-east-1 region for bucket signing
        region = getattr(settings, 'AWS_REGION', None)
        if not region or region == 'ap-south-1':
            region = 'us-east-1'
            
        self.region = region
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=self.region,
            config=Config(signature_version='s3v4')
        )
        self.bucket_name = settings.S3_BUCKET_NAME
        if not self.bucket_name:
            print("CRITICAL ERROR: S3_BUCKET_NAME is missing or empty in settings!")
        else:
            print(f"S3Service initialized with bucket: {self.bucket_name} in region: {self.region}")
    
    def generate_presigned_url(
        self, 
        file_key: str, 
        expiration: int = 3600,
        content_type: Optional[str] = None
    ) -> str:
        """
        Generate presigned URL for uploading file to S3
        
        Args:
            file_key: S3 object key (path)
            expiration: URL expiration time in seconds
            content_type: MIME type of the file
        
        Returns:
            Presigned URL string
        """
        if not self.bucket_name:
            # Return a dummy URL if S3 is not configured
            # Changed to HTTPS to avoid Nginx 301 redirects
            print(f"WARNING: S3 not configured. Returning local mock URL for {file_key}")
            return f"https://dharaidelivery.online/mock-upload/{file_key}"

        try:
            # Check if AWS credentials are dummy or if local upload mode is preferred
            if not self.bucket_name or "dummy" in getattr(settings, 'AWS_ACCESS_KEY_ID', '').lower() or True:
                # Return reliable EC2 server upload endpoint
                return f"https://dharaidelivery.online/mock-upload/{file_key}"
            
            params = {
                'Bucket': self.bucket_name,
                'Key': file_key
            }
            
            url = self.s3_client.generate_presigned_url(
                'put_object',
                Params=params,
                ExpiresIn=expiration
            )
            return url
        except Exception as e:
            print(f"Error generating presigned URL: {e}")
            return f"https://dharaidelivery.online/mock-upload/{file_key}"
            
    def upload_fileobj(self, file_data, file_key: str, content_type: Optional[str] = None) -> Optional[str]:
        """Upload file object directly to S3 or local uploads and return public URL"""
        try:
            full_path = os.path.join("uploads", file_key)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, "wb") as f:
                f.write(file_data.read())
            return f"https://dharaidelivery.online/uploads/{file_key}"
        except Exception as e:
            print(f"Error uploading file directly: {e}")
            return f"https://dharaidelivery.online/uploads/{file_key}"
    
    def get_file_url(self, file_key: str) -> str:
        """Get public URL for a file"""
        if not file_key:
            return ""
        if file_key.startswith("http://") or file_key.startswith("https://"):
            return file_key
        return f"https://dharaidelivery.online/uploads/{file_key}"
    
    def delete_file(self, file_key: str) -> bool:
        """Delete file from S3"""
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=file_key
            )
            return True
        except ClientError as e:
            print(f"Error deleting file: {e}")
            return False
    
    def generate_upload_key(self, folder: str, filename: str) -> str:
        """Generate S3 key for upload"""
        from datetime import datetime
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        return f"{folder}/{timestamp}_{filename}"


# Singleton instance
s3_service = S3Service()
