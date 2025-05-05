// static/js/comparisonChart.js

// This function renders the dynamic comparison chart using Chart.js
function renderComparisonChart(weightsA, weightsB, startDate, initialInvestment) {
  const chartEl = document.getElementById("comparisonChart");
  if (!chartEl) return;

  fetch("/api/comparison_timeseries", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      weights_a: weightsA,
      weights_b: weightsB,
      start_date: startDate,
      initial_investment: initialInvestment,
    }),
  })
    .then((res) => res.json())
    .then(({ labels, portfolio_a, portfolio_b }) => {
      const ctx = chartEl.getContext("2d");

      new Chart(ctx, {
        type: "line",
        data: {
          labels,
          datasets: [
            {
              label: "Portfolio A",
              data: portfolio_a,
              borderColor: "#4e79a7",
              backgroundColor: "rgba(78, 121, 167, 0.1)",
              fill: true,
              tension: 0.35,
              pointRadius: 0,
            },
            {
              label: "Portfolio B",
              data: portfolio_b,
              borderColor: "#f28e2b",
              backgroundColor: "rgba(242, 142, 43, 0.1)",
              fill: true,
              tension: 0.35,
              pointRadius: 0,
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { position: "top" },
            tooltip: { mode: "index", intersect: false },
          },
          interaction: {
            mode: "index",
            intersect: false,
          },
          scales: {
            y: {
              title: {
                display: true,
                text: "Cumulative Return",
              },
              beginAtZero: true,
            },
            x: {
              title: {
                display: true,
                text: "Year",
              },
            },
          },
        },
      });
    })
    .catch((err) => {
      console.error("Failed to render comparison chart:", err);
    });
}

// Automatically run on DOM load
document.addEventListener("DOMContentLoaded", () => {
  // These global variables must be injected in HTML template
  renderComparisonChart(allocationDataA, allocationDataB, "2015-01-01", 1000);
});
