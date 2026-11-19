<script setup>
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { BanknotesIcon, ChartBarIcon, CreditCardIcon, PlusIcon } from '@heroicons/vue/24/outline'

import BaseButton from '../components/BaseButton.vue'
import ChartBars from '../components/ChartBars.vue'
import ChartDonut from '../components/ChartDonut.vue'
import EmptyState from '../components/EmptyState.vue'
import LoadErrorState from '../components/LoadErrorState.vue'
import LoadingState from '../components/LoadingState.vue'
import MonthSelector from '../components/MonthSelector.vue'
import SectionHeader from '../components/SectionHeader.vue'
import SummaryCard from '../components/SummaryCard.vue'
import { api } from '../services/api'
import { formatCurrency } from '../utils/formatCurrency'
import { formatDate } from '../utils/formatDate'
import { chartPalette } from '../utils/navigation'

const router = useRouter()
const route = useRoute()

function initialPeriod() {
  const query = route.query.month
  if (typeof query === 'string' && /^\d{4}-\d{2}$/.test(query)) {
    const [year, month] = query.split('-').map(Number)
    return new Date(year, month - 1, 1)
  }
  return new Date()
}

const period = ref(initialPeriod())
const summary = ref(null)
const loading = ref(true)
const error = ref('')

const monthParam = computed(() => {
  const year = period.value.getFullYear()
  const month = String(period.value.getMonth() + 1).padStart(2, '0')
  return `${year}-${month}`
})

const totalExpenses = computed(() => {
  if (!summary.value) return 0
  // As faturas de cartão já estão incluídas em total_variable_expenses
  // (spec.md §7.2): Despesas = fixas + variáveis, sem dupla contagem.
  return Number(summary.value.total_fixed_expenses) + Number(summary.value.total_variable_expenses)
})

const donutData = computed(() => {
  if (!summary.value) return []
  const cardTotal = Number(summary.value.card_purchases_total)
  return [
    {
      label: 'Fixas',
      value: Number(summary.value.total_fixed_expenses),
      color: chartPalette.blue,
    },
    {
      label: 'Variáveis',
      value: Number(summary.value.total_variable_expenses) - cardTotal,
      color: chartPalette.orange,
    },
    {
      label: 'Cartões',
      value: cardTotal,
      color: chartPalette.purple,
    },
  ]
})

const barsData = computed(() => {
  if (!summary.value) return { labels: [], series: [] }
  const trend = summary.value.trend
  return {
    labels: trend.map((point) => {
      const [, month] = point.month.split('-')
      return ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'][
        Number(month) - 1
      ]
    }),
    series: [
      {
        label: 'Receitas',
        color: chartPalette.green,
        values: trend.map((point) => Number(point.income)),
      },
      {
        label: 'Despesas',
        color: chartPalette.red,
        values: trend.map((point) => Number(point.expenses)),
      },
    ],
  }
})

const groups = computed(() => {
  if (!summary.value) return []
  return [
    {
      title: 'Contas a Receber',
      total: summary.value.total_income,
      items: summary.value.income_items,
    },
    {
      title: 'Contas a Pagar - Fixas',
      total: summary.value.total_fixed_expenses,
      items: summary.value.fixed_expense_items,
    },
    {
      title: 'Contas a Pagar - Variáveis',
      total: summary.value.total_variable_expenses,
      items: summary.value.variable_expense_items,
    },
    {
      title: 'Investimentos',
      total: summary.value.total_investments,
      items: summary.value.investments_items,
    },
  ]
})

async function load() {
  loading.value = true
  error.value = ''
  try {
    summary.value = await api.get(`/dashboard/monthly?month=${monthParam.value}`)
  } catch (err) {
    // AC-080: erro visível com nova tentativa, nunca spinner eterno.
    error.value = err.message || 'Não foi possível carregar o resumo do mês.'
  } finally {
    loading.value = false
  }
}

// `immediate` dispara a carga inicial: sem ele, a página ficaria em
// carregamento eterno até o usuário trocar o mês.
watch(period, load, { immediate: true })
watch(
  () => route.query.month,
  () => {
    period.value = initialPeriod()
  },
)

function goAddMovement() {
  router.push({ name: 'movimentacoes', query: { novo: 1 } })
}
</script>

<template>
  <section>
    <SectionHeader
      title="Visão Mensal"
      description="Acompanhe suas receitas, despesas e saldo do mês."
    >
      <template #actions>
        <MonthSelector v-model="period" />
        <BaseButton @click="goAddMovement">
          <PlusIcon class="h-4 w-4" aria-hidden="true" />
          Nova Movimentação
        </BaseButton>
      </template>
    </SectionHeader>

    <LoadingState v-if="loading" />

    <LoadErrorState v-else-if="error" :message="error" @retry="load" />

    <template v-else-if="summary">
      <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <SummaryCard
          label="Receitas"
          :value="Number(summary.total_income)"
          tone="positive"
          :icon="BanknotesIcon"
        />
        <SummaryCard
          label="Despesas"
          :value="totalExpenses"
          tone="negative"
          :icon="CreditCardIcon"
        />
        <SummaryCard
          label="Investimentos"
          :value="Number(summary.total_investments)"
          tone="investment"
          :icon="ChartBarIcon"
        />
        <SummaryCard
          label="Restante"
          :value="Number(summary.remaining)"
          tone="neutral"
          :icon="BanknotesIcon"
          hint="Receitas − saídas do período"
        />
      </div>

      <div class="mt-6 grid grid-cols-1 gap-4 lg:grid-cols-2">
        <div class="rounded-card border border-neutral-200 bg-white p-4 shadow-card">
          <h2 class="mb-2 text-base font-semibold">Composição das Despesas</h2>
          <div class="flex flex-wrap items-center gap-6">
            <ChartDonut
              :labels="donutData.map((item) => item.label)"
              :values="donutData.map((item) => item.value)"
              :colors="donutData.map((item) => item.color)"
              :center-value="formatCurrency(totalExpenses)"
              center-label="Total"
            />
            <ul class="flex-1 space-y-2 text-sm">
              <li v-for="item in donutData" :key="item.label" class="flex items-center gap-2">
                <span class="h-2.5 w-2.5 rounded-full" :style="{ backgroundColor: item.color }" />
                <span class="text-neutral-600">{{ item.label }}</span>
                <span class="ml-auto font-medium text-neutral-900">
                  {{ formatCurrency(item.value) }}
                </span>
              </li>
            </ul>
          </div>
        </div>

        <div class="rounded-card border border-neutral-200 bg-white p-4 shadow-card">
          <h2 class="mb-2 text-base font-semibold">Receitas vs Despesas (últimos 6 meses)</h2>
          <ChartBars :labels="barsData.labels" :series="barsData.series" />
          <div class="mt-2 flex items-center justify-center gap-6 text-sm">
            <span
              v-for="serie in barsData.series"
              :key="serie.label"
              class="flex items-center gap-2"
            >
              <span class="h-2.5 w-2.5 rounded-full" :style="{ backgroundColor: serie.color }" />
              {{ serie.label }}
            </span>
          </div>
        </div>
      </div>

      <div class="mt-6 grid grid-cols-1 gap-4 lg:grid-cols-2 xl:grid-cols-4">
        <div
          v-for="group in groups"
          :key="group.title"
          class="rounded-card border border-neutral-200 bg-white shadow-card"
        >
          <div class="flex items-center justify-between border-b border-neutral-100 px-4 py-3">
            <h2 class="text-sm font-semibold text-neutral-700">{{ group.title }}</h2>
            <p class="text-sm font-semibold text-neutral-900">
              {{ formatCurrency(Number(group.total)) }}
            </p>
          </div>
          <ul v-if="group.items.length" class="divide-y divide-neutral-50 px-4">
            <li
              v-for="item in group.items"
              :key="item.name"
              class="flex items-center justify-between py-2 text-sm"
            >
              <span class="text-neutral-600">{{ item.name }}</span>
              <span class="font-medium text-neutral-900">
                {{ formatCurrency(Number(item.total)) }}
              </span>
            </li>
          </ul>
          <p v-else class="px-4 py-6 text-center text-sm text-neutral-400">
            Nenhum lançamento no período.
          </p>
        </div>
      </div>

      <h2 class="mb-3 mt-8 text-lg">Últimas movimentações</h2>

      <EmptyState
        v-if="summary.recent_transactions.length === 0"
        title="Nenhuma movimentação registrada"
        description="As movimentações lançadas no período aparecerão aqui."
      >
        <template #actions>
          <BaseButton size="sm" @click="goAddMovement">Nova Movimentação</BaseButton>
        </template>
      </EmptyState>

      <ul
        v-else
        class="divide-y divide-neutral-100 rounded-card border border-neutral-200 bg-white shadow-card"
      >
        <li
          v-for="movement in summary.recent_transactions"
          :key="movement.id"
          class="flex items-center justify-between px-4 py-3 text-sm"
        >
          <div>
            <p class="font-medium text-neutral-900">{{ movement.description }}</p>
            <p class="text-xs text-neutral-400">{{ formatDate(movement.transaction_date) }}</p>
          </div>
          <p
            class="font-semibold tabular-nums"
            :class="movement.type === 'income' ? 'text-positive' : 'text-negative'"
          >
            {{ movement.type === 'income' ? '+' : '−' }}
            {{ formatCurrency(Number(movement.amount)) }}
          </p>
        </li>
      </ul>
    </template>
  </section>
</template>
