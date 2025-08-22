"use client";

import { useState } from 'react';
import CodeBlock from './CodeBlock';
import { CodeIcon, Database01Icon, ArrowDown01Icon, ArrowUp01Icon } from '@hugeicons/core-free-icons';
import { HugeiconsIcon } from '@hugeicons/react';

interface Message {
  id?: number;
  sender: "user" | "assistant";
  text: string;
  sources?: string[];
  codes?: string[];
  created_at?: string;
}

interface MessageDisplayProps {
  message: Message;
}

const extractAnswerContent = (text: string): string => {
  const answerMatch = text.match(/<answer>([\s\S]*?)<\/answer>/);
  return answerMatch ? answerMatch[1].trim() : text;
};

export default function MessageDisplay({ message }: MessageDisplayProps) {
  const [showCode, setShowCode] = useState(false);
  const [showSources, setShowSources] = useState(false);

  // Check if we have actual data to display
  const hasCode = message.codes && message.codes.length > 0;
  const hasSources = message.sources && message.sources.length > 0;
  
  // Only use actual data, no test/sample data
  const displaySources = hasSources;
  const displayCodes = hasCode;

  return (
    <div className="space-y-3">
      {/* Main message content */}
      <div
        className={`px-6 py-4 rounded-3xl text-base max-w-[70%] whitespace-pre-line shadow-md transition-all duration-200
          ${
            message.sender === "user"
              ? "bg-blue-500 text-white rounded-br-md"
              : "bg-white/10 text-white border border-white/10 rounded-bl-md"
          }
        `}
        style={{ wordBreak: "break-word" }}
      >
        {extractAnswerContent(message.text)}
      </div>

      {/* Sources section */}
      {displaySources && (
        <div className="max-w-[70%]">
          <button
            onClick={() => setShowSources(!showSources)}
            className="flex items-center gap-2 px-3 py-2 bg-neutral-800 hover:bg-neutral-700 rounded-lg transition-colors text-sm text-gray-300"
          >
            <HugeiconsIcon icon={Database01Icon} size={16} />
            <span>Sources ({message.sources!.length})</span>
            <HugeiconsIcon 
              icon={showSources ? ArrowUp01Icon : ArrowDown01Icon} 
              size={16} 
            />
          </button>
          
          {showSources && (
            <div className="mt-2 space-y-2">
              {message.sources!.map((source: string, index: number) => (
                <div 
                  key={index}
                  className="bg-neutral-800/50 border border-white/10 rounded-lg px-4 py-3"
                >
                  <div className="flex items-start gap-3">
                    <HugeiconsIcon icon={Database01Icon} size={16} className="text-blue-400 mt-0.5 flex-shrink-0" />
                    <div className="flex-1">
                      <div className="text-sm text-gray-300 font-mono break-all">
                        {source}
                      </div>
                      <div className="text-xs text-gray-500 mt-1">
                        Dataset {index + 1}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Code section */}
      {displayCodes && (
        <div className="max-w-[70%]">
          <button
            onClick={() => setShowCode(!showCode)}
            className="flex items-center gap-2 px-3 py-2 bg-neutral-800 hover:bg-neutral-700 rounded-lg transition-colors text-sm text-gray-300"
          >
            <HugeiconsIcon icon={CodeIcon} size={16} />
            <span>View Code ({message.codes!.length} snippet{message.codes!.length > 1 ? 's' : ''})</span>
            <HugeiconsIcon 
              icon={showCode ? ArrowUp01Icon : ArrowDown01Icon} 
              size={16} 
            />
          </button>
          
          {showCode && (
            <div className="mt-3 space-y-3">
              {message.codes!.map((code: string, index: number) => (
                <div key={index} className="space-y-2">
                  {message.codes!.length > 1 && (
                    <div className="text-sm text-gray-400 font-medium">
                      Code Snippet {index + 1}
                    </div>
                  )}
                  <CodeBlock code={code} language="python" />
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
