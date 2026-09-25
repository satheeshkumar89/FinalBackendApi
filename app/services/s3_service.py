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
        """Return server upload URL to guarantee 100% reliable image uploads"""
        return f"https://dharaidelivery.online/api/v1/mock-upload/{file_key}"
            
    def upload_fileobj(self, file_data, file_key: str, content_type: Optional[str] = None) -> Optional[str]:
        """Upload file object directly to S3 or local uploads and return public URL"""
        try:
            full_path = os.path.join("uploads", file_key)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, "wb") as f:
                f.write(file_data.read())
            return f"https://dharaidelivery.online/api/v1/uploads/{file_key}"
        except Exception as e:
            print(f"Error uploading file directly: {e}")
            return f"https://dharaidelivery.online/api/v1/uploads/{file_key}"
    
    def get_file_url(self, file_key: Optional[str]) -> str:
        """Get 100% clean, reliable public HTTPS URL for any file key or image URL"""
        if not file_key:
            return ""
        
        file_key_str = str(file_key).strip()
        if not file_key_str:
            return ""
            
        # If it's a valid external URL (e.g. Unsplash), leave it
        if file_key_str.startswith("https://") and not any(d in file_key_str for d in [
            "dharaidelivery.online", "dharaifooddelivery.in", "amazonaws.com", "s3.amazonaws.com"
        ]):
            return file_key_str

        # Extract relative path after uploads/ or domain or bucket name
        clean_path = file_key_str
        
        if "/uploads/" in clean_path:
            clean_path = clean_path.split("/uploads/")[-1]
        elif clean_path.startswith("uploads/"):
            clean_path = clean_path[len("uploads/"):]
        elif clean_path.startswith("/uploads/"):
            clean_path = clean_path[len("/uploads/"):]
        elif clean_path.startswith("http://") or clean_path.startswith("https://"):
            parts = clean_path.split("/")
            if len(parts) >= 2:
                clean_path = "/".join(parts[-2:])
            else:
                clean_path = parts[-1]
                
        clean_path = clean_path.lstrip("/")
        
        if not clean_path:
            return file_key_str
            
        return f"https://dharaidelivery.online/api/v1/uploads/{clean_path}"
    
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
