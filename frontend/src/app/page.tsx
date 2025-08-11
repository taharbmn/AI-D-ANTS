"use client";

import { SentIcon, Cancel01Icon } from "@hugeicons/core-free-icons";
import { HugeiconsIcon } from "@hugeicons/react";
import DataPanel, { Bucket } from "@/components/dataPanel";
import { useState } from "react";

interface Message {
  sender: "user" | "ai";
  text: string;
}

export default function Home() {
  const [selectedBuckets, setSelectedBuckets] = useState<Bucket[]>([]);
  const [showDatasetSelector, setShowDatasetSelector] = useState(false);
  const [message, setMessage] = useState("");

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

  const messages: Message[] = [
    { sender: "user", text: "Hello, AI! Can you help me with my data?" },
    {
      sender: "ai",
      text: "Of course! Please describe your workflow or upload your dataset.",
    },
    { sender: "user", text: "I want to analyze sales anomalies for Q2." },
    {
      sender: "ai",
      text: "Great! I can help you analyze your sales data. Please upload your dataset using the data panel on the left, and I'll provide insights on any anomalies detected.",
    },
    { sender: "user", text: "How do I connect to my S3 bucket?" },
    {
      sender: "ai",
      text: "Simply enter your S3 bucket URL in the data panel and click 'Pull'. I'll fetch all available buckets and files for you to explore.",
    },
        { sender: "user", text: "Hello, AI! Can you help me with my data?" },
    {
      sender: "ai",
      text: "Of course! Please describe your workflow or upload your dataset.",
    },
    { sender: "user", text: "I want to analyze sales anomalies for Q2." },
    {
      sender: "ai",
      text: "Great! I can help you analyze your sales data. Please upload your dataset using the data panel on the left, and I'll provide insights on any anomalies detected.",
    },
    { sender: "user", text: "How do I connect to my S3 bucket?" },
    {
      sender: "ai",
      text: "Simply enter your S3 bucket URL in the data panel and click 'Pull'. I'll fetch all available buckets and files for you to explore.",
    },
        { sender: "user", text: "How do I connect to my S3 bucket?" },
    {
      sender: "ai",
      text: "Simply enter your S3 bucket URL in the data panel and click 'Pull'. I'll fetch all available buckets and files for you to explore.",
    },
    
        { sender: "user", text: "How do I connect to my S3 bucket?" },
    {
      sender: "ai",
      text: "Simply enter your S3 bucket URL in the data panel and click 'Pull'. I'll fetch all available buckets and files for you to explore.",
    },
    
        { sender: "user", text: "How do I connect to my S3 bucket?" },
    {
      sender: "ai",
      text: "Simply enter your S3 bucket URL in the data panel and click 'Pull'. I'll fetch all available buckets and files for you to explore.",
    },
    
        { sender: "user", text: "How do I connect to my S3 bucket?" },
    {
      sender: "ai",
      text: "Simply enter your S3 bucket URL in the data panel and click 'Pull'. I'll fetch all available buckets and files for you to explore.",
    },
    
    
  ];

  return (
    <div className="flex gap-6 flex-grow">
      <div className="bg-neutral-800 relative flex-grow rounded-4xl flex flex-col">
        <div className="w-full max-h-[93.5vh] flex flex-col overflow-y-auto custom-scrollbar">
          <div className="w-full flex flex-col px-24 gap-6 py-4">
            {messages.map((msg, idx) => (
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
                  {msg.text}
                </div>
              </div>
            ))}
          </div>

          <div className="flex items-center justify-center px-6 py-6">
            <div className="h-[150px] w-full max-w-4xl flex flex-col gap-4 p-4 bg-neutral-900 rounded-4xl relative">
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

                {showDatasetSelector && (
                  <div className="absolute bottom-full mb-2 left-4 bg-neutral-800 border border-gray-600 rounded-lg p-3 shadow-lg z-10 min-w-[250px]">
                    <div className="text-sm text-gray-300 mb-2">
                      Select buckets from the Data Explorer panel →
                    </div>
                    <div className="text-xs text-gray-400">
                      Click the &quot;Add&quot; button next to any bucket to include it in
                      your conversation.
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

              <div className="flex flex-grow items-end">
                <textarea
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                  placeholder="Ask me anything about your data..."
                  className="resize-none flex-grow h-full bg-transparent text-white placeholder-gray-400 outline-none p-2 rounded-lg"
                />
                <button className="rounded-full h-11 w-11 ml-3 cursor-pointer bg-blue-500 hover:bg-blue-600 flex items-center justify-center transition-colors">
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
      />
    </div>
  );
}