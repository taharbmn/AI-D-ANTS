"use client";

import { Button } from "@/components/ui/button";
import ChartComponent from "./ChartComponent";
import TableComponent from "./TableComponent";
import { useDashboardContext } from "@/contexts/DashboardContext";
import { Delete02Icon } from '@hugeicons/core-free-icons';
import { HugeiconsIcon } from '@hugeicons/react';

export function Dashboard() {
  const { dashboardItems, removeFromDashboard, clearDashboard } = useDashboardContext();

  if (dashboardItems.length === 0) {
    return (
      <div className="space-y-6 relative">
        <div className="text-center py-12">
          <h2 className="text-2xl font-bold text-white mb-4">Your Dashboard</h2>
          <p className="text-neutral-400 mb-6">
            No items added to dashboard yet. Add charts and tables from your conversations to see them here.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6 relative">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-white">Your Dashboard</h2>
        <Button 
          variant="outline" 
          onClick={clearDashboard}
          className="bg-red-600 border-red-500 text-white hover:bg-red-700"
        >
          Clear All
        </Button>
      </div>

      <div className="grid grid-cols-1 gap-6">
        {dashboardItems.map((item) => (
          <div key={item.id} className="relative group">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => removeFromDashboard(item.id)}
              className="absolute top-2 right-2 z-10 opacity-0 group-hover:opacity-100 transition-opacity bg-red-600 hover:bg-red-700 text-white"
            >
              <HugeiconsIcon icon={Delete02Icon} size={16} />
            </Button>
            
            {item.type === "chart" ? (
              <ChartComponent 
                title={item.title}
                data={item.data}
                labels={item.labels}
                xAxisKey={item.xAxisKey}
                yAxisConfig={item.yAxisConfig}
                showAddButton={false}
              />
            ) : (
              <TableComponent 
                title={item.title}
                data={item.data}
                showAddButton={false}
              />
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
