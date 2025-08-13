from fastapi import APIRouter, HTTPException, status
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from app.core.env_manager import env_manager
import json

router = APIRouter()

def get_s3_client():
    """Get S3 client using environment variables"""
    aws_access_key = env_manager.get_variable("AWS_ACCESS_KEY_ID")
    aws_secret_key = env_manager.get_variable("AWS_SECRET_ACCESS_KEY")
    aws_region = env_manager.get_variable("AWS_REGION")
    
    if not aws_access_key or not aws_secret_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="AWS credentials not configured. Please set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY."
        )
    
    try:
        return boto3.client(
            's3',
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            region_name=aws_region or 'us-east-1'
        )
    except NoCredentialsError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid AWS credentials"
        )

@router.get("/buckets")
async def list_buckets():
    """List all S3 buckets"""
    try:
        s3_client = get_s3_client()
        response = s3_client.list_buckets()
        
        buckets = []
        for bucket in response['Buckets']:
            bucket_name = bucket['Name']
            
            try:
                objects_response = s3_client.list_objects_v2(
                    Bucket=bucket_name,
                    MaxKeys=1000
                )
                object_count = objects_response.get('KeyCount', 0)
            except ClientError:
                object_count = 0
            
            buckets.append({
                "name": bucket_name,
                "creation_date": bucket['CreationDate'].isoformat(),
                "object_count": object_count
            })
        
        return {"buckets": buckets}
    
    except ClientError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"AWS Error: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing buckets: {str(e)}"
        )

@router.get("/buckets/{bucket_name}/objects")
async def list_bucket_objects(bucket_name: str, prefix: str = "", max_keys: int = 1000):
    """List objects in a specific S3 bucket"""
    try:
        s3_client = get_s3_client()
        
        kwargs = {
            'Bucket': bucket_name,
            'MaxKeys': max_keys
        }
        
        if prefix:
            kwargs['Prefix'] = prefix
        
        response = s3_client.list_objects_v2(**kwargs)
        
        objects = []
        if 'Contents' in response:
            for obj in response['Contents']:
                objects.append({
                    "key": obj['Key'],
                    "size": obj['Size'],
                    "last_modified": obj['LastModified'].isoformat(),
                    "etag": obj['ETag'].strip('"'),
                    "storage_class": obj.get('StorageClass', 'STANDARD')
                })
        
        return {
            "bucket_name": bucket_name,
            "objects": objects,
            "is_truncated": response.get('IsTruncated', False),
            "total_count": len(objects)
        }
    
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'NoSuchBucket':
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Bucket '{bucket_name}' not found"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"AWS Error: {str(e)}"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing objects: {str(e)}"
        )

@router.get("/buckets/{bucket_name}/objects/{object_key:path}/content")
async def get_object_content(bucket_name: str, object_key: str):
    """Get content of a specific S3 object (JSON files only)"""
    try:
        s3_client = get_s3_client()
        
        try:
            head_response = s3_client.head_object(Bucket=bucket_name, Key=object_key)
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Object '{object_key}' not found in bucket '{bucket_name}'"
                )
            raise
        
        file_size = head_response['ContentLength']
        if file_size > 10 * 1024 * 1024:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File too large. Maximum size is 10MB."
            )
        
        response = s3_client.get_object(Bucket=bucket_name, Key=object_key)
        content = response['Body'].read()
        
        try:
            text_content = content.decode('utf-8')
            
            if object_key.lower().endswith('.json'):
                try:
                    json_content = json.loads(text_content)
                    return {
                        "bucket_name": bucket_name,
                        "object_key": object_key,
                        "content_type": "json",
                        "size": file_size,
                        "last_modified": head_response['LastModified'].isoformat(),
                        "content": json_content
                    }
                except json.JSONDecodeError:
                    return {
                        "bucket_name": bucket_name,
                        "object_key": object_key,
                        "content_type": "text",
                        "size": file_size,
                        "last_modified": head_response['LastModified'].isoformat(),
                        "content": text_content,
                        "error": "Invalid JSON format"
                    }
            else:
                return {
                    "bucket_name": bucket_name,
                    "object_key": object_key,
                    "content_type": "text",
                    "size": file_size,
                    "last_modified": head_response['LastModified'].isoformat(),
                    "content": text_content
                }
        
        except UnicodeDecodeError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File is not a text file or uses unsupported encoding"
            )
    
    except ClientError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"AWS Error: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting object content: {str(e)}"
        )

@router.post("/buckets/{bucket_name}/test-connection")
async def test_bucket_connection(bucket_name: str):
    """Test connection to a specific S3 bucket"""
    try:
        s3_client = get_s3_client()
        
        s3_client.head_bucket(Bucket=bucket_name)
        
        return {
            "bucket_name": bucket_name,
            "accessible": True,
            "message": f"Successfully connected to bucket '{bucket_name}'"
        }
    
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == '404':
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Bucket '{bucket_name}' not found or not accessible"
            )
        elif error_code == '403':
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied to bucket '{bucket_name}'"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"AWS Error: {str(e)}"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error testing bucket connection: {str(e)}"
        )

@router.get("/aws-config/status")
async def get_aws_config_status():
    """Check if AWS credentials are configured"""
    aws_access_key = env_manager.get_variable("AWS_ACCESS_KEY_ID")
    aws_secret_key = env_manager.get_variable("AWS_SECRET_ACCESS_KEY")
    aws_region = env_manager.get_variable("AWS_REGION")
    
    return {
        "configured": bool(aws_access_key and aws_secret_key),
        "has_access_key": bool(aws_access_key),
        "has_secret_key": bool(aws_secret_key),
        "region": aws_region
    }
