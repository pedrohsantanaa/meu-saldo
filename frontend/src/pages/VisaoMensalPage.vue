<script setup>
import { ref } from 'vue'
import {
  BanknotesIcon,
  ChartBarIcon,
  CreditCardIcon,
  PlusIcon,
} from '@heroicons/vue/24/outline'

import BaseButton from '../components/BaseButton.vue'
import ChartBars from '../components/ChartBars.vue'
import ChartDonut from '../components/ChartDonut.vue'
import MonthSelector from '../components/MonthSelector.vue'
import SectionHeader from '../components/SectionHeader.vue'
import SummaryCard from '../components/SummaryCard.vue'
import { chartPalette } from '../utils/navigation'

const period = ref(new Date(2026, 10, 1))

const despesasComposition = {
  total: 16085.7,
  items: [
    { label: 'Fixas', value: 1902.41, percent: '11,8%', color: chartPalette.blue },
    { label: 'Variáveis', value: 8683.29, percent: '54,0%', color: chartPalette.orange },
    { label: 'Cartões', value: 4873.41, percent: '30,3%', color: chartPalette.purple },
  ],
}

const monthlyBars = {
  labels: ['Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov'],
  series: [
    { label: 'Receitas', color: chartPalette.green, values: [14385, 16963, 13900, 14102, 14828, 17214] },
    { label: 'Despesas', color: chartPalette.red, values: [13424, 15869, 13452, 14247, 14985, 16085] },
  ],
}

const contasAReceber = [
  { description: 'Salário Senac', value: 2976.0 },
  { description: 'FaSeC', value: null },
  { description: 'Salário IF', value: 7175.09 },
  { description: 'Agência Fomento', value: 5163.16 },
  { description: 'Extras', value: 1900.0 },
]

const contasFixas = [
  { description: 'Aluguel', value: 950.0 },
  { description: 'Água e Energia', value: 250.0 },
  { description: 'Proteção Veicular', value: 152.0 },
  { description: 'Recarga Celular/Internet', value: 246.36 },
  { description: 'Parcela Carro', value: 406.08 },
]

const contasVariaveis = [
  { description: 'Fatura Cartão - BB', value: 4873.41 },
  { description: 'Fatura Cartão - Inter', value: 290.59 },
  { description: 'Lanches', value: null },
  { description: 'Extras', value: null },
  { description: 'Gasolina', value: null },
]

function money(value) {
  return value === null ? '—' : value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })
}
</script>

<template>
  <section>
    <SectionHeader title="Visão Mensal" description="Acompanhe suas receitas, despesas e saldo do mês.">
      <template #actions>
        <MonthSelector v-model="period" />
        <BaseButton>
          <PlusIcon class="h-4 w-4" aria-hidden="true" />
          Nova Movimentação
        </BaseButton>
      </template>
    </SectionHeader>

    <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
      <SummaryCard label="Receitas" :value="17214.25" tone="positive" :icon="BanknotesIcon" />
      <SummaryCard label="Despesas" :value="16085.7" tone="negative" :icon="CreditCardIcon" />
      <SummaryCard label="Investimentos" :value="5500" tone="investment" :icon="ChartBarIcon" />
      <SummaryCard label="Restante" :value="1128.55" tone="neutral" :icon="BanknotesIcon" />
    </div>

    <div class="mt-6 grid grid-cols-1 gap-4 lg:grid-cols-2">
      <div class="rounded-card border border-neutral-200 bg-white p-4 shadow-card">
        <h2 class="mb-2 text-base font-semibold">Composição das Despesas</h2>
        <div class="flex flex-wrap items-center gap-6">
          <ChartDonut
            :labels="despesasComposition.items.map((item) => item.label)"
            :values="despesasComposition.items.map((item) => item.value)"
            :colors="despesasComposition.items.map((item) => item.color)"
            :center-value="money(despesasComposition.total)"
            center-label="Total"
          />
          <ul class="flex-1 space-y-2 text-sm">
            <li v-for="item in despesasComposition.items" :key="item.label" class="flex items-center gap-2">
              <span class="h-2.5 w-2.5 rounded-full" :style="{ backgroundColor: item.color }" />
              <span class="text-neutral-600">{{ item.label }}</span>
              <span class="ml-auto font-medium text-neutral-900">{{ money(item.value) }}</span>
              <span class="w-12 text-right text-neutral-500">{{ item.percent }}</span>
            </li>
          </ul>
        </div>
      </div>

      <div class="rounded-card border border-neutral-200 bg-white p-4 shadow-card">
        <h2 class="mb-2 text-base font-semibold">Receitas vs Despesas (últimos 6 meses)</h2>
        <ChartBars :labels="monthlyBars.labels" :series="monthlyBars.series" />
        <div class="mt-2 flex items-center justify-center gap-6 text-sm">
          <span v-for="serie in monthlyBars.series" :key="serie.label" class="flex items-center gap-2">
            <span class="h-2.5 w-2.5 rounded-full" :style="{ backgroundColor: serie.color }" />
            {{ serie.label }}
          </span>
        </div>
      </div>
    </div>

    <div class="mt-6 grid grid-cols-1 gap-4 lg:grid-cols-3">
      <div
        v-for="group in [
          { title: 'Contas a Receber', total: 17214.25, items: contasAReceber },
          { title: 'Contas a Pagar - Fixas', total: 1902.41, items: contasFixas },
          { title: 'Contas a Pagar - Variáveis', total: 8683.29, items: contasVariaveis },
        ]"
        :key="group.title"
        class="rounded-card border border-neutral-200 bg-white shadow-card"
      >
        <div class="flex items-center justify-between border-b border-neutral-100 px-4 py-3">
          <h2 class="text-sm font-semibold text-neutral-700">{{ group.title }}</h2>
          <p class="text-sm font-semibold text-neutral-900">{{ money(group.total) }}</p>
        </div>
        <ul class="divide-y divide-neutral-50 px-4">
          <li v-for="item in group.items" :key="item.description" class="flex items-center justify-between py-2 text-sm">
            <span class="text-neutral-600">{{ item.description }}</span>
            <span class="font-medium" :class="item.value === null ? 'text-neutral-300' : 'text-neutral-900'">
              {{ money(item.value) }}
            </span>
          </li>
        </ul>
      </div>
    </div>
  </section>
</template>
