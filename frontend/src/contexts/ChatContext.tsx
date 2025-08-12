"use client";

import React, { createContext, useContext, useState, ReactNode } from "react";
import api from "@/lib/api";

interface Message {
  sender: "user" | "ai";
  text: string;
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
          sender: msg.role === "user" ? "user" : "ai",
          text: msg.content,
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
      let conversationId = selectedChatId;
      let response = null;
      if (!conversationId) {
        response = await api.post("/messages/", {
          content: messageText,
        });
        conversationId = response.data.conversation.id;
        setSelectedChatId(conversationId);
        console.log("new conversation created:", conversationId);
      } else {
        response = await api.post(`/messages/`, {
          content: messageText,
          conversation_id: conversationId,
        });
        console.log("message sent:", response.data, " ------------ ", conversationId);
      }
      const aiResponse =
        response.data.response ||
        "I received your message and I'm processing it.";

      const aiMessage: Message = {
        sender: "ai",
        text: aiResponse,
      };

      setMessages((prev) => [...prev, aiMessage]);
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
