<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import {
  BanknotesIcon,
  ChartBarIcon,
  CreditCardIcon,
} from '@heroicons/vue/24/outline'

import BaseSelect from '../components/BaseSelect.vue'
import ChartArea from '../components/ChartArea.vue'
import LoadingState from '../components/LoadingState.vue'
import SectionHeader from '../components/SectionHeader.vue'
import SummaryCard from '../components/SummaryCard.vue'
import { api } from '../services/api'
import { chartPalette } from '../utils/navigation'

const router = useRouter()

const year = ref(String(new Date().getFullYear()))
const summary = ref(null)
const loading = ref(true)

const yearOptions = Array.from({ length: 5 }, (_, index) => {
  const value = String(2024 + index)
  return { value, label: value }
})

const months = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']

const rows = computed(() => {
  if (!summary.value) return []
  const items = summary.value.months
  return [
    { label: 'Total Receitas', key: 'total_income' },
    { label: 'Despesas Fixas', key: 'total_fixed_expenses' },
    { label: 'Despesas Variáveis', key: 'total_variable_expenses' },
    { label: 'Investimentos', key: 'total_investments' },
    { label: 'Restante', key: 'remaining' },
  ].map((row) => ({
    ...row,
    values: items.map((item) => Number(item[row.key])),
  }))
})

const evolution = computed(() => {
  if (!summary.value) return []
  const items = summary.value.months
  return [
    {
      label: 'Receitas',
      color: chartPalette.green,
      values: items.map((item) => Number(item.total_income)),
    },
    {
      label: 'Despesas',
      color: chartPalette.red,
      values: items.map(
        (item) => Number(item.total_fixed_expenses) + Number(item.total_variable_expenses)
      ),
    },
    {
      label: 'Investimentos',
      color: chartPalette.purple,
      values: items.map((item) => Number(item.total_investments)),
    },
  ]
})

function formatValue(value) {
  return value === 0 ? '0' : value.toLocaleString('pt-BR', { minimumFractionDigits: 2 })
}

function openMonth(index) {
  router.push({
    name: 'visao-mensal',
    query: { month: `${year.value}-${String(index + 1).padStart(2, '0')}` },
  })
}

async function load() {
  loading.value = true
  summary.value = await api.get(`/dashboard/annual?year=${year.value}`)
  loading.value = false
}

watch(year, load)
onMounted(load)
</script>

<template>
  <section>
    <SectionHeader
      title="Visão Anual"
      description="Resumo de receitas, despesas e saldo ao longo do ano."
    >
      <template #actions>
        <BaseSelect
          v-model="year"
          :options="yearOptions"
          class="w-28"
          aria-label="Selecionar ano"
        />
      </template>
    </SectionHeader>

    <LoadingState v-if="loading" />

    <template v-else-if="summary">
      <div class="overflow-x-auto rounded-card border border-neutral-200 bg-white shadow-card">
        <table class="w-full min-w-[52rem] text-left text-sm">
          <thead class="border-b border-neutral-200 bg-neutral-50 text-xs uppercase text-neutral-500">
            <tr>
              <th class="px-4 py-2">Descrição</th>
              <th
                v-for="(month, index) in months"
                :key="month"
                class="cursor-pointer px-3 py-2 text-right hover:text-primary"
                :title="`Abrir a visão mensal de ${month}/${year}`"
                @click="openMonth(index)"
              >
                {{ month }}
              </th>
            </tr>
          </thead>
          <tbody class="divide-y divide-neutral-100">
            <tr v-for="row in rows" :key="row.label">
              <td class="px-4 py-2 font-medium text-neutral-700">{{ row.label }}</td>
              <td
                v-for="(value, index) in row.values"
                :key="index"
                class="cursor-pointer px-3 py-2 text-right tabular-nums hover:bg-neutral-50"
                :class="value < 0 ? 'text-negative' : 'text-neutral-900'"
                @click="openMonth(index)"
              >
                {{ formatValue(value) }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <p class="mt-2 text-xs text-neutral-400">
        Clique em um mês para abrir a visão mensal correspondente.
      </p>

      <div class="mt-6 grid grid-cols-1 gap-4 lg:grid-cols-3">
        <div class="rounded-card border border-neutral-200 bg-white p-4 shadow-card lg:col-span-2">
          <h2 class="mb-2 text-base font-semibold">Evolução Anual</h2>
          <ChartArea :labels="months" :series="evolution" />
          <div class="mt-2 flex items-center justify-center gap-6 text-sm">
            <span v-for="serie in evolution" :key="serie.label" class="flex items-center gap-2">
              <span class="h-2.5 w-2.5 rounded-full" :style="{ backgroundColor: serie.color }" />
              {{ serie.label }}
            </span>
          </div>
        </div>

        <div class="rounded-card border border-neutral-200 bg-white p-4 shadow-card">
          <h2 class="mb-3 text-base font-semibold">Totais do Ano</h2>
          <div class="space-y-3">
            <SummaryCard
              label="Receitas"
              :value="Number(summary.totals.total_income)"
              tone="positive"
              :icon="BanknotesIcon"
            />
            <SummaryCard
              label="Despesas"
              :value="Number(summary.totals.total_expenses)"
              tone="negative"
              :icon="CreditCardIcon"
            />
            <SummaryCard
              label="Investimentos"
              :value="Number(summary.totals.total_investments)"
              tone="investment"
              :icon="ChartBarIcon"
            />
            <SummaryCard
              label="Saldo Final"
              :value="Number(summary.totals.final_balance)"
              tone="neutral"
              :icon="BanknotesIcon"
            />
          </div>
        </div>
      </div>
    </template>
  </section>
</template>
