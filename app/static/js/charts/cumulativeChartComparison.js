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
  elementId = "cumulativeChartComparison"
}) {

  const chartEl = document.getElementById(elementId);
  console.log(`→ Looking for canvas '#${elementId}':`, chartEl);
  if (!chartEl) return;

  // only decode single quote and double quote
  const decodeSingleQuote = (text) => {
    if (!text) return text;
    return text.replace(/&#39;/g, "'").replace(/&quot;/g, '"');
  };
  
  nameA = decodeSingleQuote(nameA);
  nameB = decodeSingleQuote(nameB);
  benchmarkName = decodeSingleQuote(benchmarkName);

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
              borderColor: "#3b82f6", // portfolio A
              backgroundColor: "rgba(59, 130, 246, 0.1)",
              fill: true,
              tension: 0.35,
              pointRadius: 0
            },
            {
              label: nameB,
              data: portfolio_b,
              borderColor: "#f97316", // portfolio B
              backgroundColor: "rgba(249, 115, 22, 0.1)",
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
