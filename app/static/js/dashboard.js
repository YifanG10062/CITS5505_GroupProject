import { renderCumulativeChart } from "./charts/cumulativeChart.js";
import { renderPortfolioSummary } from "./charts/summary.js";

document.addEventListener("DOMContentLoaded", () => {
  const weights = { MSFT: 0.6, TSLA: 0.4 };
  const start_date = "2020-01-01";
  const initial_investment = 10000;

  renderCumulativeChart(weights, start_date, initial_investment);
  renderPortfolioSummary(weights, start_date, initial_investment);
});
