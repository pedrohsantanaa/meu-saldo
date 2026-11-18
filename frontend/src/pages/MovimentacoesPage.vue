<script setup>
import { ref } from 'vue'
import {
  ArrowDownTrayIcon,
  MagnifyingGlassIcon,
  PencilSquareIcon,
  PlusIcon,
  TrashIcon,
} from '@heroicons/vue/24/outline'

import BaseBadge from '../components/BaseBadge.vue'
import BaseButton from '../components/BaseButton.vue'
import BaseInput from '../components/BaseInput.vue'
import BaseSelect from '../components/BaseSelect.vue'
import MonthSelector from '../components/MonthSelector.vue'
import SectionHeader from '../components/SectionHeader.vue'
import { formatCurrency } from '../utils/formatCurrency'

const period = ref(new Date(2026, 10, 1))
const search = ref('')

const movements = [
  { date: '15/11/2026', description: 'Supermercado', category: 'Lanche', type: 'Despesa', value: 385.26 },
  { date: '13/11/2026', description: 'Ifood Almoço', category: 'Lanche', type: 'Despesa', value: 28.87 },
  { date: '05/11/2026', description: 'Gasto Diversos', category: 'Lanche', type: 'Despesa', value: 100.16 },
  { date: '03/11/2026', description: 'Barbeiro', category: 'Barbeiro', type: 'Despesa', value: 150.0 },
  { date: '01/11/2026', description: 'Salário IF', category: 'Salário', type: 'Receita', value: 7175.09 },
]
</script>

<template>
  <section>
    <SectionHeader title="Movimentações" description="Gerencie suas receitas e despesas.">
      <template #actions>
        <BaseButton variant="secondary">
          <ArrowDownTrayIcon class="h-4 w-4" aria-hidden="true" />
          Exportar
        </BaseButton>
        <BaseButton>
          <PlusIcon class="h-4 w-4" aria-hidden="true" />
          Nova Movimentação
        </BaseButton>
      </template>
    </SectionHeader>

    <div class="mb-4 flex flex-wrap items-center gap-3">
      <MonthSelector v-model="period" />

      <BaseSelect
        :model-value="'todos'"
        :options="[
          { value: 'todos', label: 'Todos os tipos' },
          { value: 'receita', label: 'Receita' },
          { value: 'despesa', label: 'Despesa' },
        ]"
        class="w-44"
        aria-label="Filtrar por tipo"
      />

      <BaseSelect
        :model-value="'todas'"
        :options="[
          { value: 'todas', label: 'Todas as categorias' },
          { value: 'lanche', label: 'Lanche' },
          { value: 'salario', label: 'Salário' },
        ]"
        class="w-48"
        aria-label="Filtrar por categoria"
      />

      <div class="relative flex-1 sm:min-w-[14rem]">
        <MagnifyingGlassIcon
          class="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-neutral-400"
          aria-hidden="true"
        />
        <BaseInput
          v-model="search"
          placeholder="Buscar lançamento..."
          aria-label="Buscar lançamento"
          class="[&_input]:pl-9"
        />
      </div>
    </div>

    <div class="overflow-x-auto rounded-card border border-neutral-200 bg-white shadow-card">
      <table class="w-full min-w-[40rem] text-left text-sm">
        <thead class="border-b border-neutral-200 bg-neutral-50 text-xs uppercase text-neutral-500">
          <tr>
            <th class="px-4 py-3">Data</th>
            <th class="px-4 py-3">Descrição</th>
            <th class="px-4 py-3">Categoria</th>
            <th class="px-4 py-3">Tipo</th>
            <th class="px-4 py-3 text-right">Valor</th>
            <th class="px-4 py-3 text-right">Ações</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-neutral-100">
          <tr v-for="movement in movements" :key="`${movement.date}-${movement.description}`">
            <td class="px-4 py-3 text-neutral-600">{{ movement.date }}</td>
            <td class="px-4 py-3 font-medium text-neutral-900">{{ movement.description }}</td>
            <td class="px-4 py-3 text-neutral-600">{{ movement.category }}</td>
            <td class="px-4 py-3">
              <BaseBadge :variant="movement.type === 'Receita' ? 'income' : 'expense'">
                {{ movement.type }}
              </BaseBadge>
            </td>
            <td class="px-4 py-3 text-right font-semibold tabular-nums">
              {{ formatCurrency(movement.value) }}
            </td>
            <td class="px-4 py-3">
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
  </section>
</template>
