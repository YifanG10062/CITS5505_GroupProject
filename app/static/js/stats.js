// Loads performance summary into portfolio header
fetch("/api/portfolio-summary", {
  method: "POST",                         
  headers: { "Content-Type": "application/json" },  
  body: JSON.stringify({                
    weights: { "MSFT": 0.6, "TSLA": 0.4 },
    start_date: "2020-01-01",
    initial_investment: 10000
  })
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
    set("cumulativeReturn", data.cumulativeReturn, "", "%");
    set("cagr", data.cagr, "", "%");
    set("volatility", data.volatility, "", "%");
    set("maxDrawdown", data.maxDrawdown, "", "%");
    set("longestDD", data.longestDD);
  })
  .catch((err) => {
    console.error("Failed to load portfolio summary:", err);
  });
