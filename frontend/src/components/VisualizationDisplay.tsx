"use client";

import TableComponent from "./TableComponent";

export default function VisualizationDisplay({ components }: any) {
  if (!components || components.length === 0) {
    return null;
  }

  return (
    <div className="w-full space-y-4">
      <TableComponent 
        title="Query Results"
        data={components}
        showAddButton={true}
      />
    </div>
  );
}
