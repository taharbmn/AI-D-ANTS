'use client'
import {
  Message01Icon,
  Settings01Icon,
  ArrowDown01Icon,
  ArrowUp01Icon,
} from "@hugeicons/core-free-icons";
import { HugeiconsIcon } from "@hugeicons/react";
import Image from "next/image";
import React from "react";
import SettingsModal from "./settingsModal";
import PostgreSQLModal from "./postgresqlModal";

const Sidebar = () => {
  const [openChatHistory, setOpenChatHistory] = React.useState(false);
  const [openSettings, setOpenSettings] = React.useState(false);
  const [showDatabricksModal, setShowDatabricksModal] = React.useState(false);
  const [showPostgreSQLModal, setShowPostgreSQLModal] = React.useState(false);

  const chatHistory = [
    "Sales Anomaly Analysis Q2",
    "Customer Behavior Insights",
    "Revenue Forecasting Model",
    "Product Performance Review",
    "Market Trend Analysis"
  ];

  return (
    <div className="w-[350px] space-y-14 pr-15">
      <div className=" flex gap-4 items-center">
        <Image src="/logo.png" alt="Logo" width={60} height={60} />
        <span className=" font-bold text-2xl mt-2">D-ANTS</span>
      </div>
      <div className=" space-y-2">
        {/* Chat History Section */}
        <div>
          <div 
            onClick={() => setOpenChatHistory(!openChatHistory)} 
            className="flex items-center justify-between space-x-2 p-2 hover:bg-neutral-700 rounded-lg cursor-pointer transition-all duration-300"
          >
            <div className="flex items-center space-x-2">
              <HugeiconsIcon icon={Message01Icon} />
              <span>Chat History</span>
            </div>
            <HugeiconsIcon 
              icon={openChatHistory ? ArrowUp01Icon : ArrowDown01Icon} 
              className={`text-gray-400 transition-transform duration-300 ${openChatHistory ? 'rotate-180' : ''}`}
            />
          </div>
          {/* Chat History Dropdown with smooth animation */}
          <div 
            className={`ml-6 overflow-hidden transition-all duration-500 ease-in-out ${
              openChatHistory ? 'max-h-80 opacity-100 mt-2' : 'max-h-0 opacity-0 mt-0'
            }`}
          >
            <div className="space-y-1 max-h-80 overflow-y-auto pr-2 custom-scrollbar">
              {chatHistory.map((chat, index) => (
                <div 
                  key={index}
                  className={`p-3 text-sm text-gray-300 hover:bg-neutral-700 hover:text-white rounded-lg cursor-pointer transition-all duration-300 truncate border-l-2 border-transparent hover:border-blue-400 transform hover:translate-x-1 ${
                    openChatHistory ? 'translate-y-0 opacity-100' : 'translate-y-2 opacity-0'
                  }`}
                  style={{ 
                    transitionDelay: openChatHistory ? `${index * 50}ms` : '0ms'
                  }}
                  title={chat}
                >
                  {chat}
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Settings Section */}
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
              className={`text-gray-400 transition-transform duration-300 ${openSettings ? 'rotate-180' : ''}`}
            />
          </div>
          {/* Settings Dropdown with smooth animation */}
          <div 
            className={`ml-6 overflow-hidden transition-all duration-500 ease-in-out ${
              openSettings ? 'max-h-32 opacity-100 mt-2' : 'max-h-0 opacity-0 mt-0'
            }`}
          >
            <div className="space-y-1">
              <button 
                onClick={() => setShowDatabricksModal(true)}
                className={`w-full text-left p-3 text-sm text-gray-300 hover:bg-neutral-700 hover:text-white rounded-lg cursor-pointer transition-all duration-300 border-l-2 border-transparent hover:border-orange-400 transform hover:translate-x-1 ${
                  openSettings ? 'translate-y-0 opacity-100' : 'translate-y-2 opacity-0'
                }`}
                style={{ 
                  transitionDelay: openSettings ? '50ms' : '0ms'
                }}
              >
                Databricks
              </button>
              <button 
                onClick={() => setShowPostgreSQLModal(true)}
                className={`w-full text-left p-3 text-sm text-gray-300 hover:bg-neutral-700 hover:text-white rounded-lg cursor-pointer transition-all duration-300 border-l-2 border-transparent hover:border-blue-400 transform hover:translate-x-1 ${
                  openSettings ? 'translate-y-0 opacity-100' : 'translate-y-2 opacity-0'
                }`}
                style={{ 
                  transitionDelay: openSettings ? '100ms' : '0ms'
                }}
              >
                PostgreSQL
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Modals */}
      {showDatabricksModal && (
        <SettingsModal 
          open={showDatabricksModal} 
          onClose={() => setShowDatabricksModal(false)} 
        />
      )}
      {showPostgreSQLModal && (
        <PostgreSQLModal
          open={showPostgreSQLModal} 
          onClose={() => setShowPostgreSQLModal(false)} 
        />
      )}
    </div>
  );
};

export default Sidebar;
