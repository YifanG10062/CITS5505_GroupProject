export const chartTheme = {
  responsive: true,
  maintainAspectRatio: false,
  interaction: { mode: "index", intersect: false },
  animation: {
    duration: 1200, 
    easing: "easeOutCubic", 
  },
  hover: {
    animationDuration: 400, 
    mode: "nearest",
    intersect: true,
  },
  plugins: {
    legend: {
      labels: {
        color: "#f8f9fa",
        font: { family: "Sora", size: 12, weight: "500" },
        padding: 20,
      },
    },
    title: {
      display: false,
      text: "Cumulative Returns vs SPY",
      color: "#f3f4f6",
      font: {
        size: 16,
        family: "Sora",
        weight: "600",
      },
      padding: {
        top: 10,
        bottom: 20,
      },
    },
    tooltip: {
      backgroundColor: "#1f1f1f",
      titleColor: "#FFD700",
      titleFont: {
        family: "Sora",
        weight: "600",
        size: 14,
      },
      bodyColor: "#f3f4f6",
      bodyFont: {
        family: "Sora",
        weight: "500",
        size: 13,
      },
      borderColor: "#E69622",
      borderWidth: 1.2,
      padding: 10,
      cornerRadius: 8,
      boxPadding: 6,
      callbacks: {
        title: function (tooltipItems) {
          const rawLabel = tooltipItems[0].label;
          const date = new Date(rawLabel);
          return date.toLocaleDateString("en-US", {
            month: "short",
            year: "numeric",
          });
        },
      },
    },
  },
  scales: {
    x: {
      ticks: {
        color: "#ccc",
        font: {
          size: 11,
          family: "Sora",
        },
        maxTicksLimit: 6,
        autoSkip: true,
        callback: function (value, index, values) {
          const rawLabel = this.getLabelForValue(value);
          const date = new Date(rawLabel);
          return date.getFullYear();
        },
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
          family: "Sora",
        },
      },
      grid: {
        color: "rgba(255, 255, 255, 0.1)",
        borderDash: [3, 3],
      },
    },
  },
};
