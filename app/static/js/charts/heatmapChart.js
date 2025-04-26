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

      //shades of green for heatmap levels
      const getGreenShade = (v) => {
        if (v >= 0.2) return "#166534";
        if (v >= 0.1) return "#22c55e";
        if (v >= 0.05) return "#4ade80";
        if (v > 0.01) return "#86efac";
        if (v > 0) return "#d1fae5";
        return "#1f2937";
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
              backgroundColor: (ctx) => getGreenShade(ctx.raw.v),
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
              backgroundColor: "#111827",
              titleColor: "#f8fafc",
              bodyColor: "#e5e7eb",
              borderColor: "#374151",
              borderWidth: 1,
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
                font: { family: "Poppins", size: 10 },
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
                font: { family: "Poppins", size: 10 },
              },
            },
          },
        },
      });

      const legendContainer = document.getElementById("heatmapLegend");
      if (legendContainer) {
        legendContainer.innerHTML = `
          <div style="display: flex; justify-content: center; gap: 10px; font-family: Poppins; font-size: 11px; margin-top: 6px;">
            <span style="color: #1f2937;">■ 0%</span>
            <span style="color: #d1fae5;">■ > 0%</span>
            <span style="color: #86efac;">■ > 1%</span>
            <span style="color: #4ade80;">■ > 5%</span>
            <span style="color: #22c55e;">■ > 10%</span>
            <span style="color: #166534;">■ > 20%</span>
          </div>
        `;
      }
    })
    .catch((err) => {
      console.error("Failed to render monthly heatmap:", err);
    });
}
