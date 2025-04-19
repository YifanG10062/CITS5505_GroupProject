// Renders the Cumulative Return vs SPY chart
function renderCumulativeChart() {
  const chartEl = document.getElementById("cumulativeChart");
  if (!chartEl) return; // Avoid error if the element doesn't exist

  fetch("/api/timeseries", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      weights: { "MSFT": 0.6, "TSLA": 0.4 },
      start_date: "2020-01-01",
      initial_investment: 10000
    })
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
              label: "Strategy",
              data: strategy,
              borderColor: "#4fd1c5",
              fill: false,
              tension: 0.4,
            },
            {
              label: "SPY Benchmark",
              data: benchmark,
              borderColor: "#f6ad55",
              fill: false,
              tension: 0.4,
            },
          ],
        },
        options: {
          responsive: true,
          plugins: {
            legend: { labels: { color: "#ffffff" } },
          },
          scales: {
            x: { ticks: { color: "#aaa" } },
            y: { ticks: { color: "#aaa" } },
          },
        },
      });
    })
    .catch((err) => {
      console.error("Failed to load cumulative chart:", err);
    });
}

// TODO: later move to initDashboard() when all charts are integrated
renderCumulativeChart();
