"use client";
import {
  Message01Icon,
  Settings01Icon,
  ArrowDown01Icon,
  ArrowUp01Icon,
  Edit02Icon,
  CheckmarkCircle01Icon,
  Cancel01Icon,
  Add01Icon,
  Delete02Icon,
} from "@hugeicons/core-free-icons";
import { HugeiconsIcon } from "@hugeicons/react";
import Image from "next/image";
import React, { useEffect } from "react";
import SettingsModal from "./settingsModal";
import PostgreSQLModal from "./postgresqlModal";
import api from "@/lib/api";
import { useChatContext } from "@/contexts/ChatContext";

type ChatHistoryType = {
  title: string;
  id: string;
  created_at: string;
  updated_at: string;
  messages: Array<{
    role: "user" | "assistant";
    content: string;
  }>;
};

const Sidebar = () => {
  const { selectedChatId, selectChat, createNewChat, deleteChat } = useChatContext();
  const [openChatHistory, setOpenChatHistory] = React.useState(false);
  const [openSettings, setOpenSettings] = React.useState(false);
  const [showDatabricksModal, setShowDatabricksModal] = React.useState(false);
  const [showPostgreSQLModal, setShowPostgreSQLModal] = React.useState(false);
  const [chatHistory, setChatHistory] = React.useState<ChatHistoryType[]>([]);
  const [editingChatId, setEditingChatId] = React.useState<string | null>(null);
  const [newChatTitle, setNewChatTitle] = React.useState("");

  useEffect(() => {
    const fetchChatHistory = async () => {
      try {
        const response = await api.get("/conversations/");
        const data = response.data;
        console.log("Chat History:", data);
        setChatHistory(data);
      } catch (error) {
        console.error("Failed to fetch chat history:", error);
      }
    };

    fetchChatHistory();
  }, [selectedChatId]); // Refresh when selectedChatId changes

  const handleRenameChat = async (conversationId: string) => {
    if (!newChatTitle.trim() || !editingChatId) {
      setEditingChatId(null);
      return;
    }

    try {
      const response = await api.put(
        `/conversations/${conversationId}?title=${encodeURIComponent(
          newChatTitle
        )}`
      );
      const updatedChat = response.data;

      setChatHistory((prevChatHistory) =>
        prevChatHistory.map((chat) =>
          chat.id === conversationId
            ? { ...chat, title: updatedChat.title }
            : chat
        )
      );
    } catch (error) {
      console.error("Failed to rename chat:", error);
    } finally {
      setEditingChatId(null);
      setNewChatTitle("");
    }
  };

  const handleCancelEdit = () => {
    setEditingChatId(null);
    setNewChatTitle("");
  };

  const handleDeleteChat = async (chatId: string, chatTitle: string) => {
    if (confirm(`Are you sure you want to delete "${chatTitle}"?`)) {
      try {
        await deleteChat(chatId);
        // Remove the chat from local state
        setChatHistory((prevChatHistory) =>
          prevChatHistory.filter((chat) => chat.id !== chatId)
        );
      } catch (error) {
        console.error("Failed to delete chat:", error);
        alert("Failed to delete chat. Please try again.");
      }
    }
  };

  return (
    <div className="w-[350px] space-y-14 pr-15">
      <div className=" flex gap-4 items-center">
        <Image src="/logo.png" alt="Logo" width={60} height={60} />
        <span className=" font-bold text-2xl mt-2">D-ANTS</span>
      </div>
      <div className=" space-y-2">
        <div>
          <div className="flex items-center justify-between mb-2">
            <div
              onClick={() => setOpenChatHistory(!openChatHistory)}
              className="flex items-center justify-between space-x-2 p-2 hover:bg-neutral-700 rounded-lg cursor-pointer transition-all duration-300 flex-1"
            >
              <div className="flex items-center space-x-2">
                <HugeiconsIcon icon={Message01Icon} />
                <span>Chat History</span>
              </div>
              <HugeiconsIcon
                icon={openChatHistory ? ArrowUp01Icon : ArrowDown01Icon}
                className={`text-gray-400 transition-transform duration-300 ${
                  openChatHistory ? "rotate-180" : ""
                }`}
              />
            </div>
          </div>
          <div
            className={`ml-6 overflow-hidden transition-all duration-500 ease-in-out ${
              openChatHistory
                ? "max-h-80 opacity-100 mt-2"
                : "max-h-0 opacity-0 mt-0"
            }`}
          >
            <div className="space-y-1 max-h-80 overflow-y-auto pr-2 custom-scrollbar">
              <button
                onClick={createNewChat}
                className="p-2 bg-blue-500/5 text-sm items-center justify-center w-full border border-dashed border-blue-500/50 rounded-lg cursor-pointer transition-all duration-300 flex"
                title="New Chat"
              >
                Add new chat
                <HugeiconsIcon icon={Add01Icon} size={18} className="ml-4" />
              </button>
              {chatHistory.map((chat, index) => (
                <div
                  key={index}
                  onClick={() => !editingChatId && selectChat(chat.id)}
                  className={`group p-3 text-sm text-gray-300 hover:bg-neutral-700 hover:text-white rounded-lg cursor-pointer transition-all duration-300 truncate border-l-2 transform hover:translate-x-1 flex justify-between items-center ${
                    selectedChatId === chat.id
                      ? "bg-neutral-700 text-white border-blue-400"
                      : "border-transparent hover:border-blue-400"
                  } ${
                    openChatHistory
                      ? "translate-y-0 opacity-100"
                      : "translate-y-2 opacity-0"
                  }`}
                  style={{
                    transitionDelay: openChatHistory
                      ? `${index * 50}ms`
                      : "0ms",
                  }}
                >
                  {editingChatId === chat.id ? (
                    <div className="flex items-center w-full gap-2">
                      <input
                        type="text"
                        value={newChatTitle}
                        onChange={(e) => setNewChatTitle(e.target.value)}
                        onKeyDown={(e) => {
                          if (e.key === "Enter") {
                            handleRenameChat(chat.id);
                          }
                          if (e.key === "Escape") {
                            handleCancelEdit();
                          }
                        }}
                        className="bg-neutral-800 text-white rounded-md px-2 py-1 w-full focus:outline-none focus:ring-1 focus:ring-blue-500"
                        autoFocus
                      />
                      <button onClick={() => handleRenameChat(chat.id)}>
                        <HugeiconsIcon
                          icon={CheckmarkCircle01Icon}
                          size={18}
                          className="text-green-500 hover:text-green-400 cursor-pointer"
                        />
                      </button>
                      <button onClick={handleCancelEdit}>
                        <HugeiconsIcon
                          icon={Cancel01Icon}
                          size={18}
                          className="text-red-500 hover:text-red-400 cursor-pointer"
                        />
                      </button>
                    </div>
                  ) : (
                    <>
                      <span className="truncate" title={chat.title}>
                        {chat.title}
                      </span>
                      <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            setEditingChatId(chat.id);
                            setNewChatTitle(chat.title);
                          }}
                          className="hover:bg-neutral-600 p-1 rounded transition-colors duration-300 cursor-pointer"
                          title="Rename chat"
                        >
                          <HugeiconsIcon icon={Edit02Icon} size={14} />
                        </button>
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            handleDeleteChat(chat.id, chat.title);
                          }}
                          className="hover:bg-red-500/20 text-red-400 hover:text-red-300 p-1 rounded transition-colors duration-300 cursor-pointer"
                          title="Delete chat"
                        >
                          <HugeiconsIcon icon={Delete02Icon} size={14} />
                        </button>
                      </div>
                    </>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>

        <div>
          <div
            onClick={() => setOpenSettings(!openSettings)}
            className="flex items-center justify-between space-x-2 p-2 hover:bg-neutral-700 rounded-lg cursor-pointer transition-all duration-300"
          >
            <div className="flex items-center space-x-2">
              <HugeiconsIcon icon={Settings01Icon} />
              <span>Settings</span>
            </div>
            <HugeiconsIcon
              icon={openSettings ? ArrowUp01Icon : ArrowDown01Icon}
              className={`text-gray-400 transition-transform duration-300 ${
                openSettings ? "rotate-180" : ""
              }`}
            />
          </div>
          <div
            className={`ml-6 overflow-hidden transition-all duration-500 ease-in-out ${
              openSettings
                ? "max-h-32 opacity-100 mt-2"
                : "max-h-0 opacity-0 mt-0"
            }`}
          >
            <div className="space-y-1">
              <button
                onClick={() => setShowDatabricksModal(true)}
                className={`w-full text-left p-3 text-sm text-gray-300 hover:bg-neutral-700 hover:text-white rounded-lg cursor-pointer transition-all duration-300 border-l-2 border-transparent hover:border-orange-400 transform hover:translate-x-1 ${
                  openSettings
                    ? "translate-y-0 opacity-100"
                    : "translate-y-2 opacity-0"
                }`}
                style={{
                  transitionDelay: openSettings ? "50ms" : "0ms",
                }}
              >
                Databricks
              </button>
              <button
                onClick={() => setShowPostgreSQLModal(true)}
                className={`w-full text-left p-3 text-sm text-gray-300 hover:bg-neutral-700 hover:text-white rounded-lg cursor-pointer transition-all duration-300 border-l-2 border-transparent hover:border-blue-400 transform hover:translate-x-1 ${
                  openSettings
                    ? "translate-y-0 opacity-100"
                    : "translate-y-2 opacity-0"
                }`}
                style={{
                  transitionDelay: openSettings ? "100ms" : "0ms",
                }}
              >
                PostgreSQL
              </button>
            </div>
          </div>
        </div>
      </div>

      {showDatabricksModal && (
        <SettingsModal onClose={() => setShowDatabricksModal(false)} />
      )}
      {showPostgreSQLModal && (
        <PostgreSQLModal onClose={() => setShowPostgreSQLModal(false)} />
      )}
    </div>
  );
};

export default Sidebar;
