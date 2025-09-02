"use client";

import React, { createContext, useContext, useState, ReactNode } from "react";
import { useRouter } from "next/navigation";
import api from "@/lib/api";

interface Message {
  id?: number;
  sender: "user" | "assistant";
  text: string;
  sources?: string[];
  codes?: string[];
  table_data?: any[];
  charts?: any[];
  created_at?: string;
}

interface ChatContextType {
  selectedChatId: string | null;
  currentChatTitle: string | null;
  messages: Message[];
  loading: boolean;
  selectedFiles: Array<{ name: string; path: string; data: any }>;
  selectChat: (chatId: string) => Promise<void>;
  sendMessage: (message: string, datasets?: string[], modelType?: string) => Promise<void>;
  clearChat: () => void;
  createNewChat: () => void;
  deleteChat: (chatId: string) => Promise<void>;
  setSelectedFiles: (files: Array<{ name: string; path: string; data: any }>) => void;
}

const ChatContext = createContext<ChatContextType | undefined>(undefined);

export const useChatContext = () => {
  const context = useContext(ChatContext);
  if (!context) {
    throw new Error("useChatContext must be used within a ChatProvider");
  }
  return context;
};

interface ChatProviderProps {
  children: ReactNode;
}

export const ChatProvider: React.FC<ChatProviderProps> = ({ children }) => {
  const router = useRouter();
  const [selectedChatId, setSelectedChatId] = useState<string | null>(null);
  const [currentChatTitle, setCurrentChatTitle] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedFiles, setSelectedFiles] = useState<Array<{ name: string; path: string; data: any }>>([]);

  const selectChat = async (chatId: string) => {
    setLoading(true);
    try {
      const response = await api.get(`/conversations/${chatId}`);
      const conversation = response.data;

      const transformedMessages: Message[] =
        conversation.messages?.map((msg: any) => ({
          id: msg.id,
          sender: msg.sender_type === "user" ? "user" : "assistant",
          text: msg.content,
          sources: msg.sources || [],
          codes: msg.codes || [],
          table_data: msg.table_data || [],
          charts: msg.charts || [],
          created_at: msg.created_at,
        })) || [];

      setSelectedChatId(chatId);
      setCurrentChatTitle(conversation.title || `Chat ${chatId.slice(0, 8)}`);
      setMessages(transformedMessages);
    } catch (error) {
      console.error("Failed to load chat messages:", error);
      setSelectedChatId(chatId);
      setCurrentChatTitle(`Chat ${chatId.slice(0, 8)}`);
      setMessages([]);
    } finally {
      setLoading(false);
    }
  };

  const sendMessage = async (messageText: string, datasets?: string[], modelType?: string) => {
    if (!messageText.trim()) return;

    const userMessage: Message = {
      sender: "user",
      text: messageText,
    };
    setMessages((prev) => [...prev, userMessage]);
    setLoading(true);

    try {
      const requestBody = selectedChatId 
        ? {
            content: messageText,
            conversation_id: selectedChatId,
            available_datasets: datasets || [],
            model_type: modelType || "ollama",
          }
        : {
            content: messageText,
            available_datasets: datasets || [],
            model_type: modelType || "ollama",
          };

      
      const response = await api.post("/messages/", requestBody);
      
      if (response.data.error) {
        console.error("Chat response error:", response.data.error);
        const errorMessage: Message = {
          sender: "assistant",
          text: "Sorry, I encountered an error processing your message. Please try again.",
        };
        setMessages((prev) => [...prev, errorMessage]);
        return;
      }

      if (response.data.message) {
        const { content, conversation_id, sources, codes, table_data, charts } = response.data.message;
                
        if (!selectedChatId && conversation_id) {
          setSelectedChatId(conversation_id);
          router.push(`/chat/${conversation_id}`);
        }

        const assistantMessage: Message = {
          id: response.data.message.id,
          sender: "assistant",
          text: content,
          sources: sources || [],
          codes: codes || [],
          table_data: table_data || [],
          charts: charts || [],
        };

        setMessages((prev) => [...prev, assistantMessage]);
      } else {
        console.warn("Unexpected response structure:", response.data);
        const fallbackMessage: Message = {
          sender: "assistant",
          text: "I received your message but couldn't process the response properly.",
        };
        setMessages((prev) => [...prev, fallbackMessage]);
      }
    } catch (error) {
      console.error("Failed to send message:", error);
      setMessages((prev) => prev.slice(0, -1));
    } finally {
      setLoading(false);
    }
  };

  const clearChat = () => {
    setSelectedChatId(null);
    setCurrentChatTitle(null);
    setMessages([]);
  };

  const createNewChat = () => {
    setSelectedChatId(null);
    setCurrentChatTitle(null);
    setMessages([]);
    router.push("/");
  };

  const deleteChat = async (chatId: string) => {
    try {
      await api.delete(`/conversations/${chatId}`);

      if (selectedChatId === chatId) {
        clearChat();
      }
    } catch (error) {
      console.error("Failed to delete chat:", error);
      throw error;
    }
  };

  const value: ChatContextType = {
    selectedChatId,
    currentChatTitle,
    messages,
    loading,
    selectedFiles,
    selectChat,
    sendMessage,
    clearChat,
    createNewChat,
    deleteChat,
    setSelectedFiles,
  };

  return <ChatContext.Provider value={value}>{children}</ChatContext.Provider>;
};
