export function renderHeatmapChart(weights, start_date, initial_investment) {
  fetch("/api/timeseries", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ weights, start_date, initial_investment }),
  })
    .then((res) => res.json())
    .then((data) => {
      console.log("API Response for Heatmap:", data);
      const monthlyReturns = data.monthlyReturns;
      if (
        !monthlyReturns ||
        !monthlyReturns.labels ||
        !monthlyReturns.datasets
      ) {
        console.warn("No monthly returns data found.");
        return;
      }

      const months = monthlyReturns.labels;
      const years = monthlyReturns.datasets.map((row) => row.year.toString());

      const matrixData = [];
      for (let row of monthlyReturns.datasets) {
        row.values.forEach((val, i) => {
          matrixData.push({ x: months[i], y: row.year.toString(), v: val });
        });
      }

      // Updated green to yellow color scale
      const getShade = (v) => {
        if (v > 0.2) return "#f5c154"; 
        if (v > 0.1) return "#e6aa2e"; 
        if (v > 0.05) return "#d4b832"; 
        if (v > 0.01) return "#7cd7a7"; 
        if (v >= 0) return "#46c389"; 
        if (v > -0.01) return "#2aa27f"; 
        if (v > -0.05) return "#1b7b6c"; 
        if (v > -0.1) return "#0f5249"; 
        return "#083c35"; 
      };

      const ctx = document.getElementById("heatmapChart").getContext("2d");

      new Chart(ctx, {
        type: "matrix",
        data: {
          labels: { x: months, y: years },
          datasets: [
            {
              label: "Monthly Return",
              data: matrixData,
              backgroundColor: (ctx) => getShade(ctx.raw.v),
              borderWidth: 0,
              width: () => 22,
              height: () => 22,
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { display: false },
            title: { display: false },
            tooltip: {
              backgroundColor: "#1f1f1f",
              titleColor: "#FFD700",
              titleFont: { family: "Sora", weight: "600" },
              bodyColor: "#f3f4f6",
              bodyFont: { family: "Sora", weight: "500" },
              borderColor: "#E69622",
              borderWidth: 1.2,
              padding: 10,
              callbacks: {
                label: (ctx) => {
                  const { x, y, v } = ctx.raw;
                  return `${y} ${x}: ${(v * 100).toFixed(2)}%`;
                },
              },
            },
          },
          scales: {
            x: {
              type: "category",
              labels: months,
              offset: true,
              grid: { display: false },
              ticks: {
                color: "#d1d5db",
                font: { family: "Sora", size: 12 },
              },
            },
            y: {
              type: "category",
              labels: years,
              offset: true,
              grid: { display: false },
              reverse: true,
              ticks: {
                color: "#d1d5db",
                font: { family: "Sora", size: 12 },
              },
            },
          },
        },
      });

      const legendContainer = document.getElementById("heatmapLegend");
      if (legendContainer) {
        legendContainer.innerHTML = `
        <div style="display: flex; justify-content: center; align-items: center; gap: 1px; font-family: Sora; font-size: 10px; margin-top: 6px;">
          <div style="display: flex; gap: 1px;">
            <div style="width: 14px; height: 8px; background-color: #083c35;"></div>
            <div style="width: 14px; height: 8px; background-color: #0f5249;"></div>
            <div style="width: 14px; height: 8px; background-color: #1b7b6c;"></div>
            <div style="width: 14px; height: 8px; background-color: #2aa27f;"></div>
            <div style="width: 14px; height: 8px; background-color: #46c389;"></div>
            <div style="width: 14px; height: 8px; background-color: #7cd7a7;"></div>
            <div style="width: 14px; height: 8px; background-color: #d4b832;"></div>
            <div style="width: 14px; height: 8px; background-color: #e6aa2e;"></div>
            <div style="width: 14px; height: 8px; background-color: #f5c154;"></div>
          </div>
        </div>
      `;
      }
    })
    .catch((err) => {
      console.error("Failed to render monthly heatmap:", err);
    });
}
