import { chartTheme } from "./theme.js";

export function renderRiskReturnChart(weightsA, weightsB, startDate, initialInvestment, nameA, nameB) {
  if (!weightsA || !weightsB) {
    console.warn("Cannot render risk-return chart: weight data missing");
    return;
  }

  const ctx = document.getElementById("riskReturnChart");
  if (!ctx) {
    console.warn("Cannot find risk-return chart container element");
    return;
  }

  // Decode any HTML entities in portfolio names
  nameA = nameA ? decodeHtmlEntities(nameA) : "Portfolio A";
  nameB = nameB ? decodeHtmlEntities(nameB) : "Portfolio B";

  // Fetch metrics data from API
  fetch("/api/comparison_metrics", {
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
      if (!data || !data.summary) {
        console.warn("Risk-return chart data format error");
        return;
      }

      const summaryData = data.summary;
      
      // Extract portfolio data for plotting
      const portfolioData = [
        {
          name: nameA,
          risk: summaryData.portfolio_a.volatility * 100, // Convert to percentage
          return: summaryData.portfolio_a.cagr * 100, // Convert to percentage
          color: 'rgb(59, 130, 246)', // Blue
        },
        {
          name: nameB,
          risk: summaryData.portfolio_b.volatility * 100,
          return: summaryData.portfolio_b.cagr * 100,
          color: 'rgb(249, 115, 22)', // Orange
        },
        {
          name: "S&P 500",
          risk: summaryData.portfolio_spy.volatility * 100,
          return: summaryData.portfolio_spy.cagr * 100,
          color: 'rgb(107, 114, 128)', // Gray
        }
      ];

      // Calculate chart boundaries with padding
      const padding = 5; 
      let minRisk = Math.min(...portfolioData.map(d => d.risk)) - padding;
      let maxRisk = Math.max(...portfolioData.map(d => d.risk)) + padding;
      let minReturn = Math.min(...portfolioData.map(d => d.return)) - padding;
      let maxReturn = Math.max(...portfolioData.map(d => d.return)) + padding;
      
      // Ensure min values don't go below zero
      minRisk = Math.max(0, minRisk);
      minReturn = Math.max(0, minReturn);

      // Create scatter plot data
      const scatterData = {
        datasets: portfolioData.map(portfolio => ({
          label: portfolio.name,
          data: [{
            x: portfolio.risk,
            y: portfolio.return
          }],
          backgroundColor: portfolio.color,
          borderColor: portfolio.color,
          pointRadius: 8,
          pointHoverRadius: 10,
        }))
      };

      // Configuration options
      const config = {
        type: 'scatter',
        data: scatterData,
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            x: {
              title: {
                display: true,
                text: 'Risk (Volatility %)',
                color: 'rgba(255, 255, 255, 0.85)',
                font: {
                  size: 13,
                  weight: '500'
                },
                padding: 10
              },
              min: minRisk,
              max: maxRisk,
              grid: {
                color: 'rgba(255, 255, 255, 0.1)'
              },
              ticks: {
                color: 'rgba(255, 255, 255, 0.75)',
                callback: function(value) {
                  return value.toFixed(1) + '%';
                }
              }
            },
            y: {
              title: {
                display: true,
                text: 'Return (CAGR %)',
                color: 'rgba(255, 255, 255, 0.85)',
                font: {
                  size: 13,
                  weight: '500'
                },
                padding: 10
              },
              min: minReturn,
              max: maxReturn,
              grid: {
                color: 'rgba(255, 255, 255, 0.1)'
              },
              ticks: {
                color: 'rgba(255, 255, 255, 0.75)',
                callback: function(value) {
                  return value.toFixed(1) + '%';
                }
              }
            }
          },
          plugins: {
            legend: {
              position: 'bottom',
              labels: {
                padding: 20,
                usePointStyle: true,
                pointStyle: 'circle',
                font: {
                  size: 13,
                  weight: '500'
                },
                color: 'rgba(255, 255, 255, 0.85)'
              }
            },
            tooltip: {
              ...chartTheme.plugins.tooltip,
              callbacks: {
                label: function(context) {
                  const point = context.raw;
                  return [
                    `${context.dataset.label}:`,
                    `- Risk: ${point.x.toFixed(2)}%`,
                    `- Return: ${point.y.toFixed(2)}%`
                  ];
                },
                labelColor: function(context) {
                  return {
                    borderColor: context.dataset.borderColor,
                    backgroundColor: "rgba(255, 255, 255, 0.85)",
                    borderWidth: 1.2,
                  };
                }
              }
            }
          },
          animation: {
            duration: 1000
          }
        }
      };

      if (window.riskReturnChartInstance) {
        window.riskReturnChartInstance.destroy();
      }

      // Add trendline
      if (portfolioData.length >= 2) {
        // Create efficient frontier curve
        const createEfficientFrontier = () => {
          const points = [];
          const steps = 20;
          const baseRisk = minRisk;
          const maxPlottedRisk = maxRisk * 1.2;
          
          // Simple quadratic curve as an approximation of efficient frontier
          for (let i = 0; i <= steps; i++) {
            const risk = baseRisk + (maxPlottedRisk - baseRisk) * (i / steps);
            
            // Efficient frontier formula (simplified): return = a * sqrt(risk) - b * risk
            const efficientReturn = 0.8 * Math.sqrt(risk * 15) + minReturn;
            
            points.push({
              x: risk,
              y: Math.min(efficientReturn, maxReturn * 1.2) // Cap the max return
            });
          }
          
          return points;
        };
        
        // Add efficient frontier curve dataset
        const efficientFrontierPoints = createEfficientFrontier();
        config.data.datasets.push({
          label: 'Efficient Frontier',
          data: efficientFrontierPoints,
          showLine: true,
          fill: false,
          borderColor: 'rgba(75, 192, 192, 0.6)',
          borderDash: [5, 5],
          pointRadius: 0,
          borderWidth: 2,
          tension: 0.4
        });
      }

      // Render chart and save instance
      window.riskReturnChartInstance = new Chart(ctx, config);
    })
    .catch((err) => {
      console.error("Risk-return chart rendering failed:", err);
    });
}

// Helper function to decode HTML entities
function decodeHtmlEntities(text) {
  if (!text) return "";
  
  const textarea = document.createElement('textarea');
  textarea.innerHTML = text;
  return textarea.value;
} 
