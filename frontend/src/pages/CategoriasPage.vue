<script setup>
import { computed, ref } from 'vue'
import { PencilSquareIcon, PlusIcon, TrashIcon } from '@heroicons/vue/24/outline'

import BaseBadge from '../components/BaseBadge.vue'
import BaseButton from '../components/BaseButton.vue'
import BaseTabs from '../components/BaseTabs.vue'
import SectionHeader from '../components/SectionHeader.vue'

const filter = ref('todas')

const categories = [
  { name: 'Salário', type: 'Receita', variant: 'income', description: 'Receita de salário (Senac, IF, Fasec etc.)' },
  { name: 'Aluguel', type: 'Despesa Fixa', variant: 'fixed', description: 'Pagamento de aluguel' },
  { name: 'Água e Energia', type: 'Despesa Fixa', variant: 'fixed', description: 'Contas de água, energia e serviços básicos' },
  { name: 'Lanche', type: 'Despesa Variável', variant: 'variable', description: 'Alimentação, lanches e refeições' },
  { name: 'Investimento', type: 'Investimento', variant: 'investment', description: 'Poupança, reserva e aplicações' },
]

const filters = computed(() => [
  { value: 'todas', label: `Todas (${categories.length})` },
  { value: 'Receita', label: `Receitas (${categories.filter((item) => item.type === 'Receita').length})` },
  { value: 'Despesa Fixa', label: `Despesas Fixas (${categories.filter((item) => item.type === 'Despesa Fixa').length})` },
  { value: 'Despesa Variável', label: `Despesas Variáveis (${categories.filter((item) => item.type === 'Despesa Variável').length})` },
  { value: 'Investimento', label: `Investimentos (${categories.filter((item) => item.type === 'Investimento').length})` },
])

const filtered = computed(() =>
  filter.value === 'todas' ? categories : categories.filter((item) => item.type === filter.value)
)
</script>

<template>
  <section>
    <SectionHeader title="Categorias" description="Organize as categorias das suas receitas e despesas.">
      <template #actions>
        <BaseButton>
          <PlusIcon class="h-4 w-4" aria-hidden="true" />
          Nova Categoria
        </BaseButton>
      </template>
    </SectionHeader>

    <div class="mb-4">
      <BaseTabs v-model="filter" :items="filters" variant="pills" />
    </div>

    <div class="overflow-x-auto rounded-card border border-neutral-200 bg-white shadow-card">
      <table class="w-full min-w-[40rem] text-left text-sm">
        <thead class="border-b border-neutral-200 bg-neutral-50 text-xs uppercase text-neutral-500">
          <tr>
            <th class="px-4 py-3">Categoria</th>
            <th class="px-4 py-3">Tipo</th>
            <th class="px-4 py-3">Descrição</th>
            <th class="px-4 py-3 text-right">Ações</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-neutral-100">
          <tr v-for="category in filtered" :key="category.name">
            <td class="px-4 py-3 font-medium text-neutral-900">{{ category.name }}</td>
            <td class="px-4 py-3">
              <BaseBadge :variant="category.variant">{{ category.type }}</BaseBadge>
            </td>
            <td class="px-4 py-3 text-neutral-600">{{ category.description }}</td>
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
