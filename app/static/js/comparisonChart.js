// static/js/comparisonChart.js
import { chartTheme } from "./charts/theme.js";

const strategyAConfig = {
  weights: { NVDA: 0.5, AAPL: 0.5 },
  start_date: "2020-01-01",
  initial_investment: 1000,
};

const strategyBConfig = {
  weights: { TSLA: 0.6, AAPL: 0.4 },
  start_date: "2020-01-01",
  initial_investment: 1000,
};

async function fetchPortfolioData(config) {
  const tsRes = await fetch("/api/timeseries", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(config),
  });
  const tsData = await tsRes.json();

  const summaryRes = await fetch("/api/portfolio-summary", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(config),
  });
  const summaryData = await summaryRes.json();

  return { tsData, summaryData };
}

function normalizeRadarData(summary) {
  const maxDrawdown = Math.abs(summary.maxDrawdown / 100);
  const volatility = summary.volatility;
  const cagr = summary.cagr / 100;
  const riskReward = cagr / (maxDrawdown || 0.01); 

  return [
    riskReward / 5,
    maxDrawdown / 0.5,
    volatility / 0.5,
    cagr / 0.25
  ];
}

async function loadComparisonCharts() {
  const [strategyA, strategyB] = await Promise.all([
    fetchPortfolioData(strategyAConfig),
    fetchPortfolioData(strategyBConfig),
  ]);

  // === Cumulative Returns Chart ===
  const labels = strategyA.tsData.labels;
  const ctxCumulative = document.getElementById("cumulativeComparisonChart").getContext("2d");

  new Chart(ctxCumulative, {
    type: "line",
    data: {
      labels,
      datasets: [
        {
          label: "Strategy A",
          data: strategyA.tsData.strategy,
          borderColor: "#3b82f6",
          backgroundColor: "rgba(59, 130, 246, 0.08)",
          fill: true,
          tension: 0.35,
          pointRadius: 0,
        },
        {
          label: "Strategy B",
          data: strategyB.tsData.strategy,
          borderColor: "#ec4899",
          backgroundColor: "rgba(236, 72, 153, 0.08)",
          fill: true,
          tension: 0.35,
          pointRadius: 0,
        },
        {
          label: "SPY Benchmark",
          data: strategyA.tsData.benchmark,
          borderColor: "#facc15",
          backgroundColor: "rgba(250, 204, 21, 0.08)",
          fill: true,
          tension: 0.35,
          pointRadius: 0,
        },
      ],
    },
    options: chartTheme,
  });

  // === Radar Performance Chart ===
  const ctxRadar = document.getElementById("radarComparisonChart").getContext("2d");

  new Chart(ctxRadar, {
    type: "radar",
    data: {
      labels: ["Risk/Reward", "Max Drawdown", "Volatility", "CAGR"],
      datasets: [
        {
          label: "Strategy A",
          data: normalizeRadarData(strategyA.summaryData),
          backgroundColor: "rgba(59, 130, 246, 0.2)",
          borderColor: "#3b82f6",
        },
        {
          label: "Strategy B",
          data: normalizeRadarData(strategyB.summaryData),
          backgroundColor: "rgba(236, 72, 153, 0.2)",
          borderColor: "#ec4899",
        },
      ],
    },
    options: {
      ...chartTheme,
      scales: {
        r: {
          ticks: { color: "#d1d5db", beginAtZero: true, max: 1 },
          grid: { color: "rgba(255,255,255,0.1)" },
          pointLabels: { color: "#d1d5db" },
        },
      },
    },
  });

  // === Risk vs Return Scatter ===
  const ctxScatter = document.getElementById("riskReturnScatterChart").getContext("2d");

  new Chart(ctxScatter, {
    type: "scatter",
    data: {
      datasets: [
        {
          label: "Strategy A",
          data: [{
            x: strategyA.summaryData.volatility,
            y: strategyA.summaryData.cagr / 100,
          }],
          backgroundColor: "#3b82f6",
        },
        {
          label: "Strategy B",
          data: [{
            x: strategyB.summaryData.volatility,
            y: strategyB.summaryData.cagr / 100,
          }],
          backgroundColor: "#ec4899",
        },
      ],
    },
    options: {
      ...chartTheme,
      scales: {
        x: {
          title: { display: true, text: "Volatility (Risk)", color: "#d1d5db" },
          ticks: { color: "#d1d5db" },
          grid: { color: "rgba(255,255,255,0.1)" },
        },
        y: {
          title: { display: true, text: "CAGR (Return)", color: "#d1d5db" },
          ticks: { color: "#d1d5db" },
          grid: { color: "rgba(255,255,255,0.1)" },
        },
      },
    },
  });
}


loadComparisonCharts().catch((err) => {
  console.error("Failed to load comparison charts:", err);
});