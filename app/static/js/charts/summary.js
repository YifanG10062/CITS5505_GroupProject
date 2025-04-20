//Loads and displays portfolio summary metrics into the dashboard header.
export function renderPortfolioSummary(
  weights,
  start_date,
  initial_investment
) {
  fetch("/api/portfolio-summary", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ weights, start_date, initial_investment }),
  })
    .then((res) => res.json())
    .then((data) => {
      // Helper to update text content of HTML elements
      const set = (id, value, prefix = "", suffix = "") => {
        const el = document.getElementById(id);
        if (el) el.textContent = `${prefix}${value}${suffix}`;
      };

      set("netWorth", data.netWorth.toLocaleString(), "$");
      set("initial", data.initial.toLocaleString(), "$");
      set("profit", data.profit.toLocaleString(), "$");
      set("cumulativeReturn", data.cumulativeReturn, "", "%");
      set("cagr", data.cagr, "", "%");
      set("volatility", data.volatility, "", "%");
      set("maxDrawdown", data.maxDrawdown, "", "%");
      set("longestDD", data.longestDD);
    })
    .catch((err) => {
      console.error("Failed to load portfolio summary:", err);
    });
}
