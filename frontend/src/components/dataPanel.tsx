"use client";

import React, { useState } from 'react';
import { 
  CloudIcon, 
  ArrowDown01Icon, 
  ArrowUp01Icon, 
  FolderIcon,
  FileIcon,
  Loading03Icon,
  DatabaseIcon,
  SearchIcon,
  RefreshIcon,
  DownloadIcon,
  EyeIcon
} from "@hugeicons/core-free-icons";
import { HugeiconsIcon } from "@hugeicons/react";
import JsonView from '@uiw/react-json-view';

interface Bucket {
  name: string;
  files: string[];
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
  const [jsonData, setJsonData] = useState<any>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [isLoadingFile, setIsLoadingFile] = useState(false);

  // Mock data for demonstration
  const mockBuckets: Bucket[] = [
    {
      name: "sales-data-2024",
      files: ["quarterly-reports.json", "monthly-sales.json", "customer-analytics.json", "product-metrics.json"]
    },
    {
      name: "user-analytics",
      files: ["behavior-tracking.json", "demographics.json", "session-data.json"]
    },
    {
      name: "financial-records",
      files: ["revenue-breakdown.json", "expense-reports.json", "budget-analysis.json"]
    }
  ];

  const mockJsonData = {
    analytics: {
      period: "Q3 2024",
      metrics: {
        total_revenue: 2500000,
        growth_rate: 15.7,
        customer_acquisition: 1250,
        churn_rate: 3.2
      },
      top_performing_products: [
        { id: "PROD-001", name: "Enterprise Suite", revenue: 850000, units_sold: 340 },
        { id: "PROD-002", name: "Analytics Pro", revenue: 620000, units_sold: 780 },
        { id: "PROD-003", name: "Data Insights", revenue: 430000, units_sold: 950 }
      ],
      regional_breakdown: {
        north_america: { revenue: 1200000, percentage: 48 },
        europe: { revenue: 800000, percentage: 32 },
        asia_pacific: { revenue: 500000, percentage: 20 }
      }
    }
  };

  const handlePullBuckets = async () => {
    if (!s3Url.trim()) return;
    
    setIsLoading(true);
    // Simulate API call delay
    setTimeout(() => {
      setBuckets(mockBuckets);
      setIsLoading(false);
    }, 2000);
  };

  const handleBucketClick = (bucketName: string) => {
    if (expandedBucket === bucketName) {
      setExpandedBucket(null);
    } else {
      setExpandedBucket(bucketName);
      setSelectedFile(null);
      setJsonData(null);
    }
  };

  const handleFileClick = (fileName: string) => {
    if (selectedFile === fileName) {
      setSelectedFile(null);
      setJsonData(null);
    } else {
      setSelectedFile(fileName);
      setIsLoadingFile(true);
      // Simulate loading file content
      setTimeout(() => {
        setJsonData(mockJsonData);
        setIsLoadingFile(false);
      }, 500);
    }
  };

  // Filter buckets and files based on search term
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

  return (
    <div className="w-[530px] bg-neutral-800 rounded-4xl p-6 flex flex-col gap-6 h-full">
      {/* Header */}
      <div className="flex items-center gap-3">
        <HugeiconsIcon icon={DatabaseIcon} className="text-blue-400" size={24} />
        <h2 className="text-xl font-bold text-white">Data Explorer</h2>
      </div>

      {/* S3 URL Input */}
      <div className="space-y-3">
        <label className="text-sm font-medium text-gray-300">S3 Bucket URL</label>
        <div className="flex gap-2">
          <input
            type="text"
            value={s3Url}
            onChange={(e) => setS3Url(e.target.value)}
            placeholder="s3://your-bucket-name"
            className="flex-1 bg-neutral-900 border border-gray-600 rounded-xl px-4 py-2 text-white placeholder-gray-400 focus:outline-none focus:border-blue-400 transition-colors"
          />
          <button
            onClick={handlePullBuckets}
            disabled={isLoading || !s3Url.trim()}
            className="bg-blue-500 hover:bg-blue-600 disabled:bg-gray-600 disabled:cursor-not-allowed text-white px-4 py-2 rounded-xl font-medium transition-colors flex items-center gap-2 min-w-[80px]"
          >
            {isLoading ? (
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

      {/* Search Bar */}
      {buckets.length > 0 && (
        <div className="space-y-2">
          <label className="text-sm font-medium text-gray-300">Search Files & Buckets</label>
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
              placeholder="Search buckets and files..."
              className="w-full bg-neutral-900 border border-gray-600 rounded-xl pl-10 pr-4 py-2 text-white placeholder-gray-400 focus:outline-none focus:border-blue-400 transition-colors"
            />
          </div>
        </div>
      )}

      {/* Buckets List */}
      <div className="flex-1 space-y-2 overflow-y-auto custom-scrollbar">
        {buckets.length > 0 && (
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-medium text-gray-300">Available Buckets</h3>
              <span className="text-xs text-gray-500 bg-neutral-700 px-2 py-1 rounded-full">
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
                <div key={bucket.name} className="space-y-1">
                  <div
                    onClick={() => handleBucketClick(bucket.name)}
                    className="flex items-center justify-between p-3 bg-neutral-700 hover:bg-neutral-600 rounded-lg cursor-pointer transition-all duration-200 group"
                  >
                    <div className="flex items-center gap-3">
                      <HugeiconsIcon 
                        icon={FolderIcon} 
                        className="text-yellow-400 group-hover:text-yellow-300 transition-colors" 
                        size={20} 
                      />
                      <span className="text-white font-medium">{bucket.name}</span>
                      <span className="text-xs text-gray-400 bg-neutral-600 px-2 py-1 rounded-full">
                        {bucket.files.length} file{bucket.files.length !== 1 ? 's' : ''}
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
                          className={`px-3 py-1 text-xs rounded-full transition-all ${
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
                    className={`ml-4 overflow-hidden transition-all duration-500 ease-in-out ${
                      expandedBucket === bucket.name ? 'opacity-100' : 'max-h-0 opacity-0'
                    }`}
                  >
                    <div className="space-y-1">
                      {bucket.files.map((file, index) => (
                        <div key={file} className="space-y-2">
                          {/* File Item */}
                          <div
                            onClick={() => handleFileClick(file)}
                            className={`p-3 text-sm cursor-pointer rounded-md transition-all duration-300 group flex items-center gap-3 ${
                              selectedFile === file
                                ? 'bg-blue-600 text-white shadow-lg'
                                : 'text-gray-300 hover:bg-neutral-600 hover:text-white'
                            } transform hover:translate-x-1`}
                            style={{
                              transitionDelay: expandedBucket === bucket.name ? `${index * 50}ms` : '0ms'
                            }}
                          >
                            <HugeiconsIcon 
                              icon={FileIcon} 
                              className={`${selectedFile === file ? 'text-blue-200' : 'text-blue-400'} transition-colors`}
                              size={16} 
                            />
                            <span className="flex-1">{file}</span>
                            {selectedFile === file && (
                              <HugeiconsIcon 
                                icon={EyeIcon} 
                                className="text-blue-200" 
                                size={14} 
                              />
                            )}
                          </div>

                          {/* JSON Data Display - appears directly below the clicked file */}
                          {selectedFile === file && (
                            <div className="ml-4 p-4 bg-black/40 rounded-lg animate-fadeIn border border-gray-700">
                              <div className="flex items-center justify-between mb-3">
                                <div className="flex items-center gap-2">
                                  <HugeiconsIcon icon={FileIcon} className="text-green-400" size={16} />
                                  <span className="text-sm font-medium text-gray-300">File Content</span>
                                </div>
                                <button
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    // Add download functionality here
                                  }}
                                  className="flex items-center gap-1 text-xs text-gray-400 hover:text-gray-200 transition-colors"
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
                      ))}
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
