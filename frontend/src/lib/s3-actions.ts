'use server'

interface S3Bucket {
  name: string;
  creation_date: string;
  object_count: number;
}

interface S3Object {
  key: string;
  size: number;
  last_modified: string;
  etag: string;
  storage_class: string;
}

interface S3ObjectContent {
  bucket_name: string;
  object_key: string;
  content_type: string;
  size: number;
  last_modified: string;
  content: any;
  error?: string;
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export async function getS3Buckets(): Promise<{ buckets: S3Bucket[] }> {
  try {
    const response = await fetch(`${API_BASE_URL}/s3/buckets`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error fetching S3 buckets:', error);
    throw error;
  }
}

export async function getBucketObjects(bucketName: string, prefix?: string, maxKeys?: number): Promise<{
  bucket_name: string;
  objects: S3Object[];
  is_truncated: boolean;
  total_count: number;
}> {
  try {
    const params = new URLSearchParams();
    if (prefix) params.append('prefix', prefix);
    if (maxKeys) params.append('max_keys', maxKeys.toString());

    const url = `${API_BASE_URL}/s3/buckets/${encodeURIComponent(bucketName)}/objects${params.toString() ? `?${params.toString()}` : ''}`;
    
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error fetching bucket objects:', error);
    throw error;
  }
}

export async function getObjectContent(bucketName: string, objectKey: string): Promise<S3ObjectContent> {
  try {
    const response = await fetch(`${API_BASE_URL}/s3/buckets/${encodeURIComponent(bucketName)}/objects/${encodeURIComponent(objectKey)}/content`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error fetching object content:', error);
    throw error;
  }
}

export async function testBucketConnection(bucketName: string): Promise<{
  bucket_name: string;
  accessible: boolean;
  message: string;
}> {
  try {
    const response = await fetch(`${API_BASE_URL}/s3/buckets/${encodeURIComponent(bucketName)}/test-connection`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error testing bucket connection:', error);
    throw error;
  }
}



export async function setEnvVariable(key: string, value: string): Promise<{
  key: string;
  value: string;
  success: boolean;
  message: string;
}> {
  try {
    const response = await fetch(`${API_BASE_URL}/env/variable`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ key, value }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error setting environment variable:', error);
    throw error;
  }
}

export async function setEnvVariables(variables: Record<string, string>): Promise<{
  variables: Record<string, string>;
  success: boolean;
  message: string;
}> {
  try {
    const response = await fetch(`${API_BASE_URL}/env/variables`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ variables }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error setting environment variables:', error);
    throw error;
  }
}
