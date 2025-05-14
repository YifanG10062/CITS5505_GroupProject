import { renderComparisonCumulativeChart } from "./charts/cumulativeChartComparison.js";
import { renderComparisonRadarChart } from "./charts/comparisonRadarChart.js";
import { renderRiskReturnChart } from "./charts/riskReturnChart.js";

document.addEventListener("DOMContentLoaded", () => {
  const {
    weightsA,
    weightsB,
    weightsSPY,
    startDate,
    initialInvestment,
    nameA,
    nameB,
    nameSPY
  } = window.comparisonConfig;

  console.log("Portfolio A weights:", weightsA);
  console.log("Portfolio B weights:", weightsB);
  console.log("SPY weights:", weightsSPY);

  // Format weights data for chart rendering
  const formattedWeightsA = convertToDictFormat(weightsA);
  const formattedWeightsB = convertToDictFormat(weightsB);
  const formattedWeightsSPY = convertToDictFormat(weightsSPY);

  renderComparisonCumulativeChart({
    weights_a: formattedWeightsA,
    weights_b: formattedWeightsB,
    weights_spy: formattedWeightsSPY,
    start_date: startDate,
    initial_investment: initialInvestment,
    nameA,
    nameB,
    benchmarkName: nameSPY,
    elementId: "cumulativeChartComparison"
  });

  // Render portfolio comparison radar chart
  renderComparisonRadarChart(
    formattedWeightsA,
    formattedWeightsB,
    startDate,
    initialInvestment,
    nameA,
    nameB
  );

  // Render risk-return scatter plot 
  renderRiskReturnChart(
    formattedWeightsA,
    formattedWeightsB,
    startDate,
    initialInvestment,
    nameA,
    nameB
  );

  // Enhance responsive layout for comparison page
  handleResponsiveLayout();
  
  // Calculate and display portfolio metrics
  calculatePortfolioMetrics(weightsA, weightsB);
  
  // Restore fixWeightDisplays function call
  fixWeightDisplays();
});

// Convert new format weight list to dictionary format
function convertToDictFormat(weights) {
  // If already in dictionary format, return directly
  if (typeof weights === 'object' && !Array.isArray(weights)) {
    return weights;
  }
  
  // If in array format, convert to dictionary
  const result = {};
  if (Array.isArray(weights)) {
    weights.forEach(item => {
      result[item.ticker] = item.weight;
    });
  }
  return result;
}

// Calculate key metrics for portfolios
function calculatePortfolioMetrics(weightsA, weightsB) {
  const formattedWeightsA = convertToDictFormat(weightsA);
  const formattedWeightsB = convertToDictFormat(weightsB);
  
  const config = window.comparisonConfig || {};
  const startDate = config.startDate || "2015-01-01";
  const initialInvestment = config.initialInvestment || 1000;
  
  const payload = {
    weights_a: formattedWeightsA,
    weights_b: formattedWeightsB,
    start_date: startDate,
    initial_investment: initialInvestment
  };
  
  fetch("/api/comparison_metrics", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  })
  .then(res => {
    if (!res.ok) {
      console.error("Error fetching metrics:", res.status);
      return;
    }
    return res.json();
  })
  .then(data => {
    if (!data) return;
    
    const { summary } = data;
    
    // Portfolio A metrics
    document.getElementById('volatilityA').textContent = 
      (summary.portfolio_a.volatility * 100).toFixed(1) + "%";
    document.getElementById('volatilityA').classList.add('volatility-value');
    document.getElementById('volatilityA').closest('.mini-metric').classList.add('volatility-card');

    document.getElementById('cagrA').textContent = 
      (summary.portfolio_a.cagr * 100).toFixed(1) + "%";
    document.getElementById('cagrA').classList.add('cagr-value');
    document.getElementById('cagrA').closest('.mini-metric').classList.add('cagr-card');

    document.getElementById('maxDrawdownA').textContent = 
      (summary.portfolio_a.maxDrawdown * 100).toFixed(1) + "%";
    document.getElementById('maxDrawdownA').classList.add('drawdown-value');
    document.getElementById('maxDrawdownA').closest('.mini-metric').classList.add('drawdown-card');
    
    // Portfolio B metrics
    document.getElementById('volatilityB').textContent = 
      (summary.portfolio_b.volatility * 100).toFixed(1) + "%";
    document.getElementById('volatilityB').classList.add('volatility-value');
    document.getElementById('volatilityB').closest('.mini-metric').classList.add('volatility-card');

    document.getElementById('cagrB').textContent = 
      (summary.portfolio_b.cagr * 100).toFixed(1) + "%";
    document.getElementById('cagrB').classList.add('cagr-value');
    document.getElementById('cagrB').closest('.mini-metric').classList.add('cagr-card');

    document.getElementById('maxDrawdownB').textContent = 
      (summary.portfolio_b.maxDrawdown * 100).toFixed(1) + "%";
    document.getElementById('maxDrawdownB').classList.add('drawdown-value');
    document.getElementById('maxDrawdownB').closest('.mini-metric').classList.add('drawdown-card');
  });
}

function handleResponsiveLayout() {
  // Function to adjust card layout
  const adjustLayout = () => {
    const isMobile = window.innerWidth < 768;
    const isTablet = window.innerWidth >= 768 && window.innerWidth < 992;
    
    // Get all description metric rows
    const descriptionRows = document.querySelectorAll('.description-metrics-row');
    
    // Adjust layout based on screen size, but maintain equal division rules
    descriptionRows.forEach(row => {
      // Get column count
      const numCols = parseInt(row.className.match(/cols-(\d+)/)[1]);
      
      // Always use single column layout on mobile devices
      if (isMobile) {
        row.style.gridTemplateColumns = '1fr';
      } 
      // On tablets, maintain equal division but max 2 columns
      else if (isTablet) {
        if (numCols === 1) {
          row.style.gridTemplateColumns = '1fr';
        } else {
          row.style.gridTemplateColumns = 'repeat(2, 1fr)'; // Max 2 columns on tablet
        }
      }
      // On large screens, set columns based on actual card count
      else {
        // Remove any inline styles, use CSS class defined grid layout
        row.style.removeProperty('grid-template-columns');
      }
    });
    
    // Adjust card margins on narrow devices
    const comparisonCards = document.querySelectorAll('.dashboard-overview');
    if (isMobile && comparisonCards.length > 1) {
      comparisonCards[0].classList.add('mb-4');
    } else if (comparisonCards.length > 1) {
      comparisonCards[0].classList.remove('mb-4');
    }
    
    // Set fixed height to ensure all cards have the same height
    const descriptionMetrics = document.querySelectorAll('.description-metric');
    if (!isMobile) {
      // Fixed height on desktop view
      descriptionMetrics.forEach(metric => {
        metric.style.minHeight = '100px';
      });
    } else {
      // Adapt to content on mobile view
      descriptionMetrics.forEach(metric => {
        metric.style.minHeight = 'auto';
      });
    }
    
    // beautify the second row of performance, AI, Leverage
    const descriptionLabels = document.querySelectorAll('.stock-name');
    descriptionLabels.forEach(label => {
      if (label.textContent.includes('Performance')) {
        label.style.color = '#6366f1';
        label.style.fontWeight = '600';
      } else if (label.textContent.includes('AI')) {
        label.style.color = '#3b82f6';
        label.style.fontWeight = '600';
      } else if (label.textContent.includes('Leverage')) {
        label.style.color = '#f97316';
        label.style.fontWeight = '600';
      }
    });
    
    // Ensure all cards in the same row have equal height
    const equalizeMiniMetricHeight = () => {
      const rows = document.querySelectorAll('.description-metrics-row');
      rows.forEach(row => {
        const metrics = row.querySelectorAll('.mini-metric');
        let maxHeight = 0;
        
        // Reset heights
        metrics.forEach(metric => metric.style.height = 'auto');
        
        // Find maximum height
        metrics.forEach(metric => {
          const height = metric.offsetHeight;
          if (height > maxHeight) maxHeight = height;
        });
        
        // Apply maximum height
        if (maxHeight > 0 && !isMobile) {
          metrics.forEach(metric => metric.style.height = `${maxHeight}px`);
        }
      });
    };
    
    // Execute height equalization after DOM rendering is complete
    setTimeout(() => {
      equalizeMiniMetricHeight();
      equalizeCardWidths();
    }, 100);
  };
  
  // Initial adjustment
  adjustLayout();
  
  // Listen for window resize events
  window.addEventListener('resize', adjustLayout);
  
  // execute the layout adjustment once after the page loads
  window.addEventListener('load', adjustLayout);
}

// Fix weight displays to show integer percentages only
function fixWeightDisplays() {
  // Find all stock weight displays
  const weightElements = document.querySelectorAll('.stock-weight');
  
  // Iterate through each element, replace content
  weightElements.forEach(element => {
    const text = element.textContent || '';
    // Force replace with integer form regardless of decimal point
    if (text) {
      // Extract number part from text
      const match = text.match(/\(([\d\.]+)%\)/);
      if (match && match[1]) {
        const num = parseFloat(match[1]);
        if (num > 0) {  // Only display if value is greater than 0
          element.textContent = `(${Math.round(num)}%)`;
        } else {
          element.textContent = '';  // Don't display if 0
        }
      }
    }
  });
}

// Ensure all cards have equal width while respecting CSS equal division rules
const equalizeCardWidths = () => {
  const rows = document.querySelectorAll('.description-metrics-row');
  rows.forEach(row => {
    const numCols = parseInt(row.className.match(/cols-(\d+)/)[1]);
    
    const cards = row.querySelectorAll('.mini-metric');
    cards.forEach(card => {
      card.style.overflow = 'hidden';
      card.style.boxSizing = 'border-box';
      // Remove styles that might interfere with CSS grid layout
      card.style.removeProperty('width');
      card.style.removeProperty('max-width');
      card.style.removeProperty('min-width');
    });
  });
};
