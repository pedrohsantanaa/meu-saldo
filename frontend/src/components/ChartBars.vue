<script setup>
import { BarController, BarElement, CategoryScale, Chart, LinearScale, Tooltip } from 'chart.js'
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'

Chart.register(BarController, BarElement, CategoryScale, LinearScale, Tooltip)

const props = defineProps({
  labels: { type: Array, default: () => [] },
  // Séries: [{ label, color, values }]
  series: { type: Array, default: () => [] },
})

const canvas = ref(null)
let chart = null

function render() {
  if (!canvas.value) return
  if (chart) chart.destroy()
  chart = new Chart(canvas.value, {
    type: 'bar',
    data: {
      labels: props.labels,
      datasets: props.series.map((serie) => ({
        label: serie.label,
        data: serie.values,
        backgroundColor: serie.color,
        borderRadius: 4,
      })),
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            callback: (value) => `${value / 1000} mil`,
            color: '#94a3b8',
          },
          grid: { color: '#f1f5f9' },
        },
        x: {
          ticks: { color: '#64748b' },
          grid: { display: false },
        },
      },
    },
  })
}

onMounted(render)
watch(() => [props.labels, props.series], render, { deep: true })
onBeforeUnmount(() => chart?.destroy())
</script>

<template>
  <div class="h-56">
    <canvas ref="canvas" />
  </div>
</template>
