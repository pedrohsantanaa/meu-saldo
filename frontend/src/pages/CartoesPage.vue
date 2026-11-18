<script setup>
import { ref } from 'vue'
import {
  BanknotesIcon,
  CreditCardIcon,
  PencilSquareIcon,
  PlusIcon,
  ShoppingCartIcon,
  TrashIcon,
} from '@heroicons/vue/24/outline'

import BaseBadge from '../components/BaseBadge.vue'
import BaseButton from '../components/BaseButton.vue'
import BaseTabs from '../components/BaseTabs.vue'
import MonthSelector from '../components/MonthSelector.vue'
import ProgressBar from '../components/ProgressBar.vue'
import SectionHeader from '../components/SectionHeader.vue'
import SummaryCard from '../components/SummaryCard.vue'
import { formatCurrency } from '../utils/formatCurrency'

const period = ref(new Date(2026, 10, 1))
const activeTab = ref('compras')

const cards = [
  { id: 'nubank', name: 'Nubank', suffix: '1234', gradient: 'from-purple-500 to-purple-700' },
  { id: 'bb', name: 'Banco do Brasil', suffix: '5678', gradient: 'from-blue-500 to-blue-700' },
  { id: 'inter', name: 'Inter', suffix: '9012', gradient: 'from-orange-400 to-orange-600' },
]

const selectedCard = ref('bb')

const purchases = [
  { date: '14/11/2026', description: 'Abdu + Mercado + Brinjo', category: 'Lanche', value: 385.26 },
  { date: '12/11/2026', description: 'Ifood Almoço', category: 'Lanche', value: 58.88 },
  { date: '07/11/2026', description: 'Supermercado Carne', category: 'Lanche', value: 156.27 },
]

const tabs = [
  { value: 'compras', label: 'Compras' },
  { value: 'orcamento', label: 'Orçamento por Categoria' },
  { value: 'faturas', label: 'Faturas' },
]
</script>

<template>
  <section>
    <SectionHeader title="Cartões" description="Gerencie seus cartões, compras e faturas.">
      <template #actions>
        <BaseButton>
          <PlusIcon class="h-4 w-4" aria-hidden="true" />
          Novo Cartão
        </BaseButton>
      </template>
    </SectionHeader>

    <div class="grid grid-cols-1 gap-4 lg:grid-cols-3">
      <div class="space-y-3">
        <button
          v-for="card in cards"
          :key="card.id"
          type="button"
          class="w-full rounded-card bg-gradient-to-r p-4 text-left text-white shadow-card transition-transform"
          :class="[card.gradient, selectedCard === card.id ? 'ring-2 ring-primary ring-offset-2' : '']"
          @click="selectedCard = card.id"
        >
          <p class="flex items-center gap-2 font-semibold">
            <CreditCardIcon class="h-5 w-5" aria-hidden="true" />
            {{ card.name }}
          </p>
          <p class="mt-2 text-sm text-white/80">•••• {{ card.suffix }}</p>
        </button>

        <button
          type="button"
          class="flex w-full items-center justify-center gap-2 rounded-card border border-dashed border-neutral-300 bg-white p-3 text-sm text-neutral-500 hover:border-primary hover:text-primary"
        >
          <PlusIcon class="h-4 w-4" aria-hidden="true" />
          Adicionar cartão
        </button>
      </div>

      <div class="lg:col-span-2">
        <div class="rounded-card border border-neutral-200 bg-white p-4 shadow-card">
          <div class="flex flex-wrap items-center justify-between gap-3">
            <div class="flex items-center gap-3">
              <span class="flex h-10 w-10 items-center justify-center rounded-full bg-attention-light text-attention">
                <CreditCardIcon class="h-5 w-5" aria-hidden="true" />
              </span>
              <div>
                <h2 class="font-semibold text-neutral-900">Cartão Banco do Brasil</h2>
                <p class="text-sm text-neutral-500">Final 5678</p>
              </div>
            </div>
            <MonthSelector v-model="period" />
          </div>

          <div class="mt-4 grid grid-cols-1 gap-3 sm:grid-cols-3">
            <SummaryCard label="Orçamento" :value="5500" tone="positive" :icon="BanknotesIcon" />
            <SummaryCard label="Gastos" :value="4873.41" tone="negative" :icon="ShoppingCartIcon" />
            <SummaryCard label="Restante" :value="626.59" tone="neutral" :icon="BanknotesIcon" />
          </div>

          <div class="mt-4">
            <ProgressBar :value="4873.41" :max="5500" />
          </div>

          <div class="mt-6">
            <BaseTabs v-model="activeTab" :items="tabs" />

            <div v-if="activeTab === 'compras'" class="mt-4 overflow-x-auto">
              <table class="w-full min-w-[36rem] text-left text-sm">
                <thead class="border-b border-neutral-200 text-xs uppercase text-neutral-500">
                  <tr>
                    <th class="px-3 py-2">Data</th>
                    <th class="px-3 py-2">Descrição</th>
                    <th class="px-3 py-2">Categoria</th>
                    <th class="px-3 py-2 text-right">Valor</th>
                    <th class="px-3 py-2 text-right">Ações</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-neutral-100">
                  <tr v-for="purchase in purchases" :key="`${purchase.date}-${purchase.description}`">
                    <td class="px-3 py-2 text-neutral-600">{{ purchase.date }}</td>
                    <td class="px-3 py-2 font-medium text-neutral-900">{{ purchase.description }}</td>
                    <td class="px-3 py-2">
                      <BaseBadge variant="variable">{{ purchase.category }}</BaseBadge>
                    </td>
                    <td class="px-3 py-2 text-right font-semibold tabular-nums">
                      {{ formatCurrency(purchase.value) }}
                    </td>
                    <td class="px-3 py-2">
                      <div class="flex items-center justify-end gap-2">
                        <button type="button" class="text-primary hover:text-primary-dark" aria-label="Editar">
                          <PencilSquareIcon class="h-4 w-4" />
                        </button>
                        <button type="button" class="text-negative hover:text-negative/80" aria-label="Excluir">
                          <TrashIcon class="h-4 w-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>

            <p
              v-else
              class="mt-4 rounded-card border border-dashed border-neutral-200 p-6 text-center text-sm text-neutral-500"
            >
              Conteúdo de "{{ tabs.find((tab) => tab.value === activeTab)?.label }}" será implementado
              nas próximas fases.
            </p>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>
