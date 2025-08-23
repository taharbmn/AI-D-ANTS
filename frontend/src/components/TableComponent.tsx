"use client";

import { useState, useMemo } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { 
  DatabaseIcon, 
  Add01Icon, 
  Tick01Icon, 
  Search01Icon,
  ArrowLeft02Icon,
  ArrowRight02Icon,
  Settings02Icon,
  ArrowDown01Icon,
  Tick02Icon
} from '@hugeicons/core-free-icons';
import { HugeiconsIcon } from '@hugeicons/react';
import { useDashboardContext } from "@/contexts/DashboardContext";

interface TableComponentProps {
  title: string;
  data: any[];
  showAddButton?: boolean;
}

export default function TableComponent({ 
  title, 
  data, 
  showAddButton = false 
}: TableComponentProps) {
  const { addToDashboard } = useDashboardContext();
  const [isAdded, setIsAdded] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage] = useState(10);
  const [visibleColumns, setVisibleColumns] = useState<Record<string, boolean>>({});
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  
  const allColumns = useMemo(() => {
    return data?.length > 0 ? 
      Array.from(new Set(data.flatMap(item => Object.keys(item)))) : [];
  }, [data]);

  useState(() => {
    if (allColumns.length > 0 && Object.keys(visibleColumns).length === 0) {
      const initialVisible: Record<string, boolean> = {};
      allColumns.forEach((col, index) => {
        initialVisible[col] = index < 4;
      });
      setVisibleColumns(initialVisible);
    }
  });

  const displayColumns = allColumns.filter(col => visibleColumns[col]);

  const handleAddToDashboard = () => {
    if (addToDashboard) {
      addToDashboard({
        type: "table",
        title,
        data
      });
      setIsAdded(true);
      setTimeout(() => setIsAdded(false), 2000);
    }
  };

  const getCellValue = (row: any, column: string) => {
    const value = row[column];
    if (value === null || value === undefined) {
      return '-';
    }
    if (typeof value === 'object') {
      return JSON.stringify(value);
    }
    return String(value);
  };

  const formatColumnHeader = (column: string) => {
    return column
      .replace(/_/g, ' ')
      .replace(/\b\w/g, char => char.toUpperCase())
      .trim();
  };

  const filteredData = useMemo(() => {
    if (!searchTerm) return data;
    
    return data.filter(row => {
      return allColumns.some(column => {
        const cellValue = getCellValue(row, column).toLowerCase();
        return cellValue.includes(searchTerm.toLowerCase());
      });
    });
  }, [data, searchTerm, allColumns]);

  const totalPages = Math.ceil(filteredData.length / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage;
  const paginatedData = filteredData.slice(startIndex, startIndex + itemsPerPage);

  const goToNextPage = () => {
    if (currentPage < totalPages) {
      setCurrentPage(currentPage + 1);
    }
  };

  const goToPrevPage = () => {
    if (currentPage > 1) {
      setCurrentPage(currentPage - 1);
    }
  };

  const toggleColumnVisibility = (column: string) => {
    setVisibleColumns(prev => ({
      ...prev,
      [column]: !prev[column]
    }));
  };

  return (
    <Card className="bg-neutral-700 border-neutral-600">
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4">
        <div className="flex items-center gap-2">
          <HugeiconsIcon icon={DatabaseIcon} size={20} className="text-green-400" />
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
                : "bg-green-600 border-green-500 text-white hover:bg-green-700"
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
        <div className="flex flex-col md:flex-row gap-4 mb-4">
          <div className="relative flex-1">
            <HugeiconsIcon 
              icon={Search01Icon} 
              size={16} 
              className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" 
            />
            <Input
              placeholder="Search in all columns..."
              value={searchTerm}
              onChange={(e) => {
                setSearchTerm(e.target.value);
                setCurrentPage(1);
              }}
              className="pl-10 bg-neutral-800 border-neutral-600 text-white placeholder-gray-400"
            />
          </div>
          
          <div className="relative">
            <Button
              variant="outline"
              onClick={() => setIsDropdownOpen(!isDropdownOpen)}
              className="bg-neutral-800 border-neutral-600 text-white hover:bg-neutral-700"
            >
              <HugeiconsIcon icon={Settings02Icon} size={16} className="mr-2" />
              Columns ({displayColumns.length}/{allColumns.length})
              <HugeiconsIcon 
                icon={ArrowDown01Icon} 
                size={16} 
                className={`ml-2 transition-transform ${isDropdownOpen ? 'rotate-180' : ''}`} 
              />
            </Button>
            
            {isDropdownOpen && (
              <>
                <div 
                  className="fixed inset-0 z-10" 
                  onClick={() => setIsDropdownOpen(false)}
                />
                
                <div className="absolute right-0 top-full mt-2 z-20 w-64 bg-neutral-800 border border-neutral-600 rounded-lg shadow-lg">
                  <div className="p-3 border-b border-neutral-600">
                    <h3 className="text-sm font-medium text-gray-300">Toggle Columns</h3>
                  </div>
                  
                  <div className="max-h-64 overflow-y-auto">
                    {allColumns.map((column) => (
                      <div
                        key={column}
                        className="flex items-center gap-3 px-3 py-2 hover:bg-neutral-700 cursor-pointer transition-colors"
                        onClick={() => toggleColumnVisibility(column)}
                      >
                        <div className="flex items-center justify-center w-4 h-4">
                          {visibleColumns[column] && (
                            <HugeiconsIcon 
                              icon={Tick02Icon} 
                              size={14} 
                              className="text-blue-500" 
                            />
                          )}
                        </div>
                        <span className="text-sm text-white flex-1">
                          {formatColumnHeader(column)}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              </>
            )}
          </div>
        </div>

        <div className="overflow-x-auto rounded-lg border border-neutral-600 bg-neutral-800 table-scroll">
          <Table>
            <TableHeader>
              <TableRow className="hover:bg-neutral-700 border-neutral-600">
                {displayColumns.map((column) => (
                  <TableHead key={column} className="text-white px-6 py-4 font-semibold whitespace-nowrap">
                    {formatColumnHeader(column)}
                  </TableHead>
                ))}
              </TableRow>
            </TableHeader>
            <TableBody>
              {paginatedData?.map((row: any, index: any) => (
                <TableRow
                  key={index}
                  className="hover:bg-neutral-700 border-neutral-600"
                >
                  {displayColumns.map((column) => (
                    <TableCell key={column} className="px-6 py-4 text-white">
                      <div 
                        className="max-w-xs truncate cursor-pointer" 
                        title={getCellValue(row, column)}
                        onClick={() => {
                          navigator.clipboard.writeText(getCellValue(row, column));
                        }}
                      >
                        {getCellValue(row, column)}
                      </div>
                    </TableCell>
                  ))}
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>

        <div className="flex flex-col md:flex-row items-center justify-between mt-4 gap-4">
          <div className="text-sm text-gray-400">
            Showing {Math.min(startIndex + 1, filteredData.length)} to {Math.min(startIndex + itemsPerPage, filteredData.length)} of {filteredData.length} entries
            {searchTerm && ` (filtered from ${data.length} total entries)`}
          </div>
          
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={goToPrevPage}
              disabled={currentPage === 1}
              className="bg-neutral-800 border-neutral-600 text-white hover:bg-neutral-700 disabled:opacity-50"
            >
              <HugeiconsIcon icon={ArrowLeft02Icon} size={16} className="mr-1" />
              Previous
            </Button>
            
            <span className="px-3 py-1 bg-neutral-800 rounded text-white text-sm">
              Page {currentPage} of {totalPages}
            </span>
            
            <Button
              variant="outline"
              size="sm"
              onClick={goToNextPage}
              disabled={currentPage === totalPages}
              className="bg-neutral-800 border-neutral-600 text-white hover:bg-neutral-700 disabled:opacity-50"
            >
              Next
              <HugeiconsIcon icon={ArrowRight02Icon} size={16} className="ml-1" />
            </Button>
          </div>
        </div>

        {filteredData?.length === 0 && (
          <div className="text-center py-8 text-gray-400">
            {searchTerm ? `No results found for "${searchTerm}"` : "No data available"}
          </div>
        )}
      </CardContent>
    </Card>
  );
};
