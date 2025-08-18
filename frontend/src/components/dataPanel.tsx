"use client";
import React, { useState } from 'react';
import { 
  CloudIcon, 
  ArrowDown01Icon, 
  FolderIcon,
  FileIcon,
  Loading03Icon,
  DatabaseIcon,
  SearchIcon,
  AlertCircleIcon,
  StructureIcon,
  TableIcon,
} from "@hugeicons/core-free-icons";
import { HugeiconsIcon } from "@hugeicons/react";
import JsonView from '@uiw/react-json-view';
import {
  getS3Buckets,
  getBucketObjects,
  getObjectContent,
  testBucketConnection
} from '../lib/s3-actions';
import { createTreeStructure } from '../lib/api';

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

// Simple JSON styling for consistent appearance
const jsonViewStyle = {
  '--w-rjv-color': '#E2E8F0',
  '--w-rjv-key-string': '#A78BFA',
  '--w-rjv-background-color': 'transparent',
  '--w-rjv-type-string-color': '#7DD3FC',
  '--w-rjv-type-int-color': '#A3E635',
  '--w-rjv-type-boolean-color': '#F59E0B',
} as React.CSSProperties;

const DataPanel: React.FC<DataPanelProps> = ({ onBucketSelect, selectedBuckets = [] }) => {
  const [s3Url, setS3Url] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [buckets, setBuckets] = useState<Bucket[]>([]);
  const [expandedBucket, setExpandedBucket] = useState<string | null>(null);
  const [selectedFile, setSelectedFile] = useState<string | null>(null);
  const [jsonData, setJsonData] = useState<any | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [treeStructure, setTreeStructure] = useState<any>(null);
  const [showTreeStructure, setShowTreeStructure] = useState(false);
  const [localPaths, setLocalPaths] = useState<string[]>([]);
  const [expandedFiles, setExpandedFiles] = useState<string[]>([]);

  const handlePullBuckets = async () => {
    if (!s3Url.trim()) {
      setError('Please enter an S3 URL or local path');
      return;
    }

    const trimmedUrl = s3Url.trim();
    const isS3Path = trimmedUrl.startsWith('s3://') || trimmedUrl.includes('.s3.');
    
    if (!isS3Path) {
      // Handle local paths
      if (!localPaths.includes(trimmedUrl)) {
        setLocalPaths(prev => [...prev, trimmedUrl]);
      }
      setError(null);
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const bucketName = trimmedUrl.replace('s3://', '').split('/')[0];
      const objectsResponse = await getBucketObjects(bucketName);
      
      const bucket: Bucket = {
        name: bucketName,
        files: objectsResponse.objects.map(obj => obj.key),
        objects: objectsResponse.objects
      };

      setBuckets([bucket]);
    } catch (error) {
      setError(error instanceof Error ? error.message : 'Failed to fetch S3 data');
    } finally {
      setIsLoading(false);
    }
  };

  const handleFileClick = async (bucketName: string, fileName: string) => {
    if (selectedFile === fileName) {
      setSelectedFile(null);
      setJsonData(null);
      return;
    }

    setSelectedFile(fileName);
    setIsLoading(true);

    try {
      const content = await getObjectContent(bucketName, fileName);
      setJsonData(content.content);
    } catch (error) {
      setError(error instanceof Error ? error.message : 'Failed to load file');
    } finally {
      setIsLoading(false);
    }
  };

  const handleCreateTreeStructure = async () => {
    if (selectedBuckets.length === 0 && localPaths.length === 0) {
      setError('Please select at least one bucket or add a local path');
      return;
    }

    setIsLoading(true);
    try {
      const allPaths = [
        ...selectedBuckets.map(bucket => `s3://${bucket.name}`),
        ...localPaths
      ];
      const response = await createTreeStructure(allPaths);
      setTreeStructure(response.response);
      setShowTreeStructure(true);
    } catch (error) {
      setError(error instanceof Error ? error.message : 'Failed to create tree structure');
    } finally {
      setIsLoading(false);
    }
  };

  const filteredBuckets = buckets.filter(bucket => 
    bucket.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    bucket.files.some(file => file.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  return (
    <div className="w-[530px] bg-neutral-800 rounded-4xl p-6 flex flex-col gap-4 h-full">
      {/* Header */}
      <div className="flex items-center gap-3">
        <HugeiconsIcon icon={DatabaseIcon} className="text-blue-400" size={24} />
        <h2 className="text-xl font-bold text-white">Data Explorer</h2>
      </div>

      {/* Error Display */}
      {error && (
        <div className="bg-red-900/50 border border-red-500 rounded-xl p-3 flex items-center gap-2">
          <HugeiconsIcon icon={AlertCircleIcon} className="text-red-400" size={16} />
          <p className="text-red-200 text-sm">{error}</p>
        </div>
      )}

      {/* Input Section */}
      <div className="space-y-2">
        <input
          type="text"
          value={s3Url}
          onChange={(e) => setS3Url(e.target.value)}
          placeholder="s3://bucket-name or C:/path/to/folder"
          className="w-full bg-neutral-900 border border-gray-600 rounded-xl px-4 py-3 text-white placeholder-gray-400 focus:outline-none focus:border-blue-400"
        />
        <div className="flex gap-2">
          <button
            onClick={handlePullBuckets}
            disabled={isLoading || !s3Url.trim()}
            className="bg-blue-500 hover:bg-blue-600 disabled:bg-gray-600 text-white px-4 py-2 rounded-lg font-medium transition-colors flex items-center gap-2"
          >
            {isLoading ? (
              <HugeiconsIcon icon={Loading03Icon} className="animate-spin" size={16} />
            ) : (
              <HugeiconsIcon icon={CloudIcon} size={16} />
            )}
            Add
          </button>
          
          {(selectedBuckets.length > 0 || localPaths.length > 0) && (
            <button
              onClick={handleCreateTreeStructure}
              disabled={isLoading}
              className="bg-green-500 hover:bg-green-600 disabled:bg-gray-600 text-white px-4 py-2 rounded-lg font-medium transition-colors flex items-center gap-2"
            >
              <HugeiconsIcon icon={StructureIcon} size={16} />
              Analyze
            </button>
          )}
        </div>
      </div>

      {/* Search */}
      {buckets.length > 0 && (
        <div className="relative">
          <HugeiconsIcon 
            icon={SearchIcon} 
            className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" 
            size={16} 
          />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search files..."
            className="w-full bg-neutral-900 border border-gray-600 rounded-xl pl-10 pr-4 py-2 text-white placeholder-gray-400 focus:outline-none focus:border-blue-400"
          />
        </div>
      )}

      {/* Tree Structure Results */}
      {showTreeStructure && treeStructure && (
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-medium text-gray-300">Analyzed Files</h3>
            <button
              onClick={() => setShowTreeStructure(false)}
              className="text-gray-400 hover:text-gray-200 text-sm"
            >
              Hide
            </button>
          </div>
          <div className="max-h-[400px] overflow-y-auto space-y-2">
            {Object.entries(treeStructure).map(([filePath, fileData]: [string, any]) => {
              const fileName = fileData.name || filePath.split('/').pop() || filePath;
              const fileInfo = fileData.metadata?.file_info;
              const shape = fileInfo?.shape;
              const isExpanded = expandedFiles.includes(filePath);
              
              const toggleExpanded = () => {
                setExpandedFiles(prev => 
                  isExpanded 
                    ? prev.filter(path => path !== filePath)
                    : [...prev, filePath]
                );
              };
              
              return (
                <div key={filePath} className="space-y-2">
                  {/* File Info Header - Separate div */}
                  <div className="rounded-2xl bg-neutral-700 overflow-hidden">
                    <div 
                      className="flex items-center justify-between cursor-pointer p-3 hover:bg-neutral-600 transition-colors"
                      onClick={toggleExpanded}
                    >
                      <div className="flex items-center gap-2">
                        <HugeiconsIcon icon={FileIcon} className="text-blue-400" size={16} />
                        <div>
                          <span className="text-white text-sm font-medium">{fileName}</span>
                          <div className="flex items-center gap-3 mt-1">
                            <span className="text-xs text-gray-400 bg-neutral-600 rounded-full px-2 py-1">
                              {fileData.content_type?.toUpperCase() || fileData.type?.toUpperCase()}
                            </span>
                            {shape && (
                              <span className="text-xs text-gray-400 flex items-center gap-1">
                                <HugeiconsIcon icon={TableIcon} size={12} />
                                {shape.rows} rows × {shape.columns} cols
                              </span>
                            )}
                          </div>
                        </div>
                      </div>
                      <HugeiconsIcon
                        icon={ArrowDown01Icon}
                        className={`text-gray-400 transition-transform ${
                          isExpanded ? 'rotate-180' : ''
                        }`}
                        size={16}
                      />
                    </div>
                  </div>

                  {/* Expanded Content - Separate detached div */}
                  {isExpanded && (
                    <div className="rounded-2xl bg-neutral-800 p-4 space-y-4 border border-gray-600">
                      {/* Main Dataset Description */}
                      {fileData.description && (
                        <div>
                          <div className="text-sm font-medium text-gray-200 mb-2 flex items-center gap-2">
                            <HugeiconsIcon icon={FileIcon} className="text-green-400" size={14} />
                            Dataset Description
                          </div>
                          <div className="text-sm text-gray-300 bg-neutral-900 rounded-lg p-3 border border-gray-700">
                            {fileData.description}
                          </div>
                        </div>
                      )}

                      {/* Column Descriptions */}
                      {fileData.columnsDescription && fileData.columnsDescription.length > 0 && (
                        <div>
                          <div className="text-sm font-medium text-gray-200 mb-2 flex items-center gap-2">
                            <HugeiconsIcon icon={TableIcon} className="text-blue-400" size={14} />
                            Columns ({fileData.columnsDescription.length})
                          </div>
                          <div className="space-y-2 max-h-64 overflow-y-auto">
                            {fileData.columnsDescription.map((colDesc: any, index: number) => {
                              const [columnName, description] = Object.entries(colDesc)[0] as [string, string];
                              return (
                                <div key={index} className="bg-neutral-900 rounded-lg p-3 border border-gray-700">
                                  <div className="text-sm font-medium text-white mb-1">{columnName}</div>
                                  <div className="text-xs text-gray-400">{description}</div>
                                </div>
                              );
                            })}
                          </div>
                        </div>
                      )}

                      {/* Sample Data */}
                      {fileData.metadata?.sample_data?.head && (
                        <div>
                          <div className="text-sm font-medium text-gray-200 mb-2 flex items-center gap-2">
                            <HugeiconsIcon icon={SearchIcon} className="text-purple-400" size={14} />
                            Sample Data (First 3 rows)
                          </div>
                          <div className="bg-black/30 rounded-lg p-3 max-h-48 overflow-y-auto border border-gray-700">
                            <JsonView
                              value={fileData.metadata.sample_data.head}
                              displayDataTypes={false}
                              enableClipboard={false}
                              collapsed={1}
                              style={jsonViewStyle}
                            />
                          </div>
                        </div>
                      )}

                      {/* Tail Data */}
                      {fileData.metadata?.sample_data?.tail && (
                        <div>
                          <div className="text-sm font-medium text-gray-200 mb-2 flex items-center gap-2">
                            <HugeiconsIcon icon={SearchIcon} className="text-orange-400" size={14} />
                            Sample Data (Last 3 rows)
                          </div>
                          <div className="bg-black/30 rounded-lg p-3 max-h-48 overflow-y-auto border border-gray-700">
                            <JsonView
                              value={fileData.metadata.sample_data.tail}
                              displayDataTypes={false}
                              enableClipboard={false}
                              collapsed={1}
                              style={jsonViewStyle}
                            />
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Local Paths */}
      {localPaths.length > 0 && (
        <div className="space-y-2">
          <h3 className="text-sm font-medium text-gray-300">Local Paths ({localPaths.length})</h3>
          <div className="space-y-1">
            {localPaths.map((path, index) => (
              <div key={index} className="flex items-center justify-between p-2 bg-neutral-700 rounded-lg">
                <div className="flex items-center gap-2">
                  <HugeiconsIcon icon={FolderIcon} className="text-green-400" size={16} />
                  <span className="text-white text-sm">{path}</span>
                </div>
                <button
                  onClick={() => setLocalPaths(prev => prev.filter((_, i) => i !== index))}
                  className="text-gray-400 hover:text-red-400 text-sm"
                >
                  ×
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Buckets and Files */}
      <div className="flex-1 overflow-y-auto space-y-2">
        {filteredBuckets.map((bucket) => (
          <div key={bucket.name} className="space-y-2">
            <div
              onClick={() => setExpandedBucket(expandedBucket === bucket.name ? null : bucket.name)}
              className="flex items-center justify-between p-3 bg-neutral-700 hover:bg-neutral-600 rounded-xl cursor-pointer"
            >
              <div className="flex items-center gap-2">
                <HugeiconsIcon icon={FolderIcon} className="text-yellow-400" size={18} />
                <span className="text-white font-medium">{bucket.name}</span>
                <span className="text-xs text-gray-400 bg-neutral-600 px-2 py-1 rounded">
                  {bucket.files.length} files
                </span>
              </div>
              <div className="flex items-center gap-2">
                {onBucketSelect && (
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onBucketSelect(bucket);
                    }}
                    disabled={selectedBuckets.some(selected => selected.name === bucket.name)}
                    className={`px-3 py-1 text-xs rounded ${
                      selectedBuckets.some(selected => selected.name === bucket.name)
                        ? 'bg-green-600 text-white'
                        : 'bg-blue-500 hover:bg-blue-600 text-white'
                    }`}
                  >
                    {selectedBuckets.some(selected => selected.name === bucket.name) ? 'Added' : 'Add'}
                  </button>
                )}
                <HugeiconsIcon
                  icon={ArrowDown01Icon}
                  className={`text-gray-400 transition-transform ${
                    expandedBucket === bucket.name ? 'rotate-180' : ''
                  }`}
                  size={16}
                />
              </div>
            </div>

            {/* Files */}
            {expandedBucket === bucket.name && (
              <div className="ml-4 space-y-1">
                {bucket.files.map((file) => (
                  <div key={file}>
                    <div
                      onClick={() => handleFileClick(bucket.name, file)}
                      className={`p-3 text-sm cursor-pointer rounded-lg transition-colors flex items-center gap-2 ${
                        selectedFile === file
                          ? 'bg-blue-600 text-white'
                          : 'text-gray-300 hover:bg-neutral-600 bg-neutral-800'
                      }`}
                    >
                      <HugeiconsIcon icon={FileIcon} className="text-blue-400" size={14} />
                      <span>{file}</span>
                    </div>
                    
                    {/* File Content */}
                    {selectedFile === file && jsonData && (
                      <div className="mt-2 p-3 bg-black/40 rounded-lg">
                        <div className="text-xs text-gray-400 mb-2">File Content:</div>
                        <div className="max-h-64 overflow-y-auto">
                          <JsonView
                            value={jsonData}
                            displayDataTypes={false}
                            enableClipboard={false}
                            collapsed={1}
                            style={jsonViewStyle}
                          />
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default DataPanel;
export type { Bucket };
