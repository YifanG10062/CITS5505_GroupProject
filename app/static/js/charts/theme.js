export const chartTheme = {
  responsive: true,
  maintainAspectRatio: false,
  interaction: { mode: "index", intersect: false },
  plugins: {
    legend: {
      labels: {
        color: "#f8f9fa",
        font: { family: "Poppins", size: 12, weight: "500" },
        padding: 20,
      },
    },
    title: {
      display: false,
      text: "Cumulative Returns vs SPY",
      color: "#f3f4f6",
      font: {
        size: 16,
        family: "Poppins",
        weight: "600",
      },
      padding: {
        top: 10,
        bottom: 20,
      },
    },
    tooltip: {
      backgroundColor: "#1f1f1f",
      titleColor: "#f8f9fa",
      bodyColor: "#d1d1d1",
      borderColor: "#333",
      borderWidth: 1,
    },
  },
  scales: {
    x: {
      ticks: {
        color: "#ccc",
        font: {
          size: 11,
          family: "Poppins",
        },
        maxTicksLimit: 6,
        autoSkip: true,
      },
      grid: {
        display: false,
      },
    },
    y: {
      ticks: {
        color: "#ccc",
        font: {
          size: 11,
          family: "Poppins",
        },
      },
      grid: {
        color: "rgba(255, 255, 255, 0.1)",
        borderDash: [3, 3],
      },
    },
  },
};
