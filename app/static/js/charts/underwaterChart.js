import { chartTheme } from "./theme.js";

const csrfToken = document.querySelector('meta[name="csrf-token"]').content;

export function renderUnderwaterChart(weights, start_date, initial_investment) {
  const chartEl = document.getElementById("underwaterChart");
  if (!chartEl) return;

  fetch("/api/portfolio-drawdown", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrfToken,
    },
    body: JSON.stringify({ weights, start_date, initial_investment }),
  })
    .then((res) => res.json())
    .then(({ labels, values }) => {
      const ctx = chartEl.getContext("2d");

      new Chart(ctx, {
        type: "line",
        data: {
          labels,
          datasets: [
            {
              label: "Drawdown",
              data: values.map((v) => v * 100),
              borderColor: "#f87171",
              backgroundColor: "rgba(248,113,113,0.15)",
              fill: true,
              pointRadius: 0,
              tension: 0.3,
            },
          ],
        },
        options: {
          ...chartTheme,
          plugins: {
            ...chartTheme.plugins,
            tooltip: {
              ...chartTheme.plugins.tooltip,
              callbacks: {
                label: (ctx) => `Drawdown: ${ctx.raw.toFixed(2)}%`,
              },
            },
          },
          scales: {
            x: chartTheme.scales.x,
            y: {
              ...chartTheme.scales.y,
              ticks: {
                color: "#ccc",
                callback: (val) => `${val}%`,
              },
            },
          },
        },
      });
    })
    .catch((err) => {
      console.error("Failed to render drawdown chart:", err);
    });
}
