"use client";

import { useState } from 'react';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { Copy01Icon, Tick01Icon } from '@hugeicons/core-free-icons';
import { HugeiconsIcon } from '@hugeicons/react';

interface CodeBlockProps {
  code: string;
  language?: string;
}

export default function CodeBlock({ code, language = 'python' }: CodeBlockProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(code);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy code:', err);
    }
  };

  return (
    <div className="relative bg-neutral-900 rounded-lg overflow-hidden border border-white/10">
      <div className="flex items-center justify-between px-4 py-2 bg-neutral-800 border-b border-white/10">
        <span className="text-sm text-gray-400 font-medium">{language}</span>
        <button
          onClick={handleCopy}
          className="flex items-center gap-2 px-2 py-1 text-xs text-gray-400 hover:text-white hover:bg-white/10 rounded transition-all"
        >
          <HugeiconsIcon 
            icon={copied ? Tick01Icon : Copy01Icon} 
            size={14} 
          />
          {copied ? 'Copied!' : 'Copy'}
        </button>
      </div>
      <div className="overflow-x-auto">
        <SyntaxHighlighter
          language={language}
          style={vscDarkPlus}
          customStyle={{
            margin: 0,
            padding: '16px',
            backgroundColor: 'transparent',
            fontSize: '14px',
            lineHeight: '1.5',
          }}
          showLineNumbers={true}
          lineNumberStyle={{
            color: '#6b7280',
            fontSize: '12px',
            minWidth: '3em',
            paddingRight: '1em',
          }}
        >
          {code}
        </SyntaxHighlighter>
      </div>
    </div>
  );
}
