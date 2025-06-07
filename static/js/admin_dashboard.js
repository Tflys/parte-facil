// static/js/admin_dashboard.js
document.addEventListener("DOMContentLoaded", function() {
  // KPI animado (contador)
  document.querySelectorAll('.kpi-value[data-value]').forEach(el => {
    let val = parseInt(el.dataset.value), curr = 0;
    const inc = Math.max(1, Math.ceil(val / 60));
    const timer = setInterval(() => {
      curr += inc;
      if (curr >= val) {
        el.textContent = val;
        clearInterval(timer);
      } else {
        el.textContent = curr;
      }
    }, 12);
  });

  // Si tienes un gráfico con Chart.js
  if (window.Chart && document.getElementById('grafico-trabajos-mes')) {
    const ctx = document.getElementById('grafico-trabajos-mes').getContext('2d');
    new Chart(ctx, {
      type: 'bar',
      data: {
        labels: window.labelsMeses || [],
        datasets: [{
          label: 'Trabajos por mes',
          data: window.dataMeses || [],
          backgroundColor: '#00ba56'
        }]
      },
      options: {
        responsive: true,
        plugins: { legend: { display: false } }
      }
    });
  }
});
