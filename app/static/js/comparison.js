/*
 * comparison.js
 * Dynamically renders the Comparison page charts:
 * 1) Metrics bar chart comparing Portfolio A vs B
 * 2) Cumulative return line chart for A vs B
 * 3) Allocation pie charts for A and B
 */

// Wait until DOM is fully loaded
document.addEventListener('DOMContentLoaded', () => {
  // Extract configuration injected by template
  const {
    weightsA,
    weightsB,
    startDate,
    initialInvestment,
    nameA,
    nameB
  } = window.comparisonConfig;

  // Fetch summary metrics for both portfolios
  Promise.all([
    fetch('/api/portfolio-summary', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        weights: weightsA,
        start_date: startDate,
        initial_investment: initialInvestment
      })
    }).then(res => res.json()),
    fetch('/api/portfolio-summary', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        weights: weightsB,
        start_date: startDate,
        initial_investment: initialInvestment
      })
    }).then(res => res.json())
  ])
    .then(([summaryA, summaryB]) => {
      // Prepare data for metrics bar chart
      const metricLabels = [
        'Net Worth',
        'Profit',
        'Volatility',
        'Total Return',
        'CAGR',
        'Max Drawdown',
        'Longest DD'
      ];

      const valuesA = [
        summaryA.netWorth,
        summaryA.profit,
        summaryA.volatility,
        summaryA.cumulativeReturn,
        summaryA.cagr,
        summaryA.maxDrawdown,
        summaryA.longestDD
      ];

      const valuesB = [
        summaryB.netWorth,
        summaryB.profit,
        summaryB.volatility,
        summaryB.cumulativeReturn,
        summaryB.cagr,
        summaryB.maxDrawdown,
        summaryB.longestDD
      ];

      const ctxMetrics = document.getElementById('metricsChart').getContext('2d');
      new Chart(ctxMetrics, {
        type: 'bar',
        data: {
          labels: metricLabels,
          datasets: [
            {
              label: nameA,
              data: valuesA,
              backgroundColor: 'rgba(54, 162, 235, 0.5)'
            },
            {
              label: nameB,
              data: valuesB,
              backgroundColor: 'rgba(255, 99, 132, 0.5)'
            }
          ]
        },
        options: {
          responsive: true,
          scales: {
            y: { beginAtZero: true }
          }
        }
      });
    })
    .catch(err => console.error('Metrics fetch error:', err));

  // Fetch and render cumulative return comparison
  fetch('/api/comparison_timeseries', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      weights_a: weightsA,
      weights_b: weightsB,
      start_date: startDate,
      initial_investment: initialInvestment
    })
  })
    .then(res => res.json())
    .then(data => {
      const ctxLine = document.getElementById('comparisonChart').getContext('2d');
      new Chart(ctxLine, {
        type: 'line',
        data: {
          labels: data.labels,
          datasets: [
            {
              label: nameA,
              data: data.portfolio_a,
              fill: false,
              tension: 0.1
            },
            {
              label: nameB,
              data: data.portfolio_b,
              fill: false,
              tension: 0.1
            }
          ]
        },
        options: {
          responsive: true,
          scales: {
            x: { title: { display: true, text: 'Date' } },
            y: { title: { display: true, text: 'Cumulative Value' } }
          }
        }
      });
    })
    .catch(err => console.error('Comparison timeseries error:', err));

  // Render allocation pie charts for both portfolios
  const ctxAllocA = document.getElementById('allocationChartA').getContext('2d');
  new Chart(ctxAllocA, {
    type: 'pie',
    data: {
      labels: Object.keys(weightsA),
      datasets: [
        {
          data: Object.values(weightsA),
          // Chart.js will auto-assign colors
        }
      ]
    }
  });

  const ctxAllocB = document.getElementById('allocationChartB').getContext('2d');
  new Chart(ctxAllocB, {
    type: 'pie',
    data: {
      labels: Object.keys(weightsB),
      datasets: [
        {
          data: Object.values(weightsB)
        }
      ]
    }
  });
});
