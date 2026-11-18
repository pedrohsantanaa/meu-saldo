<script setup>
import { ref } from 'vue'
import { CreditCardIcon, PlusIcon } from '@heroicons/vue/24/outline'

import BaseButton from '../components/BaseButton.vue'
import BaseSelect from '../components/BaseSelect.vue'
import MonthSelector from '../components/MonthSelector.vue'
import ProgressBar from '../components/ProgressBar.vue'
import SectionHeader from '../components/SectionHeader.vue'
import { formatCurrency } from '../utils/formatCurrency'

const period = ref(new Date(2026, 11, 1))
const card = ref('bb')

const cardOptions = [
  { value: 'bb', label: 'Cartão Banco do Brasil' },
  { value: 'nubank', label: 'Cartão Nubank' },
  { value: 'inter', label: 'Cartão Inter' },
]

const budgets = [
  { category: 'Gasolina', budget: 0, spent: 0 },
  { category: 'Lanche', budget: 3050, spent: 3070.06 },
  { category: 'Barbeiro', budget: 300, spent: 150 },
  { category: 'Academia', budget: 149.99, spent: 0 },
  { category: 'Google Drive + Youtube', budget: 123.89, spent: 0 },
  { category: 'Spotify', budget: 23.9, spent: 0 },
]

function remainder(row) {
  return row.budget - row.spent
}
</script>

<template>
  <section>
    <SectionHeader
      title="Orçamentos"
      description="Defina o orçamento por categoria em cada cartão e acompanhe os gastos do mês."
    >
      <template #actions>
        <BaseButton>
          <PlusIcon class="h-4 w-4" aria-hidden="true" />
          Novo Orçamento
        </BaseButton>
      </template>
    </SectionHeader>

    <div class="mb-4 flex flex-wrap items-center gap-3">
      <MonthSelector v-model="period" />

      <div class="flex items-center gap-2">
        <span class="flex h-8 w-8 items-center justify-center rounded-full bg-attention-light text-attention">
          <CreditCardIcon class="h-4 w-4" aria-hidden="true" />
        </span>
        <BaseSelect v-model="card" :options="cardOptions" class="w-56" aria-label="Selecionar cartão" />
      </div>
    </div>

    <div class="overflow-x-auto rounded-card border border-neutral-200 bg-white shadow-card">
      <table class="w-full min-w-[44rem] text-left text-sm">
        <thead class="border-b border-neutral-200 bg-neutral-50 text-xs uppercase text-neutral-500">
          <tr>
            <th class="px-4 py-3">Categoria</th>
            <th class="px-4 py-3 text-right">Orçamento</th>
            <th class="px-4 py-3 text-right">Gastos</th>
            <th class="px-4 py-3 text-right">Restante</th>
            <th class="px-4 py-3">Uso</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-neutral-100">
          <tr v-for="row in budgets" :key="row.category">
            <td class="px-4 py-3 font-medium text-neutral-900">{{ row.category }}</td>
            <td class="px-4 py-3 text-right tabular-nums">{{ formatCurrency(row.budget) }}</td>
            <td class="px-4 py-3 text-right tabular-nums">{{ formatCurrency(row.spent) }}</td>
            <td
              class="px-4 py-3 text-right font-semibold tabular-nums"
              :class="remainder(row) < 0 ? 'text-negative' : 'text-neutral-900'"
            >
              {{ formatCurrency(remainder(row)) }}
            </td>
            <td class="px-4 py-3">
              <div class="flex items-center gap-3">
                <ProgressBar :value="row.spent" :max="row.budget || 1" :show-label="false" class="flex-1" />
                <span class="w-10 text-right text-xs text-neutral-500">
                  {{ row.budget ? `${Math.round((row.spent / row.budget) * 100)}%` : '0%' }}
                </span>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>
</template>
