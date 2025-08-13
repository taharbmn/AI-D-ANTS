"use client";

import React, { createContext, useContext, useState, ReactNode } from "react";
import api from "@/lib/api";

interface Message {
  id?: number;
  sender: "user" | "assistant";
  text: string;
  created_at?: string;
}

interface ChatContextType {
  selectedChatId: string | null;
  messages: Message[];
  loading: boolean;
  selectChat: (chatId: string) => Promise<void>;
  sendMessage: (message: string) => Promise<void>;
  clearChat: () => void;
  createNewChat: () => void;
  deleteChat: (chatId: string) => Promise<void>;
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
  const [selectedChatId, setSelectedChatId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);

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
          created_at: msg.created_at,
        })) || [];

      setSelectedChatId(chatId);
      setMessages(transformedMessages);
    } catch (error) {
      console.error("Failed to load chat messages:", error);
      setSelectedChatId(chatId);
      setMessages([]);
    } finally {
      setLoading(false);
    }
  };

  const sendMessage = async (messageText: string) => {
    if (!messageText.trim()) return;

    const userMessage: Message = {
      sender: "user",
      text: messageText,
    };
    setMessages((prev) => [...prev, userMessage]);

    try {
      const requestBody = selectedChatId 
        ? {
            content: messageText,
            conversation_id: selectedChatId,
          }
        : {
            content: messageText,
          };

      const response = await api.post("/messages/", requestBody);
      
      // Handle the exact response format from the backend
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
        const { content, conversation_id } = response.data.message;
        
        if (!selectedChatId && conversation_id) {
          setSelectedChatId(conversation_id);
          console.log("New conversation created:", conversation_id);
        }

        const assistantMessage: Message = {
          id: response.data.message.id,
          sender: "assistant",
          text: content,
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
    }
  };

  const clearChat = () => {
    setSelectedChatId(null);
    setMessages([]);
  };

  const createNewChat = () => {
    setSelectedChatId(null);
    setMessages([]);
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
    messages,
    loading,
    selectChat,
    sendMessage,
    clearChat,
    createNewChat,
    deleteChat,
  };

  return <ChatContext.Provider value={value}>{children}</ChatContext.Provider>;
};
