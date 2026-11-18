<script setup>
import { computed, onMounted, ref } from 'vue'
import {
  CheckIcon,
  PencilSquareIcon,
  PlusIcon,
  PowerIcon,
} from '@heroicons/vue/24/outline'

import BaseBadge from '../components/BaseBadge.vue'
import BaseButton from '../components/BaseButton.vue'
import BaseInput from '../components/BaseInput.vue'
import BaseModal from '../components/BaseModal.vue'
import BaseSelect from '../components/BaseSelect.vue'
import BaseTabs from '../components/BaseTabs.vue'
import ConfirmDialog from '../components/ConfirmDialog.vue'
import EmptyState from '../components/EmptyState.vue'
import LoadingState from '../components/LoadingState.vue'
import SectionHeader from '../components/SectionHeader.vue'
import { api } from '../services/api'

const categories = ref([])
const loading = ref(true)
const filter = ref('todas')

const modalOpen = ref(false)
const editing = ref(null)
const saving = ref(false)
const formError = ref('')
const confirmTarget = ref(null)

const form = ref({ name: '', group_type: 'expense', expense_type: 'variable' })

const groupLabels = {
  income: 'Receita',
  expense: 'Despesa',
  investment: 'Investimento',
}

const badgeVariants = {
  income: 'income',
  investment: 'investment',
}

const groupOptions = [
  { value: 'income', label: 'Receita' },
  { value: 'expense', label: 'Despesa' },
  { value: 'investment', label: 'Investimento' },
]

const expenseTypeOptions = [
  { value: 'fixed', label: 'Fixa' },
  { value: 'variable', label: 'Variável' },
]

const filters = computed(() => [
  { value: 'todas', label: `Todas (${categories.value.length})` },
  { value: 'income', label: `Receitas (${countBy('income')})` },
  { value: 'fixed', label: `Despesas Fixas (${countBy('fixed')})` },
  { value: 'variable', label: `Despesas Variáveis (${countBy('variable')})` },
  { value: 'investment', label: `Investimentos (${countBy('investment')})` },
])

const filtered = computed(() => {
  if (filter.value === 'todas') return categories.value
  if (filter.value === 'income' || filter.value === 'investment') {
    return categories.value.filter((item) => item.group_type === filter.value)
  }
  return categories.value.filter((item) => item.expense_type === filter.value)
})

function countBy(key) {
  return categories.value.filter(
    (item) => item.group_type === key || item.expense_type === key
  ).length
}

function typeLabel(item) {
  return item.group_type === 'expense'
    ? `Despesa ${item.expense_type === 'fixed' ? 'Fixa' : 'Variável'}`
    : groupLabels[item.group_type]
}

function badgeVariant(item) {
  if (item.group_type === 'expense') return item.expense_type
  return badgeVariants[item.group_type]
}

async function load() {
  loading.value = true
  categories.value = await api.get('/categories')
  loading.value = false
}

function openCreate() {
  editing.value = null
  form.value = { name: '', group_type: 'expense', expense_type: 'variable' }
  formError.value = ''
  modalOpen.value = true
}

function openEdit(category) {
  editing.value = category
  form.value = {
    name: category.name,
    group_type: category.group_type,
    expense_type: category.expense_type ?? 'variable',
  }
  formError.value = ''
  modalOpen.value = true
}

async function onSave() {
  saving.value = true
  formError.value = ''
  const payload = {
    name: form.value.name,
    group_type: form.value.group_type,
    expense_type: form.value.group_type === 'expense' ? form.value.expense_type : null,
  }
  try {
    if (editing.value) {
      await api.put(`/categories/${editing.value.id}`, payload)
    } else {
      await api.post('/categories', payload)
    }
    modalOpen.value = false
    await load()
  } catch (err) {
    formError.value = err.message || 'Não foi possível salvar a categoria.'
  } finally {
    saving.value = false
  }
}

async function onToggleActive(category) {
  await api.patch(`/categories/${category.id}/status`, {
    is_active: !category.is_active,
  })
  await load()
}

async function onConfirmDeactivate() {
  await api.patch(`/categories/${confirmTarget.value.id}/status`, { is_active: false })
  confirmTarget.value = null
  await load()
}

onMounted(load)
</script>

<template>
  <section>
    <SectionHeader
      title="Categorias"
      description="Organize as categorias das suas receitas e despesas."
    >
      <template #actions>
        <BaseButton @click="openCreate">
          <PlusIcon class="h-4 w-4" aria-hidden="true" />
          Nova Categoria
        </BaseButton>
      </template>
    </SectionHeader>

    <LoadingState v-if="loading" />

    <template v-else>
      <div class="mb-4">
        <BaseTabs v-model="filter" :items="filters" variant="pills" />
      </div>

      <EmptyState
        v-if="filtered.length === 0"
        title="Nenhuma categoria encontrada"
        description="Crie uma categoria ou ajuste os filtros."
      />

      <div
        v-else
        class="overflow-x-auto rounded-card border border-neutral-200 bg-white shadow-card"
      >
        <table class="w-full min-w-[36rem] text-left text-sm">
          <thead class="border-b border-neutral-200 bg-neutral-50 text-xs uppercase text-neutral-500">
            <tr>
              <th class="px-4 py-3">Categoria</th>
              <th class="px-4 py-3">Tipo</th>
              <th class="px-4 py-3">Situação</th>
              <th class="px-4 py-3 text-right">Ações</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-neutral-100">
            <tr
              v-for="category in filtered"
              :key="category.id"
              :class="category.is_active ? '' : 'opacity-60'"
            >
              <td class="px-4 py-3 font-medium text-neutral-900">
                {{ category.name }}
                <span v-if="category.is_default" class="ml-1 text-xs text-neutral-400">
                  (padrão)
                </span>
              </td>
              <td class="px-4 py-3">
                <BaseBadge :variant="badgeVariant(category)">{{ typeLabel(category) }}</BaseBadge>
              </td>
              <td class="px-4 py-3 text-neutral-600">
                {{ category.is_active ? 'Ativa' : 'Inativa' }}
              </td>
              <td class="px-4 py-3">
                <div class="flex items-center justify-end gap-2">
                  <button
                    type="button"
                    class="text-primary hover:text-primary-dark"
                    aria-label="Editar"
                    @click="openEdit(category)"
                  >
                    <PencilSquareIcon class="h-4 w-4" />
                  </button>

                  <button
                    v-if="category.is_active"
                    type="button"
                    class="text-negative hover:text-negative/80"
                    aria-label="Desativar"
                    @click="confirmTarget = category"
                  >
                    <PowerIcon class="h-4 w-4" />
                  </button>
                  <button
                    v-else
                    type="button"
                    class="text-positive hover:text-positive/80"
                    aria-label="Reativar"
                    @click="onToggleActive(category)"
                  >
                    <CheckIcon class="h-4 w-4" />
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </template>

    <BaseModal
      :open="modalOpen"
      :title="editing ? 'Editar categoria' : 'Nova categoria'"
      @update:open="modalOpen = $event"
    >
      <form class="space-y-4" @submit.prevent="onSave">
        <BaseInput v-model="form.name" label="Nome" placeholder="Ex.: Alimentação" required />

        <BaseSelect v-model="form.group_type" label="Grupo" :options="groupOptions" />

        <BaseSelect
          v-if="form.group_type === 'expense'"
          v-model="form.expense_type"
          label="Classificação"
          :options="expenseTypeOptions"
        />

        <p
          v-if="formError"
          role="alert"
          class="rounded-md bg-negative-light px-3 py-2 text-sm text-negative"
        >
          {{ formError }}
        </p>
      </form>

      <template #footer>
        <BaseButton variant="secondary" @click="modalOpen = false">Cancelar</BaseButton>
        <BaseButton :loading="saving" @click="onSave">Salvar</BaseButton>
      </template>
    </BaseModal>

    <ConfirmDialog
      :open="Boolean(confirmTarget)"
      title="Desativar categoria"
      :message="`Deseja desativar a categoria &quot;${confirmTarget?.name}&quot;? Ela poderá ser reativada depois e o histórico é preservado.`"
      confirm-label="Desativar"
      @update:open="confirmTarget = null"
      @confirm="onConfirmDeactivate"
    />
  </section>
</template>
