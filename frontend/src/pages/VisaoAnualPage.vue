<script setup>
import { computed, ref } from 'vue'
import {
  BanknotesIcon,
  ChartBarIcon,
  CreditCardIcon,
} from '@heroicons/vue/24/outline'

import BaseSelect from '../components/BaseSelect.vue'
import ChartArea from '../components/ChartArea.vue'
import SectionHeader from '../components/SectionHeader.vue'
import SummaryCard from '../components/SummaryCard.vue'
import { chartPalette } from '../utils/navigation'

const year = ref('2026')

const yearOptions = Array.from({ length: 5 }, (_, index) => {
  const value = String(2024 + index)
  return { value, label: value }
})

const months = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']

const rows = [
  { label: 'Total Receitas', values: [7000, 2000, 15350, 15228, 14412, 14385, 16963, 13900, 14102, 14828, 17214, 14724] },
  { label: 'Despesas Fixas', values: [1905, 1820, 1775, 1822, 2048, 2157, 2090, 1776, 1357, 1947, 1902, 1900] },
  { label: 'Despesas Variáveis', values: [5123, 3423, 12317, 11217, 7782, 7268, 8279, 8076, 7619, 8010, 8683, 7591] },
  { label: 'Investimentos', values: [0, 0, 0, 0, 1800, 4000, 4000, 5500, 5500, 5500, 5500, 5500] },
  { label: 'Restante', values: [-28, -3243, 1258, 389, 583, 961, 1095, -1452, -374, -628, 1129, -266] },
]

const evolution = [
  { label: 'Receitas', color: chartPalette.green, values: rows[0].values },
  { label: 'Despesas', color: chartPalette.red, values: rows[1].values.map((value, index) => value + rows[2].values[index]) },
  { label: 'Investimentos', color: chartPalette.purple, values: rows[3].values },
]

const totals = computed(() => ({
  receitas: rows[0].values.reduce((sum, value) => sum + value, 0),
  despesas:
    rows[1].values.reduce((sum, value) => sum + value, 0) +
    rows[2].values.reduce((sum, value) => sum + value, 0),
  investimentos: rows[3].values.reduce((sum, value) => sum + value, 0),
  saldo: rows[4].values.reduce((sum, value) => sum + value, 0),
}))
</script>

<template>
  <section>
    <SectionHeader title="Visão Anual" description="Resumo de receitas, despesas e saldo ao longo do ano.">
      <template #actions>
        <BaseSelect
          v-model="year"
          :options="yearOptions"
          class="w-28"
          aria-label="Selecionar ano"
        />
      </template>
    </SectionHeader>

    <div class="overflow-x-auto rounded-card border border-neutral-200 bg-white shadow-card">
      <table class="w-full min-w-[52rem] text-left text-sm">
        <thead class="border-b border-neutral-200 bg-neutral-50 text-xs uppercase text-neutral-500">
          <tr>
            <th class="px-4 py-2">Descrição</th>
            <th v-for="month in months" :key="month" class="px-3 py-2 text-right">{{ month }}</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-neutral-100">
          <tr v-for="row in rows" :key="row.label">
            <td class="px-4 py-2 font-medium text-neutral-700">{{ row.label }}</td>
            <td
              v-for="(value, index) in row.values"
              :key="index"
              class="px-3 py-2 text-right tabular-nums"
              :class="value < 0 ? 'text-negative' : 'text-neutral-900'"
            >
              {{ value.toLocaleString('pt-BR') }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>

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
          <SummaryCard label="Receitas" :value="totals.receitas" tone="positive" :icon="BanknotesIcon" />
          <SummaryCard label="Despesas" :value="totals.despesas" tone="negative" :icon="CreditCardIcon" />
          <SummaryCard label="Investimentos" :value="totals.investimentos" tone="investment" :icon="ChartBarIcon" />
          <SummaryCard label="Saldo Final" :value="totals.saldo" tone="neutral" :icon="BanknotesIcon" />
        </div>
      </div>
    </div>
  </section>
</template>
