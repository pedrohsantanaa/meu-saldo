<script setup>
import { ArcElement, Chart, Tooltip } from 'chart.js'
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'

Chart.register(ArcElement, Tooltip)

const props = defineProps({
  labels: { type: Array, default: () => [] },
  values: { type: Array, default: () => [] },
  colors: { type: Array, default: () => [] },
  centerValue: { type: String, default: '' },
  centerLabel: { type: String, default: '' },
})

const canvas = ref(null)
let chart = null

function render() {
  if (!canvas.value) return
  if (chart) chart.destroy()
  chart = new Chart(canvas.value, {
    type: 'doughnut',
    data: {
      labels: props.labels,
      datasets: [
        {
          data: props.values,
          backgroundColor: props.colors,
          borderWidth: 0,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      cutout: '68%',
      plugins: { legend: { display: false }, tooltip: { enabled: true } },
    },
  })
}

onMounted(render)
watch(() => [props.labels, props.values, props.colors], render, { deep: true })
onBeforeUnmount(() => chart?.destroy())
</script>

<template>
  <div class="relative h-56">
    <canvas ref="canvas" />
    <div
      v-if="centerValue"
      class="pointer-events-none absolute inset-0 flex flex-col items-center justify-center"
    >
      <span class="text-lg font-semibold text-neutral-900">{{ centerValue }}</span>
      <span v-if="centerLabel" class="text-xs text-neutral-500">{{ centerLabel }}</span>
    </div>
  </div>
</template>
