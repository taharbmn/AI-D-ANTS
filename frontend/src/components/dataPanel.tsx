"use client";
/* eslint-disable */
import React, { useState, useEffect } from 'react';
import { 
  CloudIcon, 
  ArrowDown01Icon, 
  ArrowUp01Icon, 
  FolderIcon,
  FileIcon,
  Loading03Icon,
  DatabaseIcon,
  SearchIcon,
  DownloadIcon,
  EyeIcon,
  AlertCircleIcon,
} from "@hugeicons/core-free-icons";
import { HugeiconsIcon } from "@hugeicons/react";
import JsonView from '@uiw/react-json-view';
import {
  getS3Buckets,
  getBucketObjects,
  getObjectContent,
  testBucketConnection
} from '../lib/s3-actions';

interface S3Object {
  key: string;
  size: number;
  last_modified: string;
  etag: string;
  storage_class: string;
}

interface Bucket {
  name: string;
  creation_date?: string;
  object_count?: number;
  files: string[];
  objects?: S3Object[];
}

interface DataPanelProps {
  onBucketSelect?: (bucket: Bucket) => void;
  selectedBuckets?: Bucket[];
}

const DataPanel: React.FC<DataPanelProps> = ({ onBucketSelect, selectedBuckets = [] }) => {
  const [s3Url, setS3Url] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [buckets, setBuckets] = useState<Bucket[]>([]);
  const [expandedBucket, setExpandedBucket] = useState<string | null>(null);
  const [selectedFile, setSelectedFile] = useState<string | null>(null);
  const [jsonData, setJsonData] = useState<any | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [isLoadingFile, setIsLoadingFile] = useState(false);
  const [awsConfigured, setAwsConfigured] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isLoadingBuckets, setIsLoadingBuckets] = useState(false);



  const extractBucketNameFromUrl = (url: string): string => {
    if (url.startsWith('s3://')) {
      return url.replace('s3://', '').split('/')[0];
    }
    
    if (url.includes('.s3.') && url.includes('.amazonaws.com')) {
      const match = url.match(/https?:\/\/([^.]+)\.s3\./);
      return match ? match[1] : url;
    }
    
    return url;
  };

  const handlePullBuckets = async () => {
    if (!s3Url.trim()) {
      setError('Please enter an S3 URL or bucket name');
      return;
    }

    if (!awsConfigured) {
      setError('AWS credentials not configured in backend. Please check your backend .env file.');
      return;
    }
    
    setIsLoadingBuckets(true);
    setError(null);

    try {
      const bucketName = extractBucketNameFromUrl(s3Url.trim());
      
      await testBucketConnection(bucketName);

      if (bucketName) {
        const objectsResponse = await getBucketObjects(bucketName);
        
        const bucket: Bucket = {
          name: bucketName,
          files: objectsResponse.objects.map(obj => obj.key),
          objects: objectsResponse.objects
        };

        setBuckets([bucket]);
      } else {
        const response = await getS3Buckets();
        const bucketsWithFiles: Bucket[] = [];

        for (const bucket of response.buckets) {
          try {
            const objectsResponse = await getBucketObjects(bucket.name, '', 100);
            bucketsWithFiles.push({
              name: bucket.name,
              creation_date: bucket.creation_date,
              object_count: bucket.object_count,
              files: objectsResponse.objects.map(obj => obj.key),
              objects: objectsResponse.objects
            });
          } catch (error) {
            bucketsWithFiles.push({
              name: bucket.name,
              creation_date: bucket.creation_date,
              object_count: bucket.object_count,
              files: [],
              objects: []
            });
          }
        }

        setBuckets(bucketsWithFiles);
      }
    } catch (error) {
      setError(error instanceof Error ? error.message : 'Failed to fetch S3 data');
      setBuckets([]);
    } finally {
      setIsLoadingBuckets(false);
    }
  };

  const handleBucketClick = async (bucketName: string) => {
    if (expandedBucket === bucketName) {
      setExpandedBucket(null);
    } else {
      setExpandedBucket(bucketName);
      setSelectedFile(null);
      setJsonData(null);

      const bucket = buckets.find(b => b.name === bucketName);
      if (bucket && (!bucket.objects || bucket.objects.length === 0) && bucket.files.length === 0) {
        try {
          const objectsResponse = await getBucketObjects(bucketName);
          setBuckets(prev => prev.map(b => 
            b.name === bucketName 
              ? { ...b, files: objectsResponse.objects.map(obj => obj.key), objects: objectsResponse.objects }
              : b
          ));
        } catch (error) {
          console.error('Error loading bucket objects:', error);
        }
      }
    }
  };

  const handleFileClick = async (bucketName: string, fileName: string) => {
    if (selectedFile === fileName) {
      setSelectedFile(null);
      setJsonData(null);
    } else {
      setSelectedFile(fileName);
      setIsLoadingFile(true);
      setError(null);

      try {
        const content = await getObjectContent(bucketName, fileName);
        setJsonData(content.content);
      } catch (error) {
        setError(error instanceof Error ? error.message : 'Failed to load file content');
        setJsonData(null);
      } finally {
        setIsLoadingFile(false);
      }
    }
  };

  const filteredBuckets = buckets.filter(bucket => 
    bucket.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    bucket.files.some(file => file.toLowerCase().includes(searchTerm.toLowerCase()))
  ).map(bucket => ({
    ...bucket,
    files: bucket.files.filter(file => 
      file.toLowerCase().includes(searchTerm.toLowerCase()) ||
      bucket.name.toLowerCase().includes(searchTerm.toLowerCase())
    )
  }));

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getFileExtension = (filename: string): string => {
    return filename.split('.').pop()?.toLowerCase() || '';
  };

  const isJsonFile = (filename: string): boolean => {
    return getFileExtension(filename) === 'json';
  };
  return (
    <div className="w-[530px] bg-neutral-800 rounded-4xl p-6 flex flex-col gap-6 h-full">
      <div className="flex items-center gap-3">
        <HugeiconsIcon icon={DatabaseIcon} className="text-blue-400" size={24} />
        <h2 className="text-xl font-bold text-white">Data Explorer</h2>
      </div>

      {error && (
        <div className="bg-red-900/50 border border-red-500 rounded-2xl p-4 flex items-start gap-3">
          <HugeiconsIcon icon={AlertCircleIcon} className="text-red-400 flex-shrink-0 mt-0.5" size={20} />
          <div>
            <p className="text-red-200 text-sm font-medium">Error</p>
            <p className="text-red-300 text-sm">{error}</p>
          </div>
        </div>
      )}

      <div className="space-y-3">
        <label className="text-sm font-medium text-gray-300 inline-block">S3 Bucket URL or Name</label>
        <div className="flex gap-3">
          <input
            type="text"
            value={s3Url}
            onChange={(e) => setS3Url(e.target.value)}
            placeholder="s3://your-bucket-name or just bucket-name"
            className="flex-1 bg-neutral-900 border border-gray-600 rounded-full px-6 py-3 text-white placeholder-gray-400 focus:outline-none focus:border-blue-400 transition-colors"
          />
          <button
            onClick={handlePullBuckets}
            disabled={isLoadingBuckets || !s3Url.trim()}
            className="bg-blue-500 hover:bg-blue-600 disabled:bg-gray-600 disabled:cursor-not-allowed text-white px-6 py-3 rounded-full font-medium transition-colors flex items-center gap-2 min-w-[100px]"
          >
            {isLoadingBuckets ? (
              <>
                <HugeiconsIcon icon={Loading03Icon} className="animate-spin" size={16} />
                Pulling...
              </>
            ) : (
              <>
                <HugeiconsIcon icon={CloudIcon} size={16} />
                Pull
              </>
            )}
          </button>
        </div>
      </div>

      {buckets.length > 0 && (
        <div className="space-y-3">
          <label className="text-sm font-medium text-gray-300 inline-block">Search Files & Buckets</label>
          <div className="relative">
            <HugeiconsIcon 
              icon={SearchIcon} 
              className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400" 
              size={16} 
            />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search buckets and files..."
              className="w-full bg-neutral-900 border border-gray-600 rounded-full pl-12 pr-6 py-3 text-white placeholder-gray-400 focus:outline-none focus:border-blue-400 transition-colors"
            />
          </div>
        </div>
      )}

      <div className="flex-1 space-y-2 overflow-y-auto custom-scrollbar">
        {buckets.length > 0 && (
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-medium text-gray-300">Available Buckets</h3>
              <span className="text-xs text-gray-500 bg-neutral-700 px-3 py-2 rounded-full font-medium">
                {filteredBuckets.length} bucket{filteredBuckets.length !== 1 ? 's' : ''}
              </span>
            </div>
            
            {filteredBuckets.length === 0 ? (
              <div className="text-center py-8 text-gray-400">
                <HugeiconsIcon icon={SearchIcon} size={32} className="mx-auto mb-2 opacity-50" />
                <p>No buckets or files match your search</p>
              </div>
            ) : (
              filteredBuckets.map((bucket) => (
                <div key={bucket.name} className="space-y-2">
                  <div
                    onClick={() => handleBucketClick(bucket.name)}
                    className="flex items-center justify-between p-4 bg-neutral-700 hover:bg-neutral-600 rounded-full cursor-pointer transition-all duration-200 group"
                  >
                    <div className="flex items-center gap-3">
                      <HugeiconsIcon 
                        icon={FolderIcon} 
                        className="text-yellow-400 group-hover:text-yellow-300 transition-colors" 
                        size={20} 
                      />
                      <span className="text-white font-medium">{bucket.name}</span>
                      <span className="text-xs text-gray-400 bg-neutral-600 px-3 py-1.5 rounded-full">
                        {bucket.files.length} file{bucket.files.length !== 1 ? 's' : ''}
                      </span>
                    </div>
                    <div className="flex items-center gap-3">
                      {onBucketSelect && (
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            onBucketSelect(bucket);
                          }}
                          disabled={selectedBuckets.some(selected => selected.name === bucket.name)}
                          className={`px-4 py-2 text-xs rounded-full transition-all font-medium ${
                            selectedBuckets.some(selected => selected.name === bucket.name)
                              ? 'bg-green-600 text-white cursor-not-allowed'
                              : 'bg-blue-500 hover:bg-blue-600 text-white cursor-pointer'
                          }`}
                        >
                          {selectedBuckets.some(selected => selected.name === bucket.name) ? 'Added' : 'Add'}
                        </button>
                      )}
                      <HugeiconsIcon
                        icon={expandedBucket === bucket.name ? ArrowUp01Icon : ArrowDown01Icon}
                        className="text-gray-400 transition-transform duration-300 group-hover:text-gray-300"
                        size={16}
                      />
                    </div>
                  </div>

                  <div
                    className={`ml-6 overflow-hidden transition-all duration-500 ease-in-out ${
                      expandedBucket === bucket.name ? 'opacity-100' : 'max-h-0 opacity-0'
                    }`}
                  >
                    <div className="space-y-2">
                      {bucket.files.map((file, index) => {
                        const fileObj = bucket.objects?.find(obj => obj.key === file);
                        return (
                          <div key={file} className="space-y-3">
                            <div
                              onClick={() => handleFileClick(bucket.name, file)}
                              className={`p-4 text-sm cursor-pointer rounded-full w-[90%] transition-all duration-300 group flex items-center gap-3 ${
                                selectedFile === file
                                  ? 'bg-blue-600 text-white shadow-lg'
                                  : 'text-gray-300 hover:bg-neutral-600 hover:text-white bg-neutral-800/50'
                              } transform hover:translate-x-1 ${
                                !isJsonFile(file) ? 'opacity-60 cursor-not-allowed' : ''
                              }`}
                              style={{
                                transitionDelay: expandedBucket === bucket.name ? `${index * 50}ms` : '0ms'
                              }}
                            >
                              <HugeiconsIcon 
                                icon={FileIcon} 
                                className={`${selectedFile === file ? 'text-blue-200' : 'text-blue-400'} transition-colors`}
                                size={16} 
                              />
                              <div className="flex-1">
                                <span className="block">{file}</span>
                                {fileObj && (
                                  <span className="text-xs text-gray-400">
                                    {formatFileSize(fileObj.size)} • {new Date(fileObj.last_modified).toLocaleDateString()}
                                  </span>
                                )}
                              </div>
                              {!isJsonFile(file) && (
                                <span className="text-xs text-gray-500">JSON only</span>
                              )}
                              {selectedFile === file && isJsonFile(file) && (
                                <HugeiconsIcon 
                                  icon={EyeIcon} 
                                  className="text-blue-200" 
                                  size={14} 
                                />
                              )}
                            </div>
                            {selectedFile === file && isJsonFile(file) && (
                              <div className="ml-6 p-5 bg-black/40 rounded-3xl animate-fadeIn border border-gray-700">
                                <div className="flex items-center justify-between mb-4">
                                  <div className="flex items-center gap-2">
                                    <HugeiconsIcon icon={FileIcon} className="text-green-400" size={16} />
                                    <span className="text-sm font-medium text-gray-300">File Content</span>
                                  </div>
                                  <button
                                    onClick={(e) => {
                                      e.stopPropagation();
                                      // Download JSON file
                                      const dataStr = JSON.stringify(jsonData, null, 2);
                                      const dataBlob = new Blob([dataStr], { type: 'application/json' });
                                      const url = URL.createObjectURL(dataBlob);
                                      const link = document.createElement('a');
                                      link.href = url;
                                      link.download = file;
                                      document.body.appendChild(link);
                                      link.click();
                                      document.body.removeChild(link);
                                      URL.revokeObjectURL(url);
                                    }}
                                    className="flex items-center gap-2 text-xs text-gray-400 hover:text-gray-200 transition-colors bg-neutral-700 hover:bg-neutral-600 px-3 py-2 rounded-full"
                                  >
                                    <HugeiconsIcon icon={DownloadIcon} size={12} />
                                    Export
                                  </button>
                                </div>
                                
                                {isLoadingFile ? (
                                  <div className="flex items-center justify-center py-8">
                                    <HugeiconsIcon icon={Loading03Icon} className="animate-spin text-blue-400" size={24} />
                                    <span className="ml-2 text-gray-400">Loading file content...</span>
                                  </div>
                                ) : jsonData ? (
                                  <JsonView
                                    value={jsonData}
                                    displayDataTypes={false}
                                    enableClipboard={false}
                                    shortenTextAfterLength={30}
                                    collapsed={1}
                                    style={{
                                      '--w-rjv-color': '#E2E8F0',
                                      '--w-rjv-key-number': '#22D3EE',
                                      '--w-rjv-key-string': '#A78BFA',
                                      '--w-rjv-background-color': 'transparent',
                                      '--w-rjv-line-color': '#33415580',
                                      '--w-rjv-arrow-color': '#94A3B8',
                                      '--w-rjv-edit-color': '#22D3EE',
                                      '--w-rjv-info-color': '#94A3B8CC',
                                      '--w-rjv-update-color': '#34D399',
                                      '--w-rjv-copied-color': '#22D3EE',
                                      '--w-rjv-copied-success-color': '#10B981',
                                      '--w-rjv-curlybraces-color': '#818CF8',
                                      '--w-rjv-colon-color': '#818CF8',
                                      '--w-rjv-brackets-color': '#818CF8',
                                      '--w-rjv-ellipsis-color': '#F472B6',
                                      '--w-rjv-quotes-color': '#94A3B8',
                                      '--w-rjv-quotes-string-color': '#7DD3FC',
                                      '--w-rjv-type-string-color': '#7DD3FC',
                                      '--w-rjv-type-int-color': '#A3E635',
                                      '--w-rjv-type-float-color': '#A3E635',
                                      '--w-rjv-type-bigint-color': '#A3E635',
                                      '--w-rjv-type-boolean-color': '#F59E0B',
                                      '--w-rjv-type-date-color': '#A3E635',
                                      '--w-rjv-type-url-color': '#60A5FA',
                                      '--w-rjv-type-null-color': '#A78BFA',
                                      '--w-rjv-type-nan-color': '#F43F5E',
                                      '--w-rjv-type-undefined-color': '#FB7185',
                                    } as React.CSSProperties}
                                  />
                                ) : null}
                              </div>
                            )}
                          </div>
                        );
                      })}
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default DataPanel;
export type { Bucket };
