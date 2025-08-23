"use client";

import { useState } from "react";
import { CartesianGrid, Line, LineChart, XAxis, YAxis, ResponsiveContainer } from "recharts";
import { ChartContainer, ChartTooltip, ChartTooltipContent } from "@/components/ui/chart";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { BarChartIcon, Add01Icon, Tick01Icon } from '@hugeicons/core-free-icons';
import { HugeiconsIcon } from '@hugeicons/react';
import { useDashboardContext } from "@/contexts/DashboardContext";

const chartConfig = {
  desktop: {
    label: "Desktop",
    color: "#3b82f6",
  },
  mobile: {
    label: "Mobile", 
    color: "#10b981",
  },
};

interface ChartComponentProps {
  title: string;
  data: any[];
  labels?: Array<{ name: string; color: string }>;
  showAddButton?: boolean;
}

export default function ChartComponent({ 
  title, 
  data, 
  labels, 
  showAddButton = false 
}: ChartComponentProps) {
  const { addToDashboard } = useDashboardContext();
  const [isAdded, setIsAdded] = useState(false);

  const handleAddToDashboard = () => {
    if (addToDashboard) {
      addToDashboard({
        type: "chart",
        title,
        data,
        labels
      });
      setIsAdded(true);
      // Reset the state after 2 seconds
      setTimeout(() => setIsAdded(false), 2000);
    }
  };

  return (
    <Card className="bg-neutral-700 border-neutral-600">
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4">
        <div className="flex items-center gap-2">
          <HugeiconsIcon icon={BarChartIcon} size={20} className="text-blue-400" />
          <CardTitle className="text-white text-lg">{title}</CardTitle>
        </div>
        {showAddButton && (
          <Button 
            variant="outline" 
            size="sm"
            onClick={handleAddToDashboard}
            disabled={isAdded}
            className={`transition-all duration-200 ${
              isAdded 
                ? "bg-green-600 border-green-500 text-white" 
                : "bg-blue-600 border-blue-500 text-white hover:bg-blue-700"
            }`}
          >
            <HugeiconsIcon 
              icon={isAdded ? Tick01Icon : Add01Icon} 
              size={16} 
              className="mr-2" 
            />
            {isAdded ? "Added!" : "Add to Dashboard"}
          </Button>
        )}
      </CardHeader>
      <CardContent>
        <ChartContainer config={chartConfig} className="h-[300px] w-full">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data}>
              <CartesianGrid vertical={false} className="stroke-neutral-600" />
              <XAxis
                dataKey="date"
                tickLine={false}
                axisLine={false}
                tickMargin={8}
                className="fill-neutral-400"
                tickFormatter={(value) => new Date(value).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
              />
              <YAxis 
                tickLine={false}
                axisLine={false}
                tickMargin={8}
                className="fill-neutral-400"
              />
              <ChartTooltip
                cursor={false}
                content={<ChartTooltipContent />}
              />
              <Line
                dataKey="desktop"
                type="monotone"
                stroke="#3b82f6"
                strokeWidth={2}
                dot={{ fill: "#3b82f6", strokeWidth: 2, r: 4 }}
                activeDot={{ r: 6 }}
              />
              <Line
                dataKey="mobile"
                type="monotone"
                stroke="#10b981"
                strokeWidth={2}
                dot={{ fill: "#10b981", strokeWidth: 2, r: 4 }}
                activeDot={{ r: 6 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </ChartContainer>
      </CardContent>
    </Card>
  );
};
