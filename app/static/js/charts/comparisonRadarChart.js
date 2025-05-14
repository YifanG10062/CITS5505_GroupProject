export function renderComparisonRadarChart(weightsA, weightsB, startDate, initialInvestment, nameA, nameB) {
  if (!weightsA || !weightsB) {
    console.warn("Cannot render comparison radar chart: weight data missing");
    return;
  }

  const ctx = document.getElementById("comparisonRadarChart");
  if (!ctx) {
    console.warn("Cannot find comparison radar chart container element");
    return;
  }

  // Decode any HTML entities in portfolio names
  nameA = nameA ? decodeHtmlEntities(nameA) : "Portfolio A";
  nameB = nameB ? decodeHtmlEntities(nameB) : "Portfolio B";

  // Fetch performance metrics data from API
  fetch("/api/comparison-radar", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ 
      weights_a: weightsA, 
      weights_b: weightsB, 
      start_date: startDate, 
      initial_investment: initialInvestment 
    }),
  })
    .then((res) => {
      if (!res.ok) {
        throw new Error(`API response error: ${res.status}`);
      }
      return res.json();
    })
    .then((data) => {
      if (!data || !data.portfolio_a || !data.portfolio_b) {
        console.warn("Comparison radar chart data format error");
        return;
      }

      // Log original data for debugging
      console.log("Radar chart original data:", JSON.stringify(data, null, 2));

      const portfolioAData = data.portfolio_a;
      const portfolioBData = data.portfolio_b;

      // For visualization purposes, convert drawdown values from negative to positive
      portfolioAData.max_drawdown = Math.abs(portfolioAData.max_drawdown);
      portfolioBData.max_drawdown = Math.abs(portfolioBData.max_drawdown);

      // Define metric directions and labels
      const metrics = {
        "CAGR": {
          a: portfolioAData.cagr || 0,
          b: portfolioBData.cagr || 0,
          direction: 1, // Positive indicator
        },
        "Volatility": {
          a: portfolioAData.volatility || 0,
          b: portfolioBData.volatility || 0,
          direction: -1, // Negative indicator
        },
        "Sharpe Ratio": {
          a: portfolioAData.sharpe || 0,
          b: portfolioBData.sharpe || 0,
          direction: 1,
        },
        "Sortino Ratio": {
          a: portfolioAData.sortino || 0,
          b: portfolioBData.sortino || 0,
          direction: 1,
        },
        "Calmar Ratio": {
          a: portfolioAData.calmar || 0,
          b: portfolioBData.calmar || 0,
          direction: 1,
        },
        "Max Drawdown": {
          a: portfolioAData.max_drawdown || 0,
          b: portfolioBData.max_drawdown || 0,
          direction: -1,
        },
        "Win Rate": {
          a: portfolioAData.win_rate || 0,
          b: portfolioBData.win_rate || 0,
          direction: 1,
        },
      };

      // Process data
      const labels = Object.keys(metrics);
      const portfolioAValues = [];
      const portfolioBValues = [];

      // Display percentages instead of normalized values (0-100)
      labels.forEach((label) => {
        const metric = metrics[label];
        
        // Ensure values are numbers and valid
        metric.a = typeof metric.a === 'number' && !isNaN(metric.a) ? metric.a : 0;
        metric.b = typeof metric.b === 'number' && !isNaN(metric.b) ? metric.b : 0;

        // For percentage metrics (CAGR, Volatility, Max Drawdown, Win Rate), convert to percentage (0-100)
        if (label === "CAGR" || label === "Volatility" || label === "Max Drawdown" || label === "Win Rate") {
          portfolioAValues.push(metric.a * 100);
          portfolioBValues.push(metric.b * 100);
        } 
        // For ratio metrics (Sharpe, Sortino, Calmar), scale them to suitable range
        else {
          // Scale ratios to 0-5 range, then multiply by 20 to get 0-100 scale
          const aScaled = Math.min(metric.a, 5) * 20;
          const bScaled = Math.min(metric.b, 5) * 20;
          portfolioAValues.push(aScaled);
          portfolioBValues.push(bScaled);
        }
      });

      // Output processed values for debugging
      console.log("Processed chart values:");
      labels.forEach((label, index) => {
        console.log(`${label}: A=${portfolioAValues[index].toFixed(2)}, B=${portfolioBValues[index].toFixed(2)}`);
      });

      // Create chart
      const chartData = {
        labels: labels,
        datasets: [
          {
            label: nameA,
            data: portfolioAValues,
            backgroundColor: "rgba(59, 130, 246, 0.2)", // Blue
            borderColor: "rgb(59, 130, 246)",
            pointBackgroundColor: "rgb(59, 130, 246)",
            pointBorderColor: "#fff",
            pointHoverBackgroundColor: "#fff",
            pointHoverBorderColor: "rgb(59, 130, 246)",
          },
          {
            label: nameB,
            data: portfolioBValues,
            backgroundColor: "rgba(249, 115, 22, 0.2)", // Orange
            borderColor: "rgb(249, 115, 22)",
            pointBackgroundColor: "rgb(249, 115, 22)",
            pointBorderColor: "#fff",
            pointHoverBackgroundColor: "#fff",
            pointHoverBorderColor: "rgb(249, 115, 22)",
          },
        ],
      };

      // Original values mapping for tooltips
      const originalValues = {
        "CAGR": {
          a: (portfolioAData.cagr * 100).toFixed(2) + '%',
          b: (portfolioBData.cagr * 100).toFixed(2) + '%'
        },
        "Volatility": {
          a: (portfolioAData.volatility * 100).toFixed(2) + '%',
          b: (portfolioBData.volatility * 100).toFixed(2) + '%'
        },
        "Sharpe Ratio": {
          a: portfolioAData.sharpe ? portfolioAData.sharpe.toFixed(2) : "0.00",
          b: portfolioBData.sharpe ? portfolioBData.sharpe.toFixed(2) : "0.00"
        },
        "Sortino Ratio": {
          a: portfolioAData.sortino ? portfolioAData.sortino.toFixed(2) : "0.00",
          b: portfolioBData.sortino ? portfolioBData.sortino.toFixed(2) : "0.00"
        },
        "Calmar Ratio": {
          a: portfolioAData.calmar ? portfolioAData.calmar.toFixed(2) : "0.00",
          b: portfolioBData.calmar ? portfolioBData.calmar.toFixed(2) : "0.00"
        },
        "Max Drawdown": {
          a: (portfolioAData.max_drawdown * 100).toFixed(2) + '%',
          b: (portfolioBData.max_drawdown * 100).toFixed(2) + '%'
        },
        "Win Rate": {
          a: (portfolioAData.win_rate * 100).toFixed(2) + '%',
          b: (portfolioBData.win_rate * 100).toFixed(2) + '%'
        }
      };

      // Configuration options
      const config = {
        type: "radar",
        data: chartData,
        options: {
          responsive: true,
          maintainAspectRatio: false,
          elements: {
            line: {
              borderWidth: 3,
            },
            point: {
              radius: 4,
              hoverRadius: 6,
            }
          },
          scales: {
            r: {
              angleLines: {
                display: true,
                color: "rgba(255, 255, 255, 0.3)",
              },
              grid: {
                color: "rgba(255, 255, 255, 0.2)",
              },
              ticks: {
                display: true,
                backdropColor: "transparent",
                font: {
                  size: 11,
                  weight: '500',
                },
                color: "rgba(255, 255, 255, 0.75)",
                z: 1,
                // For percentage display
                min: 0,
                max: 100,
                stepSize: 20,
                callback: function(value) {
                  return value + '%';
                }
              },
              pointLabels: {
                font: {
                  size: 13,
                  weight: "bold",
                },
                color: "rgba(255, 255, 255, 0.85)",
                padding: 5,
              },
              beginAtZero: true
            },
          },
          plugins: {
            legend: {
              position: "bottom",
              labels: {
                padding: 20,
                usePointStyle: true,
                font: {
                  size: 13,
                  weight: '500'
                },
                color: "rgba(255, 255, 255, 0.85)",
              }
            },
            tooltip: {
              callbacks: {
                title: function(tooltipItems) {
                  return tooltipItems[0].label;
                },
                label: function (context) {
                  const datasetLabel = context.dataset.label || '';
                  const index = context.dataIndex;
                  const label = labels[index];
                  const type = context.datasetIndex === 0 ? "a" : "b";
                  const value = originalValues[label][type];
                  return `${datasetLabel}: ${value}`;
                },
              },
              titleFont: {
                size: 14,
                weight: 'bold'
              },
              bodyFont: {
                size: 13
              },
              padding: 12,
              backgroundColor: 'rgba(0, 0, 0, 0.8)',
              titleColor: 'rgba(255, 255, 255, 0.95)',
              bodyColor: 'rgba(255, 255, 255, 0.85)', 
              borderColor: 'rgba(255, 255, 255, 0.15)',
              borderWidth: 1
            },
            title: {
              display: false,
            }
          },
        },
      };

      if (window.comparisonRadarChartInstance) {
        window.comparisonRadarChartInstance.destroy();
      }

      // Render chart and save instance
      window.comparisonRadarChartInstance = new Chart(ctx, config);
    })
    .catch((err) => {
      console.error("Comparison radar chart rendering failed:", err);
    });
}

// Helper function to decode HTML entities
function decodeHtmlEntities(text) {
  if (!text) return "";
  
  const textarea = document.createElement('textarea');
  textarea.innerHTML = text;
  return textarea.value;
} 
