"use client";

import { useState } from 'react';
import { CartesianGrid, Line, LineChart, XAxis, YAxis, ResponsiveContainer } from "recharts";
import { ChartContainer, ChartTooltip, ChartTooltipContent } from "@/components/ui/chart";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { 
  DropdownMenu, 
  DropdownMenuContent, 
  DropdownMenuItem, 
  DropdownMenuTrigger 
} from "@/components/ui/dropdown-menu";
import { ArrowDown01Icon, BarChartIcon, DatabaseIcon } from '@hugeicons/core-free-icons';
import { HugeiconsIcon } from '@hugeicons/react';

interface ChartData {
  [key: string]: any;
}

interface VisualizationComponent {
  type: "chart" | "table";
  title: string;
  data: ChartData[];
  labels?: {
    name: string;
    color: string;
  }[];
}

interface VisualizationDisplayProps {
  components: VisualizationComponent[];
}

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

const DownloadButton = ({ type, title }: { type: "chart" | "table"; title: string }) => {
  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button 
          variant="outline" 
          size="sm"
          className="bg-neutral-700 border-neutral-600 text-white hover:bg-neutral-600"
        >
          <HugeiconsIcon icon={ArrowDown01Icon} size={16} className="mr-2" />
          Download
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent 
        align="end" 
        className="bg-neutral-800 border-neutral-600"
      >
        {type === "chart" ? (
          <>
            <DropdownMenuItem className="text-white hover:bg-neutral-700">
              Download as PNG
            </DropdownMenuItem>
            <DropdownMenuItem className="text-white hover:bg-neutral-700">
              Download as SVG
            </DropdownMenuItem>
            <DropdownMenuItem className="text-white hover:bg-neutral-700">
              Download as PDF
            </DropdownMenuItem>
          </>
        ) : (
          <>
            <DropdownMenuItem className="text-white hover:bg-neutral-700">
              Download as CSV
            </DropdownMenuItem>
            <DropdownMenuItem className="text-white hover:bg-neutral-700">
              Download as Excel
            </DropdownMenuItem>
            <DropdownMenuItem className="text-white hover:bg-neutral-700">
              Download as JSON
            </DropdownMenuItem>
          </>
        )}
      </DropdownMenuContent>
    </DropdownMenu>
  );
};

const ChartComponent = ({ component }: { component: VisualizationComponent }) => {
  return (
    <Card className="bg-neutral-700 border-neutral-600">
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4">
        <div className="flex items-center gap-2">
          <HugeiconsIcon icon={BarChartIcon} size={20} className="text-blue-400" />
          <CardTitle className="text-white text-lg">{component.title}</CardTitle>
        </div>
        <DownloadButton type="chart" title={component.title} />
      </CardHeader>
      <CardContent>
        <ChartContainer config={chartConfig} className="h-[300px] w-full">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={component.data}>
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

const TableComponent = ({ component }: { component: VisualizationComponent }) => {
  const columns = component.data?.length > 0 ? Object.keys(component?.data[0]) : [];
  
  return (
    <Card className="bg-neutral-700 border-neutral-600">
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4">
        <div className="flex items-center gap-2">
          <HugeiconsIcon icon={DatabaseIcon} size={20} className="text-green-400" />
          <CardTitle className="text-white text-lg">{component.title}</CardTitle>
        </div>
        <DownloadButton type="table" title={component.title} />
      </CardHeader>
      <CardContent>
        <div className="overflow-hidden rounded-lg border border-neutral-600 bg-neutral-800">
          <Table>
            <TableHeader>
              <TableRow className="hover:bg-neutral-700 border-neutral-600">
                {columns.map((column) => (
                  <TableHead key={column} className="text-white px-6 py-4 capitalize">
                    {column}
                  </TableHead>
                ))}
              </TableRow>
            </TableHeader>
            <TableBody>
              {component.data?.map((row, index) => (
                <TableRow
                  key={index}
                  className="hover:bg-neutral-700 border-neutral-600"
                >
                  {columns.map((column) => (
                    <TableCell key={column} className="px-6 py-4 text-white">
                      {row[column]}
                    </TableCell>
                  ))}
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>
  );
};

export default function VisualizationDisplay({ components }: VisualizationDisplayProps) {
  if (!components || components.length === 0) {
    return null;
  }

  return (
    <div className="max-w-[70%] space-y-4">
      {components.map((component, index) => (
        <div key={index}>
          {component.type === "chart" ? (
            <ChartComponent component={component} />
          ) : (
            <TableComponent component={component} />
          )}
        </div>
      ))}
    </div>
  );
}
