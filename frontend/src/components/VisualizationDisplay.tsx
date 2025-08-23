"use client";

import TableComponent from "./TableComponent";
import ChartComponent from "./ChartComponent";

export default function VisualizationDisplay({ components }: any) {
  console.log("VisualizationDisplay received components:", components);
  
  if (!components) {
    console.log("No components received, returning null");
    return null;
  }

  // Now components should be an object with table_data and charts properties
  const tableData = components.table_data || [];
  const chartsConfig = components.charts || [];

  console.log("Extracted tableData:", tableData);
  console.log("Extracted chartsConfig:", chartsConfig);
  console.log("About to render charts. chartsConfig.length:", chartsConfig.length);
  console.log("About to render table. tableData.length:", tableData.length);

  return (
    <div className="w-full space-y-4">
      {chartsConfig.length > 0 && chartsConfig.map((chart: any, index: number) => {
        console.log(`Processing chart ${index}:`, chart);
        console.log("Chart type:", chart.type);
        console.log("Chart x_axis:", chart.x_axis);
        console.log("Chart y_axis:", chart.y_axis);
        console.log("tableData.length:", tableData.length);
        
        if (chart.type === "line" && tableData.length > 0 && chart.x_axis && chart.y_axis) {
          console.log("Chart condition met, processing...");
          
          const xAxisName = chart.x_axis;
          const yAxisName = chart.y_axis[0].name;
          
          console.log("X-Axis Name:", xAxisName);
          console.log("Y-Axis Name:", yAxisName);
          console.log("Table Data:", tableData);
          
          const chartData = tableData.map((row: any) => {
            const newObject = {
              [xAxisName]: row[xAxisName],
              [yAxisName]: row[yAxisName]
            };
            return newObject;
          });
          
          console.log("Chart Data Created:", chartData);

          return (
            <ChartComponent
              key={`chart-${index}`}
              title={`Revenue by Year`}
              data={chartData}
              xAxisKey={chart.x_axis}
              yAxisConfig={chart.y_axis}
              showAddButton={true}
            />
          );
        } else {
          console.log("Chart condition NOT met");
        }
        return null;
      })}
      
      {tableData.length > 0 && (
        <TableComponent 
          title="Query Results"
          data={tableData}
          showAddButton={true}
        />
      )}
    </div>
  );
}
