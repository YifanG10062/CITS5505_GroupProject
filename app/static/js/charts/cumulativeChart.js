// static/js/charts/cumulativeChart.js

export function renderCumulativeChart(weights, start_date, initial_investment) {
  const chartEl = document.getElementById("cumulativeChart");
  if (!chartEl) return;

  fetch("/api/timeseries", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ weights, start_date, initial_investment }),
  })
    .then((res) => res.json())
    .then(({ labels, strategy, benchmark }) => {
      const ctx = chartEl.getContext("2d");

      new Chart(ctx, {
        type: "line",
        data: {
          labels,
          datasets: [
            {
              label: "Your Strategy",
              data: strategy,
              borderColor: "#42A5F5",
              backgroundColor: "rgba(66, 165, 245, 0.1)",
              fill: true,
              tension: 0.3,
              pointRadius: 0,
            },
            {
              label: "SPY Benchmark",
              data: benchmark,
              borderColor: "#FFA726",
              backgroundColor: "rgba(255, 167, 38, 0.1)",
              fill: true,
              tension: 0.3,
              pointRadius: 0,
            },
          ],
        },
        options: {
          responsive: true,
          interaction: { mode: "index", intersect: false },
          plugins: {
            legend: {
              labels: {
                color: "#333",
                font: { size: 12, family: "Arial" },
              },
            },
            tooltip: {
              backgroundColor: "#f9f9f9",
              titleColor: "#333",
              bodyColor: "#444",
              borderColor: "#ccc",
              borderWidth: 1,
            },
          },
          scales: {
            x: { ticks: { color: "#666" }, grid: { display: false } },
            y: { ticks: { color: "#666" }, grid: { borderDash: [3, 3] } },
          },
        },
      });
    })
    .catch((err) => {
      console.error("Failed to render cumulative chart:", err);
    });
}
