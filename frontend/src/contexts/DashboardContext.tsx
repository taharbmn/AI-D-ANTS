"use client";

import React, { createContext, useContext, useState, ReactNode } from "react";

export interface DashboardItem {
  id: string;
  type: "chart" | "table";
  title: string;
  data: any[];
  labels?: Array<{ name: string; color: string }>;
  addedAt: Date;
}

interface DashboardContextType {
  dashboardItems: DashboardItem[];
  addToDashboard: (item: Omit<DashboardItem, "id" | "addedAt">) => void;
  removeFromDashboard: (id: string) => void;
  clearDashboard: () => void;
}

const DashboardContext = createContext<DashboardContextType | undefined>(undefined);

export const useDashboardContext = () => {
  const context = useContext(DashboardContext);
  if (!context) {
    throw new Error("useDashboardContext must be used within a DashboardProvider");
  }
  return context;
};

interface DashboardProviderProps {
  children: ReactNode;
}

export const DashboardProvider: React.FC<DashboardProviderProps> = ({ children }) => {
  const [dashboardItems, setDashboardItems] = useState<DashboardItem[]>([]);

  const addToDashboard = (item: Omit<DashboardItem, "id" | "addedAt">) => {
    const newItem: DashboardItem = {
      ...item,
      id: `${item.type}-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      addedAt: new Date()
    };
    
    setDashboardItems(prev => [...prev, newItem]);
  };

  const removeFromDashboard = (id: string) => {
    setDashboardItems(prev => prev.filter(item => item.id !== id));
  };

  const clearDashboard = () => {
    setDashboardItems([]);
  };

  return (
    <DashboardContext.Provider 
      value={{ 
        dashboardItems, 
        addToDashboard, 
        removeFromDashboard, 
        clearDashboard 
      }}
    >
      {children}
    </DashboardContext.Provider>
  );
};
