import { renderComparisonCumulativeChart } from "./charts/cumulativeChartComparison.js";

document.addEventListener("DOMContentLoaded", () => {

  const {
    weightsA,
    weightsB,
    startDate,
    initialInvestment,
    nameA,
    nameB,
    nameSPY
  } = window.comparisonConfig;

  renderComparisonCumulativeChart({
    weights_a: weightsA,
    weights_b: weightsB,
    start_date: startDate,
    initial_investment: initialInvestment,
    nameA,
    nameB,
    benchmarkName: nameSPY,
    elementId: "cumulativeChartComparison"
  });
});
