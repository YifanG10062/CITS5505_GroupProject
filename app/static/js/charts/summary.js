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
      const set = (id, value, prefix = "", suffix = "") => {
        const el = document.getElementById(id);
        if (el) el.textContent = `${prefix}${value}${suffix}`;
      };

      set("netWorth", data.netWorth.toLocaleString(), "$");
      set("initial", data.initial.toLocaleString(), "$");
      set("profit", data.profit.toLocaleString(), "$");

      // Correctly convert decimal values to percentages
      set(
        "cumulativeReturn",
        (data.cumulativeReturn * 100).toFixed(2),
        "",
        "%"
      );
      set("cagr", (data.cagr * 100).toFixed(2), "", "%");
      set("maxDrawdown", (data.maxDrawdown * 100).toFixed(2), "", "%");

      // Leave volatility as raw number unless confirmed to be %
      set("volatility", data.volatility.toFixed(2));

      set("longestDD", data.longestDD || "0");
    })
    .catch((err) => {
      console.error("Failed to load portfolio summary:", err);
    });
}
