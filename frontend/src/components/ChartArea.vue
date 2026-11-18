<script setup>
import {
  CategoryScale,
  Chart,
  Filler,
  LinearScale,
  LineElement,
  PointElement,
  Tooltip,
} from 'chart.js'
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'

Chart.register(CategoryScale, LinearScale, PointElement, LineElement, Filler, Tooltip)

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
    type: 'line',
    data: {
      labels: props.labels,
      datasets: props.series.map((serie) => ({
        label: serie.label,
        data: serie.values,
        borderColor: serie.color,
        backgroundColor: `${serie.color}33`,
        fill: true,
        tension: 0.35,
        pointRadius: 2,
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
