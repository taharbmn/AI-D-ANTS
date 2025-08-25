"use client";

import { SentIcon, Cancel01Icon, ArrowDown01Icon, Tick02Icon, DatabaseIcon, BarChartIcon } from "@hugeicons/core-free-icons";
import { HugeiconsIcon } from "@hugeicons/react";
import DataPanel, { Bucket } from "@/components/dataPanel";
import MessageDisplay from "@/components/MessageDisplay";
import { useState, useEffect, useRef } from "react";
import { useChatContext } from "@/contexts/ChatContext";
import { Dashboard } from "@/components/Dashboard";


const availableModels = [
  { id: "ollama", name: "Ollama", description: "Local AI models" },
  { id: "databricks", name: "Databricks", description: "Cloud AI platform" },
];

export default function Home() {
  const { messages, sendMessage, loading, currentChatTitle } = useChatContext();
  const [selectedBuckets, setSelectedBuckets] = useState<Bucket[]>([]);
  const [selectedFiles, setSelectedFiles] = useState<Array<{ name: string; path: string; data: any }>>([]);
  const [showDatasetSelector, setShowDatasetSelector] = useState(false);
  const [message, setMessage] = useState("");
  const [selectedModel, setSelectedModel] = useState("ollama");
  const [showModelDropdown, setShowModelDropdown] = useState(false);
  const [isDragOver, setIsDragOver] = useState(false);
  const [chatWidth, setChatWidth] = useState(70);
  const [isResizing, setIsResizing] = useState(false);
  const [activeTab, setActiveTab] = useState<'data' | 'dashboard'>('data');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const modelDropdownRef = useRef<HTMLDivElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (modelDropdownRef.current && !modelDropdownRef.current.contains(event.target as Node)) {
        setShowModelDropdown(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  // Resizer functionality
  const handleMouseDown = (e: React.MouseEvent) => {
    e.preventDefault();
    setIsResizing(true);
  };

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (!isResizing || !containerRef.current) return;
      
      const containerRect = containerRef.current.getBoundingClientRect();
      const newChatWidth = ((e.clientX - containerRect.left) / containerRect.width) * 100;
      
      const constrainedWidth = Math.min(Math.max(newChatWidth, 30), 80);
      setChatWidth(constrainedWidth);
    };

    const handleMouseUp = () => {
      setIsResizing(false);
    };

    if (isResizing) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
      document.body.style.cursor = 'col-resize';
      document.body.style.userSelect = 'none';
    }

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
      document.body.style.cursor = '';
      document.body.style.userSelect = '';
    };
  }, [isResizing]);

  const handleBucketSelect = (bucket: Bucket) => {
    if (!selectedBuckets.some((selected) => selected.name === bucket.name)) {
      setSelectedBuckets((prev) => [...prev, bucket]);
    }
  };

  const removeBucket = (bucketName: string) => {
    setSelectedBuckets((prev) =>
      prev.filter((bucket) => bucket.name !== bucketName)
    );
  };

  const removeFile = (filePath: string) => {
    setSelectedFiles((prev) =>
      prev.filter((file) => file.path !== filePath)
    );
  };

  const handleSendMessage = async () => {
    if (!message.trim()) return;
    
    // Collect all selected dataset paths
    const datasetPaths = [
      ...selectedBuckets.map(bucket => bucket.name), // Use bucket names as paths for now
      ...selectedFiles.map(file => file.path)
    ];
    
    const messageToSend = message;
    setMessage("");
    await sendMessage(messageToSend, datasetPaths);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleFileSelect = (file: { name: string; path: string; data: any }) => {
    if (!selectedFiles.some((selected) => selected.path === file.path)) {
      setSelectedFiles((prev) => [...prev, file]);
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    
    // First check if it's a dragged analyzed file from the data explorer
    const jsonData = e.dataTransfer.getData('application/json');
    if (jsonData) {
      try {
        const draggedFile = JSON.parse(jsonData);
        // Add the analyzed file as a dataset chip
        if (!selectedFiles.some(selected => selected.path === draggedFile.path)) {
          setSelectedFiles(prev => [...prev, draggedFile]);
        }
        return;
      } catch (error) {
        console.error("Invalid JSON data:", error);
      }
    }
    
    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0) {
      files.forEach(file => {
        const filePath = (file as any).path || file.name;
        const fileName = file.name;
        
        const newFile = {
          name: fileName,
          path: filePath,
          data: {
            content_type: file.type || 'unknown',
            description: `Dragged file: ${fileName}`,
            metadata: {
              file_info: {
                size: file.size
              }
            }
          }
        };
        
        if (!selectedFiles.some(selected => selected.path === filePath)) {
          setSelectedFiles(prev => [...prev, newFile]);
        }
      });
    }
  };

  return (
    <div className="flex gap-2 flex-grow" ref={containerRef}>
      <div 
        className="bg-neutral-800 relative rounded-4xl flex flex-col transition-all duration-200 ease-out"
        style={{ width: `${chatWidth}%` }}
      >
        <div className="w-full max-h-[93.5vh] flex flex-col overflow-y-auto custom-scrollbar">
          <div className="px-6 py-4 border-b border-neutral-700/50">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-medium text-white">
                {currentChatTitle || "New Chat"}
              </h2>
              <div className="relative" ref={modelDropdownRef}>
                <button
                  onClick={() => setShowModelDropdown(!showModelDropdown)}
                  className="flex justify-between items-center gap-2 px-4 py-2 bg-neutral-700 hover:bg-neutral-600 border border-neutral-600 rounded-full text-sm text-white transition-all duration-200 min-w-[160px] "
                >
                  <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                  <span className="truncate">{availableModels.find(m => m.id === selectedModel)?.name || selectedModel}</span>
                  <HugeiconsIcon icon={ArrowDown01Icon} size={20} className={`transition-transform duration-200 ${showModelDropdown ? 'rotate-180' : ''}`} />
                </button>
                
                {showModelDropdown && (
                  <div className="absolute top-full mt-2 right-0 bg-neutral-800 border border-neutral-600 rounded-2xl z-20 min-w-[280px] overflow-hidden">
                    <div className="max-h-64 overflow-y-auto">
                      {availableModels.map((model) => (
                        <button
                          key={model.id}
                          onClick={() => {
                            setSelectedModel(model.id);
                            setShowModelDropdown(false);
                          }}
                          className={`w-full text-left p-3 hover:bg-neutral-700 transition-colors duration-200 border-l-4 ${
                            selectedModel === model.id 
                              ? 'border-blue-500 bg-neutral-700/50' 
                              : 'border-transparent'
                          }`}
                        >
                          <div className="flex items-center justify-between">
                            <div className="flex-1">
                              <div className="flex items-center gap-2">
                                <div className={`w-2 h-2 rounded-full ${
                                  selectedModel === model.id ? 'bg-blue-400' : 'bg-green-400'
                                }`}></div>
                                <span className="text-sm font-medium text-white">{model.name}</span>
                              </div>
                              <p className="text-xs text-gray-400 mt-1">{model.description}</p>
                            </div>
                            {selectedModel === model.id && (
                              <HugeiconsIcon icon={Tick02Icon}  strokeWidth={2} size={20} className="text-blue-400" />
                            )}
                          </div>
                        </button>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
          <div className="w-full flex flex-col px-24 gap-6 py-4 h-[74vh] overflow-y-scroll">
            {messages.length === 0 ? (
              <div className="flex items-center justify-center h-64 text-gray-400">
                <div className="text-center">
                  <h2 className="text-xl mb-2">Welcome to AI-D-ANTS</h2>
                  <p>Start a conversation or select a chat from the history.</p>
                </div>
              </div>
            ) : (
              messages.map((msg, idx) => (
                <div
                  key={idx}
                  className={`flex ${
                    msg.sender === "user" ? "justify-end" : "justify-start"
                  }`}
                >
                  {msg.sender === "user" ? (
                    <div className="px-6 py-4 rounded-3xl text-base max-w-[70%] whitespace-pre-line transition-all duration-200 bg-blue-500 text-white rounded-br-md"
                         style={{ wordBreak: "break-word" }}>
                      {msg.text}
                    </div>
                  ) : (
                    <MessageDisplay message={msg} />
                  )}
                </div>
              ))
            )}
            {loading && (
              <div className="flex justify-start">
                <div className="px-6 py-4 rounded-3xl text-base max-w-[70%] bg-white/10 text-white border border-white/10 rounded-bl-md">
                  <div className="flex items-center space-x-2">
                    <span>Thinking</span>
                    <div className="flex space-x-1">
                      <div className="w-1 h-1 bg-white rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                      <div className="w-1 h-1 bg-white rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                      <div className="w-1 h-1 bg-white rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                    </div>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          <div className="flex items-center justify-center px-6 py-6">
            <div 
              className={`h-[200px] w-full max-w-4xl flex flex-col gap-4 p-4 bg-neutral-900 rounded-4xl relative transition-all duration-200 ${
                isDragOver ? 'border-2 border-dashed border-blue-400 bg-blue-900/10' : ''
              }`}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
            >
              <div className="flex items-center gap-2">
                <button
                  onClick={() => setShowDatasetSelector(!showDatasetSelector)}
                  className="bg-white/10 cursor-pointer border border-dashed text-sm py-2 border-white/50 rounded-full w-fit px-4 text-center transition-all hover:bg-white/20"
                >
                  Add Dataset +
                </button>

                {selectedBuckets.length > 0 && (
                  <div className="flex flex-wrap gap-2">
                    {selectedBuckets.map((bucket) => (
                      <div
                        key={bucket.name}
                        className="bg-blue-500/10 flex items-center justify-center gap-2 cursor-pointer border border-dashed text-sm py-2 border-blue-500/50 rounded-full w-fit px-4 text-center transition-all hover:bg-blue-500/20"
                      >
                        <span>{bucket.name}</span>
                        <button
                          onClick={() => removeBucket(bucket.name)}
                          className="hover:bg-red-500/20 cursor-pointer rounded-full p-0.5 transition-colors"
                        >
                          <HugeiconsIcon icon={Cancel01Icon} size={15} />
                        </button>
                      </div>
                    ))}
                  </div>
                )}

                {selectedFiles.length > 0 && (
                  <div className="flex flex-wrap gap-2">
                    {selectedFiles.map((file) => (
                      <div
                        key={file.path}
                        className="bg-blue-500/10 flex items-center justify-center gap-2 cursor-pointer border border-dashed text-sm py-2 border-blue-500/50 rounded-full w-fit px-4 text-center transition-all hover:bg-blue-500/20"
                      >
                        <span>{file.name}</span>
                        <button
                          onClick={() => removeFile(file.path)}
                          className="hover:bg-red-500/20 cursor-pointer rounded-full p-0.5 transition-colors"
                        >
                          <HugeiconsIcon icon={Cancel01Icon} size={15} />
                        </button>
                      </div>
                    ))}
                  </div>
                )}

                {showDatasetSelector && (
                  <div className="absolute bottom-full mb-2 left-4 bg-neutral-800 border border-gray-600 rounded-lg p-3  z-10 min-w-[250px]">
                    <div className="text-sm text-gray-300 mb-2">
                      Select datasets from the Data Explorer panel →
                    </div>
                    <div className="text-xs text-gray-400 space-y-1">
                      <div>• Click the &quot;+&quot; button next to analyzed files</div>
                      <div>• Drag analyzed files from Data Explorer to here</div>
                      <div>• Or drag & drop files from your computer</div>
                      <div>All will appear as dataset chips above</div>
                    </div>
                    <button
                      onClick={() => setShowDatasetSelector(false)}
                      className="mt-2 text-xs text-blue-400 hover:text-blue-300 transition-colors"
                    >
                      Got it!
                    </button>
                  </div>
                )}
              </div>

              <div className="flex flex-grow items-end relative">
                {isDragOver && (
                  <div className="absolute inset-0 flex items-center justify-center bg-blue-900/20 rounded-lg pointer-events-none z-10">
                    <div className="text-center">
                      <div className="text-blue-300 text-lg font-medium mb-1">Drop datasets here</div>
                      <div className="text-blue-400 text-sm">Drag from Data Explorer or drop files/folders</div>
                    </div>
                  </div>
                )}

                <textarea
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder={isDragOver ? "" : "Ask me anything about your data..."}
                  className="resize-none flex-grow h-full bg-transparent pt-5 text-white placeholder-gray-400 outline-none p-2 rounded-lg"
                  disabled={loading}
                />
                <button 
                  onClick={handleSendMessage}
                  disabled={loading || !message.trim()}
                  className="rounded-full h-11 w-11 ml-3 cursor-pointer bg-blue-500 hover:bg-blue-600 disabled:bg-gray-600 disabled:cursor-not-allowed flex items-center justify-center transition-colors"
                >
                  <HugeiconsIcon icon={SentIcon} className="text-white" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div 
        className={`relative flex items-center justify-center group cursor-col-resize transition-all duration-200 rounded-full ${
          isResizing ? 'bg-blue-500/20' : 'hover:bg-neutral-700/50'
        }`}
        style={{ width: '12px' }}
        onMouseDown={handleMouseDown}
      >
        <div className="flex flex-col gap-1 items-center">
          <div className={`w-1 h-1 rounded-full transition-all duration-200 ${
            isResizing ? 'bg-blue-400' : 'bg-neutral-500 group-hover:bg-neutral-400'
          }`}></div>
          <div className={`w-1 h-1 rounded-full transition-all duration-200 ${
            isResizing ? 'bg-blue-400' : 'bg-neutral-500 group-hover:bg-neutral-400'
          }`}></div>
          <div className={`w-1 h-1 rounded-full transition-all duration-200 ${
            isResizing ? 'bg-blue-400' : 'bg-neutral-500 group-hover:bg-neutral-400'
          }`}></div>
          <div className={`w-1 h-1 rounded-full transition-all duration-200 ${
            isResizing ? 'bg-blue-400' : 'bg-neutral-500 group-hover:bg-neutral-400'
          }`}></div>
          <div className={`w-1 h-1 rounded-full transition-all duration-200 ${
            isResizing ? 'bg-blue-400' : 'bg-neutral-500 group-hover:bg-neutral-400'
          }`}></div>
        </div>
        
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none z-10">
          <div className="bg-neutral-900 text-white text-xs px-2 py-1 rounded-lg  whitespace-nowrap -translate-y-8">
            Drag to resize
            <div className="absolute top-full left-1/2 transform -translate-x-1/2 w-2 h-2 bg-neutral-900 rotate-45 -mt-1"></div>
          </div>
        </div>
      </div>

      <div 
        className="transition-all duration-200 ease-out flex flex-col"
        style={{ width: `${100 - chatWidth}%` }}
      >
       <div className="flex mb-6 space-x-4 bg-neutral-800 p-1 rounded-2xl w-fit ">
          <button
            onClick={() => setActiveTab('data')}
            className={`flex items-center gap-3 px-6 py-3 rounded-xl transition-all duration-300 ease-out transform ${
              activeTab === 'data'
                ? 'bg-blue-500 text-white  scale-105 '
                : 'text-neutral-400 hover:text-white hover:bg-neutral-700/50'
            }`}
          >
            <HugeiconsIcon 
              icon={DatabaseIcon} 
              size={20}
              className={`transition-colors duration-300 ${
                activeTab === 'data' ? 'text-white' : 'text-neutral-400'
              }`}
            />
            <span className="font-semibold text-sm">Data Panel</span>
          </button>
          <button
            onClick={() => setActiveTab('dashboard')}
            className={`flex items-center gap-3 px-6 py-3 rounded-xl transition-all duration-300 ease-out transform ${
              activeTab === 'dashboard'
                ? 'bg-blue-500 text-white  scale-105'
                : 'text-neutral-400 hover:text-white hover:bg-neutral-700/50'
            }`}
          >
            <HugeiconsIcon 
              icon={BarChartIcon} 
              size={20}
              className={`transition-colors duration-300 ${
                activeTab === 'dashboard' ? 'text-white' : 'text-neutral-400'
              }`}
            />
            <span className="font-semibold text-sm">Dashboard</span>
          </button>
        </div>

        <div className=" bg-neutral-800  rounded-2xl p-6 h-[88vh] overflow-y-scroll  border border-neutral-700">
          {activeTab === 'data' ? (
            <DataPanel
              onBucketSelect={handleBucketSelect}
              selectedBuckets={selectedBuckets}
              onFileSelect={handleFileSelect}
              selectedFiles={selectedFiles}
            />
          ) : (
            <Dashboard />
          )}
        </div>
      </div>
    </div>
  );
}