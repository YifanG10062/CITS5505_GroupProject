fetch("/api/cumulative")
  .then((res) => res.json())
  .then((data) => {
    const ctx = document.getElementById("cumulativeChart").getContext("2d");
    new Chart(ctx, {
      type: "line",
      data: {
        labels: data.labels,
        datasets: [
          {
            label: "Strategy",
            data: data.strategy,
            borderColor: "#4fd1c5",
            fill: false,
            tension: 0.4,
          },
          {
            label: "SPY Benchmark",
            data: data.benchmark,
            borderColor: "#f6ad55",
            fill: false,
            tension: 0.4,
          },
        ],
      },
      options: {
        responsive: true,
        plugins: {
          legend: { labels: { color: "#ffffff" } },
        },
        scales: {
          x: { ticks: { color: "#aaa" } },
          y: { ticks: { color: "#aaa" } },
        },
      },
    });
  });
