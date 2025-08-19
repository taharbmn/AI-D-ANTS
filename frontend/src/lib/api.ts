import axios from 'axios';

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use(
  (config) => {
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

export default api;

// Anomalies API functions
export interface CreateTreeStructureRequest {
  folder_paths: string[];
}

export interface TreeStructureResponse {
  response: any;
  success: boolean;
  status: number;
}

export const createTreeStructure = async (folderPaths: string[]): Promise<TreeStructureResponse> => {
  try {
    const response = await api.post('/anomalies/create_tree_structure', {
      folder_paths: folderPaths
    });
    return response.data;
  } catch (error) {
    console.error('Error creating tree structure:', error);
    throw error;
  }
};

export const getProcessedTreeStructure = async (): Promise<TreeStructureResponse> => {
  try {
    const response = await api.get('/anomalies/processed_tree_structure');
    return response.data;
  } catch (error) {
    console.error('Error fetching processed tree structure:', error);
    throw error;
  }
};
