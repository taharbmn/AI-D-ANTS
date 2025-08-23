```json
{
  "components": [
    {
      "type": "chart",
      "title": "Active Users",
      "data": [
  { date: "2024-04-01", desktop: 222, mobile: 150 },
  { date: "2024-04-02", desktop: 97, mobile: 180 },
  { date: "2024-04-03", desktop: 167, mobile: 120 },
  { date: "2024-04-04", desktop: 242, mobile: 260 }
  ],
      "labels": [
        {
          "name": "Users",
          "color": "Red"
        }
      ]
    },
    {
      "type": "table",
      "title": "Active Users",
      "data": [
  { date: "2024-04-01", desktop: 222, mobile: 150 },
  { date: "2024-04-02", desktop: 97, mobile: 180 },
  { date: "2024-04-03", desktop: 167, mobile: 120 },
  { date: "2024-04-04", desktop: 242, mobile: 260 }
  ],
    }
  ]@*
}
```
"chart": [{

"type": "line",
"x_axis": "date",
"y_axis": [
    {
        "name": "desktop",
        "color": "#hfazre"
    }
]}]