"use client";

import { SentIcon, Cancel01Icon } from "@hugeicons/core-free-icons";
import { HugeiconsIcon } from "@hugeicons/react";
import DataPanel, { Bucket } from "@/components/dataPanel";
import { useState, useEffect, useRef } from "react";
import { useChatContext } from "@/contexts/ChatContext";

const extractAnswerContent = (text: string): string => {
  const answerMatch = text.match(/<answer>([\s\S]*?)<\/answer>/);
  return answerMatch ? answerMatch[1].trim() : text;
};

export default function Home() {
  const { messages, sendMessage, loading } = useChatContext();
  const [selectedBuckets, setSelectedBuckets] = useState<Bucket[]>([]);
  const [selectedFiles, setSelectedFiles] = useState<Array<{ name: string; path: string; data: any }>>([]);
  const [showDatasetSelector, setShowDatasetSelector] = useState(false);
  const [message, setMessage] = useState("");
  const [isDragOver, setIsDragOver] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

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
    
    const messageToSend = message;
    setMessage("");
    await sendMessage(messageToSend);
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
    <div className="flex gap-6 flex-grow">
      <div className="bg-neutral-800 relative flex-grow rounded-4xl flex flex-col">
        <div className="w-full max-h-[93.5vh] flex flex-col overflow-y-auto custom-scrollbar">
          <div className="w-full flex flex-col px-24 gap-6 py-4 h-[78vh] overflow-y-scroll">
            {messages.length === 0 ? (
              <div className="flex items-center justify-center h-64 text-gray-400">
                <div className="text-center">
                  <h2 className="text-xl mb-2">Welcome to D-ANTS</h2>
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
                  <div
                    className={`px-6 py-4 rounded-3xl text-base max-w-[70%] whitespace-pre-line shadow-md transition-all duration-200
                      ${
                        msg.sender === "user"
                          ? "bg-blue-500 text-white rounded-br-md"
                          : "bg-white/10 text-white border border-white/10 rounded-bl-md"
                      }
                    `}
                    style={{ wordBreak: "break-word" }}
                  >
                    {msg.sender === "assistant" 
                      ? extractAnswerContent(msg.text)
                      : msg.text
                    }
                  </div>
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
                  <div className="absolute bottom-full mb-2 left-4 bg-neutral-800 border border-gray-600 rounded-lg p-3 shadow-lg z-10 min-w-[250px]">
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

      <DataPanel
        onBucketSelect={handleBucketSelect}
        selectedBuckets={selectedBuckets}
        onFileSelect={handleFileSelect}
        selectedFiles={selectedFiles}
      />
    </div>
  );
}