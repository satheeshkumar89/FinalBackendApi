import boto3
from botocore.exceptions import ClientError
from datetime import timedelta
from typing import Optional
from app.config import get_settings

settings = get_settings()


class S3Service:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
        self.bucket_name = settings.S3_BUCKET_NAME
        if not self.bucket_name:
            print("CRITICAL ERROR: S3_BUCKET_NAME is missing or empty in settings!")
        else:
            print(f"S3Service initialized with bucket: {self.bucket_name}")
    
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
            return f"https://dharaifooddelivery.in/mock-upload/{file_key}"

        try:
            params = {
                'Bucket': self.bucket_name,
                'Key': file_key
            }
            
            if content_type:
                params['ContentType'] = content_type
            
            url = self.s3_client.generate_presigned_url(
                'put_object',
                Params=params,
                ExpiresIn=expiration
            )
            return url
        except Exception as e:
            print(f"Error generating presigned URL: {e}")
            # Fallback to dummy URL even on AWS errors to keep the flow alive during testing
            return f"https://dharaifooddelivery.in/mock-upload/{file_key}"
    
    def get_file_url(self, file_key: str) -> str:
        """Get public URL for a file in S3"""
        if not self.bucket_name:
            return f"http://dharaifooddelivery.in/static/placeholder.png"
        return f"https://{self.bucket_name}.s3.{settings.AWS_REGION}.amazonaws.com/{file_key}"
    
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
