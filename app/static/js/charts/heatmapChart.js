// static/js/charts/heatmapChart.js
import { chartTheme } from "./theme.js";

export function renderHeatmapChart(weights, start_date, initial_investment) {
  fetch("/api/timeseries", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ weights, start_date, initial_investment }),
  })
    .then((res) => res.json())
    .then((data) => {
      console.log("/api/timeseries returned:", data);

      const monthlyReturns = data.monthlyReturns;
      if (
        !monthlyReturns ||
        !monthlyReturns.labels ||
        !monthlyReturns.datasets
      ) {
        console.warn("No monthly returns data found.");
        return;
      }

      const ctx = document.getElementById("heatmapChart").getContext("2d");

      const labels = monthlyReturns.labels;
      const datasets = monthlyReturns.datasets.map((yearRow) => ({
        label: yearRow.year.toString(),
        data: yearRow.values,
        backgroundColor: yearRow.values.map((v) =>
          v >= 0
            ? `rgba(0, 200, 150, ${0.2 + v * 2})`
            : `rgba(255, 99, 132, ${0.2 + Math.abs(v) * 2})`
        ),
        borderWidth: 1,
      }));

      new Chart(ctx, {
        type: "bar",
        data: {
          labels: labels,
          datasets: datasets,
        },
        options: {
          ...chartTheme,
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            ...chartTheme.plugins,
            title: {
              display: true,
              text: "Monthly Returns Heatmap",
              color: "#ffffff",
              font: {
                size: 16,
                weight: "bold",
                family: "Poppins",
              },
            },
          },
          scales: {
            x: {
              stacked: true,
              ticks: { color: "#ccc" },
            },
            y: {
              stacked: true,
              ticks: {
                color: "#ccc",
                callback: (val) => `${(val * 100).toFixed(0)}%`,
              },
            },
          },
        },
      });
    })
    .catch((err) =>
      console.error("Failed to render monthly returns heatmap:", err)
    );
}
