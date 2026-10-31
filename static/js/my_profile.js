document.addEventListener('DOMContentLoaded', function() {
  const dataElement = document.getElementById('profileChartData');
  if (!dataElement || typeof Chart === 'undefined') return;

  const chartData = JSON.parse(dataElement.textContent);
  const styles = getComputedStyle(document.documentElement);
  const textColor = styles.getPropertyValue('--text-muted').trim();
  const gridColor = styles.getPropertyValue('--border-light').trim();
  const cardColor = styles.getPropertyValue('--bg-card').trim();

  const trendCanvas = document.getElementById('myScoreTrendChart');
  if (trendCanvas) {
    new Chart(trendCanvas, {
      type: 'line',
      data: {
        labels: chartData.trendLabels,
        datasets: [{
          label: 'Average quality score',
          data: chartData.trendScores,
          borderColor: '#2780e8',
          backgroundColor: 'rgba(39, 128, 232, 0.1)',
          borderWidth: 2,
          tension: 0.28,
          fill: true,
          pointRadius: 2,
          pointHoverRadius: 4
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: function(context) {
                return 'Score: ' + context.raw + '%';
              }
            }
          }
        },
        scales: {
          x: {
            grid: { color: gridColor },
            ticks: { color: textColor, font: { size: 9 }, maxRotation: 0 }
          },
          y: {
            min: 0,
            max: 100,
            grid: { color: gridColor },
            ticks: {
              color: textColor,
              font: { size: 9 },
              callback: function(value) { return value + '%'; }
            }
          }
        }
      }
    });
  }

  const distributionCanvas = document.getElementById('myScoreDistributionChart');
  if (distributionCanvas) {
    new Chart(distributionCanvas, {
      type: 'doughnut',
      data: {
        labels: chartData.scoreLabels,
        datasets: [{
          data: chartData.scoreData,
          backgroundColor: ['#ef4444', '#f59e0b', '#10b981'],
          borderColor: cardColor,
          borderWidth: 2,
          hoverOffset: 3
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: '72%',
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: function(context) {
                return context.label + ': ' + context.raw + ' audits';
              }
            }
          }
        }
      }
    });
  }
});
