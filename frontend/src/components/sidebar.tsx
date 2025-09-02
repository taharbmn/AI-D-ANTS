"use client";
import {
  Message01Icon,
  ArrowDown01Icon,
  ArrowUp01Icon,
  Edit02Icon,
  CheckmarkCircle01Icon,
  Cancel01Icon,
  Add01Icon,
  Delete02Icon,
  AiCloudIcon,
  Menu01Icon,
  ArrowRight02Icon,
  ArrowLeft02Icon,
} from "@hugeicons/core-free-icons";
import { HugeiconsIcon } from "@hugeicons/react";
import Image from "next/image";
import React, { useEffect } from "react";
import { useRouter } from "next/navigation";
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
  const router = useRouter();
  const { selectedChatId, selectChat, createNewChat, deleteChat } =
    useChatContext();
  const [isCollapsed, setIsCollapsed] = React.useState(false);
  const [openChatHistory, setOpenChatHistory] = React.useState(false);
  const [openModels, setOpenModels] = React.useState(false);
  const [showDatabricksModal, setShowDatabricksModal] = React.useState(false);
  const [showOllamaModal, setShowOllamaModal] = React.useState(false);
  const [chatHistory, setChatHistory] = React.useState<ChatHistoryType[]>([]);
  const [editingChatId, setEditingChatId] = React.useState<string | null>(null);
  const [newChatTitle, setNewChatTitle] = React.useState("");
  const [ollamaModelName, setOllamaModelName] = React.useState("");
  const [isSidebarOpen, setIsSidebarOpen] = React.useState(false);
  const [isXlScreen, setIsXlScreen] = React.useState(false);

  // Check screen size
  useEffect(() => {
    const checkScreenSize = () => {
      setIsXlScreen(window.innerWidth >= 1280);
    };
    
    checkScreenSize();
    window.addEventListener('resize', checkScreenSize);
    
    return () => window.removeEventListener('resize', checkScreenSize);
  }, []);

  useEffect(() => {
    const fetchChatHistory = async () => {
      try {
        const response = await api.get("/conversations/");
        const data = response.data;
        setChatHistory(data);
      } catch (error) {
        console.error("Failed to fetch chat history:", error);
      }
    };

    fetchChatHistory();
  }, [selectedChatId]);

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

  const handleSaveOllamaModel = () => {
    if (ollamaModelName.trim()) {
      localStorage.setItem("ollamaModelName", ollamaModelName.trim());
      setOllamaModelName("");
      setShowOllamaModal(false);
    }
  };

  const handleCancelOllamaModal = () => {
    setOllamaModelName("");
    setShowOllamaModal(false);
  };

  const handleDeleteChat = async (chatId: string, chatTitle: string) => {
    try {
      await deleteChat(chatId);
      setChatHistory((prevChatHistory) =>
        prevChatHistory.filter((chat) => chat.id !== chatId)
      );
    } catch (error) {
      console.error("Failed to delete chat:", error);
      alert("Failed to delete chat. Please try again.");
    }
  };

  return (
    <>
      {/* Overlay for mobile sidebar */}
      {isSidebarOpen && !isXlScreen && (
        <div 
          className="fixed inset-0 bg-black/50 z-30 xl:hidden"
          onClick={() => setIsSidebarOpen(false)}
        />
      )}

      {/* Floating Toggle Button - Only visible on screens smaller than xl */}
      <button
        onClick={() => setIsSidebarOpen(!isSidebarOpen)}
        className={`fixed top-1/2 -translate-y-1/2 xl:hidden z-50 w-12 h-12 bg-blue-500 hover:bg-blue-600 rounded-full flex items-center justify-center shadow-lg transition-all duration-300 ${
          isSidebarOpen ? 'left-[21rem]' : 'left-4'
        }`}
      >
        <HugeiconsIcon 
          icon={isSidebarOpen ? ArrowLeft02Icon : ArrowRight02Icon} 
          size={20} 
          className="text-white" 
        />
      </button>

      {/* Sidebar Container - Absolute on small screens, relative on xl+ */}
      <div
        className={`transition-all duration-300 ease-in-out bg-neutral-900 
          fixed xl:relative top-0 xl:top-0 left-0 xl:left-0 bottom-0 xl:bottom-0 
          w-80 z-40 xl:z-auto rounded-r-2xl xl:rounded-none
          ${isSidebarOpen ? 'translate-x-0' : '-translate-x-full xl:translate-x-0'}
          ${isCollapsed ? "xl:w-18" : "xl:min-w-[350px] xl:max-w-[350px]"} 
          xl:pr-10 p-6 xl:p-0 overflow-y-auto`}
      >
        <div className={`flex gap-4 items-center ${isCollapsed && isXlScreen ? "justify-center w-18" : "justify-between w-full" } mb-8 `}>
          {(!isCollapsed || !isXlScreen) && (
            <div className="flex gap-4 items-center">
              <Image src="/logo.png" alt="Logo" width={60} height={60} />
              <span className="font-bold text-2xl mt-2">AI-D-ANTS</span>
            </div>
          )}
          {/* Only show collapse button on xl+ screens */}
          {isXlScreen && (
            <button
              onClick={() => setIsCollapsed(!isCollapsed)}
              className="p-2 hover:bg-neutral-700 rounded-lg cursor-pointer transition-all duration-300"
              title="Collapse Sidebar"
            >
              <HugeiconsIcon icon={Menu01Icon} size={24} />
            </button>
          )}
        </div>

        {isCollapsed && isXlScreen ? (
          <div className="space-y-4 flex flex-col items-center w-18">
            <button
              onClick={() => {
                setIsCollapsed(false);
                setTimeout(() => setOpenChatHistory(true), 100);
              }}
              className="p-3 hover:bg-neutral-700 rounded-lg cursor-pointer transition-all duration-200 flex items-center justify-center"
              title="Chat History"
            >
              <HugeiconsIcon icon={Message01Icon} size={24} />
            </button>
            <button
              onClick={() => {
                setIsCollapsed(false);
                setTimeout(() => setOpenModels(true), 100);
              }}
              className="p-3 hover:bg-neutral-700 rounded-lg cursor-pointer transition-all duration-200 flex items-center justify-center"
              title="Models"
            >
              <HugeiconsIcon icon={AiCloudIcon} size={24} />
            </button>
          </div>
        ) : (
        <div className="space-y-6">
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
                    onClick={() => !editingChatId && router.push(`/chat/${chat.id}`)}
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

          {/* Models Section */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <div
                onClick={() => setOpenModels(!openModels)}
                className="flex items-center justify-between space-x-2 p-2 hover:bg-neutral-700 rounded-lg cursor-pointer transition-all duration-300 flex-1"
              >
                <div className="flex items-center space-x-2">
                  <HugeiconsIcon icon={AiCloudIcon} />
                  <span>Models</span>
                </div>
                <HugeiconsIcon
                  icon={openModels ? ArrowUp01Icon : ArrowDown01Icon}
                  className={`text-gray-400 transition-transform duration-300 ${
                    openModels ? "rotate-180" : ""
                  }`}
                />
              </div>
            </div>
            <div
              className={`ml-6 overflow-hidden transition-all duration-500 ease-in-out ${
                openModels
                  ? "max-h-40 opacity-100 mt-2"
                  : "max-h-0 opacity-0 mt-0"
              }`}
            >
              <div className="space-y-2">
                <button
                  onClick={() => setShowOllamaModal(true)}
                  className="flex items-center space-x-2 p-2 hover:bg-neutral-700 rounded-lg cursor-pointer transition-all duration-300 w-full text-left border-l-2 border-transparent hover:border-green-400 transform hover:translate-x-1"
                >
                  <span className="text-sm">Ollama</span>
                </button>
                <button
                  onClick={() => setShowDatabricksModal(true)}
                  className="flex items-center space-x-2 p-2 hover:bg-neutral-700 rounded-lg cursor-pointer transition-all duration-300 w-full text-left border-l-2 border-transparent hover:border-orange-400 transform hover:translate-x-1"
                >
                  <span className="text-sm">Databricks</span>
                </button>
              </div>
            </div>
          </div>
        </div>
        )}

      {showOllamaModal && (
        <div className="h-screen w-screen absolute inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-neutral-800 rounded-3xl p-10 w-full max-w-lg shadow-2xl border border-neutral-700">
            <h2 className="text-2xl font-bold mb-6 text-white text-center tracking-wide">
              Configure Ollama Model
            </h2>
            <div className="space-y-4">
              <div className="flex flex-col gap-1">
                <label className="text-base text-gray-200 font-medium">
                  Model Name<span className="text-red-400">*</span>
                </label>
                <input
                  className="rounded-2xl border border-gray-500 bg-neutral-900 text-white px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-400 transition-all"
                  type="text"
                  value={ollamaModelName}
                  onChange={(e) => setOllamaModelName(e.target.value)}
                  placeholder="e.g., llama3.1:8b, mistral:7b"
                  onKeyDown={(e) => {
                    if (e.key === "Enter") {
                      handleSaveOllamaModel();
                    }
                    if (e.key === "Escape") {
                      handleCancelOllamaModal();
                    }
                  }}
                  autoFocus
                  autoComplete="off"
                />
              </div>
            </div>
            <div className="flex justify-between mt-8">
              <button
                onClick={handleCancelOllamaModal}
                className="text-base cursor-pointer text-blue-400 hover:underline"
              >
                Cancel
              </button>
              <button
                onClick={handleSaveOllamaModel}
                disabled={!ollamaModelName.trim()}
                className="bg-blue-500 cursor-pointer hover:bg-blue-600 disabled:bg-gray-600 disabled:cursor-not-allowed text-white rounded-2xl px-7 py-2 font-semibold transition-colors shadow"
              >
                Save
              </button>
            </div>
          </div>
        </div>
      )}

      {showDatabricksModal && (
        <SettingsModal onClose={() => setShowDatabricksModal(false)} />
      )}
      </div>
    </>
  );
};

export default Sidebar;
