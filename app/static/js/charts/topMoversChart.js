import { chartTheme } from "./theme.js";

export async function renderTopMoversChart(weights) {
  const ctx = document.getElementById("topMoversChart").getContext("2d");

  const csrfToken = document
    .querySelector('meta[name="csrf-token"]')
    ?.getAttribute("content");

  try {
    const response = await fetch("/api/portfolio-top-movers", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken,
      },
      body: JSON.stringify({ weights }),
    });

    const data = await response.json();

    const config = {
      type: "bar",
      data: {
        labels: data.labels,
        datasets: [
          {
            label: "Return (%)",
            data: data.values,
            backgroundColor: data.values.map((v) =>
              v >= 0 ? "#00c49a" : "#f87171"
            ),
            borderRadius: 5,
            barThickness: 16,
          },
        ],
      },
      options: {
        ...chartTheme,
        indexAxis: "y",
        scales: {
          x: {
            ticks: {
              color: "#ddd",
              callback: function (value) {
                return `${value}%`;
              },
            },
            grid: {
              color: "rgba(255, 255, 255, 0.05)",
            },
          },
          y: {
            ticks: {
              color: "#ddd",
            },
            grid: {
              display: false,
            },
          },
        },
        plugins: {
          ...chartTheme.plugins,
          tooltip: {
            backgroundColor: "#1f1f1f",
            titleColor: "#FFD700",
            titleFont: {
              family: "Sora",
              size: 14,
              weight: "600",
            },
            bodyColor: "#f3f4f6",
            bodyFont: {
              family: "Sora",
              size: 13,
              weight: "500",
            },
            borderColor: "#E69622",
            borderWidth: 1.2,
            padding: 10,
            cornerRadius: 6,
            boxPadding: 4,
            animation: {
              duration: 200,
              easing: "easeOutQuart",
            },
            interaction: {
              mode: "nearest",
              intersect: false,
            },
            callbacks: {
              label: function (context) {
                return `${context.raw >= 0 ? "+" : ""}${context.raw.toFixed(
                  2
                )}%`;
              },
            },
          },
        },
      },
    };

    new Chart(ctx, config);
  } catch (error) {
    console.error("🚨 Top movers chart rendering failed:", error.message);
  }
}
