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
  xAxisKey?: string;
  yAxisConfig?: Array<{ name: string; color: string }>;
}

export default function ChartComponent({ 
  title, 
  data, 
  labels, 
  showAddButton = false,
  xAxisKey = "date",
  yAxisConfig = []
}: ChartComponentProps) {
  const { addToDashboard } = useDashboardContext();
  const [isAdded, setIsAdded] = useState(false);

  const handleAddToDashboard = () => {
    if (addToDashboard) {
      addToDashboard({
        type: "chart",
        title,
        data,
        labels,
        xAxisKey,
        yAxisConfig
      });
      setIsAdded(true);
      // Reset the state after 2 seconds
      setTimeout(() => setIsAdded(false), 2000);
    }
  };

  return (
    <Card className="bg-neutral-700 border-neutral-600">
      {showAddButton && (
        <div className="flex justify-end p-4 pb-0">
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
        </div>
      )}
      <CardContent className={showAddButton ? "" : "pt-6"}>
        <ChartContainer config={chartConfig} className="h-[300px] w-full">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data}>
              <CartesianGrid vertical={false} className="stroke-neutral-600" />
              <XAxis
                dataKey={xAxisKey}
                tickLine={false}
                axisLine={false}
                tickMargin={8}
                className="fill-neutral-400"
                tickFormatter={(value) => {
                  // Handle different data types for x-axis
                  if (xAxisKey === "date" || (typeof value === "string" && value.includes("-"))) {
                    return new Date(value).toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
                  }
                  return value;
                }}
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
              {yAxisConfig.length > 0 ? (
                // Render lines based on yAxisConfig
                yAxisConfig.map((axis, index) => (
                  <Line
                    key={axis.name}
                    dataKey={axis.name}
                    type="monotone"
                    stroke={axis.color}
                    strokeWidth={2}
                    dot={{ fill: axis.color, strokeWidth: 2, r: 4 }}
                    activeDot={{ r: 6 }}
                  />
                ))
              ) : (
                // Fallback to default lines if no yAxisConfig
                <>
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
                </>
              )}
            </LineChart>
          </ResponsiveContainer>
        </ChartContainer>
      </CardContent>
    </Card>
  );
};
