"use client";

import * as React from "react";

interface DataTableProps {
  data: any[];
}

export default function DataTable({ data }: DataTableProps) {
  const [currentPage, setCurrentPage] = React.useState(0);
  const [sortColumn, setSortColumn] = React.useState<string | null>(null);
  const [sortDirection, setSortDirection] = React.useState<'asc' | 'desc'>('asc');
  const [filterValue, setFilterValue] = React.useState('');
  
  const itemsPerPage = 10;

  if (!data || data.length === 0) {
    return (
      <div className="flex items-center justify-center h-24 text-gray-500 border border-white/10 rounded-md bg-neutral-800/50">
        No data available
      </div>
    );
  }

  // Get column names from the first row
  const columns = Object.keys(data[0]);

  // Handle sorting
  const handleSort = (column: string) => {
    if (sortColumn === column) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortColumn(column);
      setSortDirection('asc');
    }
    setCurrentPage(0);
  };

  // Sort data
  const sortedData = React.useMemo(() => {
    if (!sortColumn) return data;
    
    return [...data].sort((a, b) => {
      const aVal = a[sortColumn];
      const bVal = b[sortColumn];
      
      if (typeof aVal === 'number' && typeof bVal === 'number') {
        return sortDirection === 'asc' ? aVal - bVal : bVal - aVal;
      }
      
      const aStr = String(aVal).toLowerCase();
      const bStr = String(bVal).toLowerCase();
      
      if (sortDirection === 'asc') {
        return aStr.localeCompare(bStr);
      } else {
        return bStr.localeCompare(aStr);
      }
    });
  }, [data, sortColumn, sortDirection]);

  // Filter data
  const filteredData = React.useMemo(() => {
    if (!filterValue.trim()) return sortedData;
    
    return sortedData.filter(row =>
      Object.values(row).some(value =>
        String(value).toLowerCase().includes(filterValue.toLowerCase())
      )
    );
  }, [sortedData, filterValue]);

  // Paginate data
  const totalPages = Math.ceil(filteredData.length / itemsPerPage);
  const paginatedData = filteredData.slice(
    currentPage * itemsPerPage,
    (currentPage + 1) * itemsPerPage
  );

  const formatValue = (value: any) => {
    if (typeof value === 'number') {
      return new Intl.NumberFormat("en-US", {
        minimumFractionDigits: 0,
        maximumFractionDigits: 2,
      }).format(value);
    }
    return String(value);
  };

  return (
    <div className="w-full space-y-4">
      {/* Filter Input */}
      <div className="flex items-center gap-4">
        <input
          type="text"
          placeholder="Filter data..."
          value={filterValue}
          onChange={(e) => {
            setFilterValue(e.target.value);
            setCurrentPage(0);
          }}
          className="px-3 py-2 bg-neutral-800 border border-white/10 rounded-md text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <span className="text-sm text-gray-400">
          {filteredData.length} row{filteredData.length !== 1 ? 's' : ''} total
        </span>
      </div>

      {/* Table */}
      <div className="overflow-hidden rounded-md border border-white/10 bg-neutral-800/50">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-white/10 bg-neutral-700/50">
                {columns.map((column) => (
                  <th
                    key={column}
                    className="px-4 py-3 text-left text-sm font-medium text-gray-300 cursor-pointer hover:bg-neutral-600/50 transition-colors"
                    onClick={() => handleSort(column)}
                  >
                    <div className="flex items-center gap-2">
                      <span>{column.replace(/_/g, ' ').toUpperCase()}</span>
                      {sortColumn === column && (
                        <span className="text-blue-400">
                          {sortDirection === 'asc' ? '↑' : '↓'}
                        </span>
                      )}
                    </div>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {paginatedData.map((row, index) => (
                <tr
                  key={index}
                  className="border-b border-white/5 hover:bg-neutral-700/30 transition-colors"
                >
                  {columns.map((column) => (
                    <td key={column} className="px-4 py-3 text-sm text-gray-300">
                      <div className={typeof row[column] === 'number' ? 'text-right font-medium' : ''}>
                        {formatValue(row[column])}
                      </div>
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between">
          <span className="text-sm text-gray-400">
            Page {currentPage + 1} of {totalPages}
          </span>
          <div className="flex gap-2">
            <button
              onClick={() => setCurrentPage(Math.max(0, currentPage - 1))}
              disabled={currentPage === 0}
              className="px-3 py-1 bg-neutral-700 hover:bg-neutral-600 disabled:opacity-50 disabled:cursor-not-allowed rounded text-sm text-white transition-colors"
            >
              Previous
            </button>
            <button
              onClick={() => setCurrentPage(Math.min(totalPages - 1, currentPage + 1))}
              disabled={currentPage === totalPages - 1}
              className="px-3 py-1 bg-neutral-700 hover:bg-neutral-600 disabled:opacity-50 disabled:cursor-not-allowed rounded text-sm text-white transition-colors"
            >
              Next
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
