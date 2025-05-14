import { chartTheme } from "./theme.js";

/**
 * Render a comparison cumulative returns chart for two portfolios against a benchmark.
 * @param {{weights_a: Object, weights_b: Object, weights_spy: Object, start_date: string, initial_investment: number, nameA: string, nameB: string, benchmarkName?: string, elementId?: string}} config
 */
export function renderComparisonCumulativeChart({
  weights_a,
  weights_b,
  weights_spy = {"SPY": 1.0},
  start_date,
  initial_investment,
  nameA,
  nameB,
  benchmarkName = "SPY Benchmark",
  elementId = "comparisonChart"
}) {

  const chartEl = document.getElementById(elementId);
  console.log(`→ Looking for canvas '#${elementId}':`, chartEl);
  if (!chartEl) return;

  const payload = {
    weights_a,
    weights_b,
    start_date,
    initial_investment
  };
  console.log("→ comparison_timeseries payload:", payload);

  fetch("/api/comparison_timeseries", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  })
    .then(res => {
      console.log("→ comparison_timeseries status:", res.status);
      if (!res.ok) {
        return res.json().then(err => { throw new Error(err.error || `Status ${res.status}`); });
      }
      return res.json();
    })
    .then(data => {
 
      const { labels, portfolio_a, portfolio_b, portfolio_spy } = data;
    
      const ctx = chartEl.getContext("2d");
      new Chart(ctx, {
        type: "line",
        data: {
          labels,
          datasets: [
            {
              label: nameA,
              data: portfolio_a,
              borderColor: "#10b981",
              backgroundColor: "rgba(16, 185, 129, 0.08)",
              fill: true,
              tension: 0.35,
              pointRadius: 0
            },
            {
              label: nameB,
              data: portfolio_b,
              borderColor: "#3b82f6",
              backgroundColor: "rgba(59, 130, 246, 0.08)",
              fill: true,
              tension: 0.35,
              pointRadius: 0
            },
            {
              label: benchmarkName,
              data: portfolio_spy,
              borderColor: "#E69622",
              backgroundColor: "rgba(250, 204, 21, 0.1)",
              fill: true,
              tension: 0.35,
              pointRadius: 0
            }
          ]
        },
        options: chartTheme
      });
    })
    .catch(error => {
      console.error("Error rendering cumulative comparison chart:", error);
    });
}
