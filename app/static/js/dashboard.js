import { renderCumulativeChart } from "./charts/cumulativeChart.js";
import { renderHeatmapChart } from "./charts/heatmapChart.js";
import { renderPortfolioSummary } from "./charts/summary.js";

document.addEventListener("DOMContentLoaded", () => {
  const weights = window.dashboardData?.weights || { MSFT: 0.6, TSLA: 0.4 };
  const start_date = window.dashboardData?.start_date || "2015-01-01";
  const initial_investment = window.dashboardData?.initial_investment || 10000;

  renderCumulativeChart(weights, start_date, initial_investment);
  renderHeatmapChart(weights, start_date, initial_investment);
  renderPortfolioSummary(weights, start_date, initial_investment);

  // Inject portfolio overview values
  const data = window.dashboardData || {};

  const formatCurrency = (val) => {
    if (val == null) return "$0";
    return `$${Number(val).toLocaleString()}`;
  };

  const formatPercent = (val) => {
    if (val == null) return "0%";
    return `${(Number(val) * 100).toFixed(2)}%`;
  };

  try {
    document.getElementById("netWorth").textContent = formatCurrency(
      data.net_worth
    );
    document.getElementById("initial").textContent = formatCurrency(
      data.initial_investment
    );
    document.getElementById("profit").textContent = formatCurrency(
      (data.net_worth ?? 0) - (data.initial_investment ?? 0)
    );

    document.getElementById("cumulativeReturn").textContent = formatPercent(
      data.cumulative_return
    );
    document.getElementById("cagr").textContent = formatPercent(data.cagr);
    document.getElementById("volatility").textContent = formatPercent(
      data.volatility
    );
    document.getElementById("maxDrawdown").textContent = formatPercent(
      data.max_drawdown
    );
    document.getElementById("longestDD").textContent =
      data.longest_dd_days ?? "0";

    const dateRange = `${data.start_date ?? "—"} to ${data.end_date ?? "—"}`;
    document.getElementById("date-range").textContent = dateRange;
  } catch (err) {
    console.warn("Overview data missing or DOM mismatch", err);
  }
});
