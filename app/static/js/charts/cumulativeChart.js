import { chartTheme } from "./theme.js";

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
              borderColor: "#10b981", // Tailwind emerald-500
              backgroundColor: "rgba(16, 185, 129, 0.08)",
              fill: true,
              tension: 0.35,
              pointRadius: 0,
            },
            {
              label: "SPY Benchmark",
              data: benchmark,
              borderColor: "#facc15", // Tailwind yellow-400
              backgroundColor: "rgba(250, 204, 21, 0.1)",
              fill: true,
              tension: 0.35,
              pointRadius: 0,
            },
          ],
        },
        options: chartTheme,
      });
    })
    .catch((err) => {
      console.error("Failed to render cumulative chart:", err);
    });
}
