<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
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
import BaseModal from '../components/BaseModal.vue'
import BaseSelect from '../components/BaseSelect.vue'
import ConfirmDialog from '../components/ConfirmDialog.vue'
import EmptyState from '../components/EmptyState.vue'
import LoadingState from '../components/LoadingState.vue'
import MonthSelector from '../components/MonthSelector.vue'
import SectionHeader from '../components/SectionHeader.vue'
import TransactionForm from '../components/TransactionForm.vue'
import { api } from '../services/api'
import { formatCurrency } from '../utils/formatCurrency'
import { formatDate } from '../utils/formatDate'

const period = ref(new Date())
const search = ref('')
const typeFilter = ref('')
const categoryFilter = ref('')
const paymentFilter = ref('')
const route = useRoute()

const movements = ref([])
const categories = ref([])
const loading = ref(true)

const modalOpen = ref(false)
const editing = ref(null)
const saving = ref(false)
const formError = ref('')
const confirmTarget = ref(null)

const typeOptions = [
  { value: 'income', label: 'Receita' },
  { value: 'expense', label: 'Despesa' },
  { value: 'investment', label: 'Investimento' },
]

const paymentOptions = [
  { value: 'dinheiro', label: 'Dinheiro' },
  { value: 'pix', label: 'Pix' },
  { value: 'debito', label: 'Débito' },
  { value: 'outra', label: 'Outra' },
]

const categoryOptions = computed(() =>
  categories.value.map((category) => ({
    value: String(category.id),
    label: category.name,
  })),
)

const monthBounds = computed(() => {
  const year = period.value.getFullYear()
  const month = period.value.getMonth()
  const lastDay = new Date(year, month + 1, 0).getDate()
  const pad = (value) => String(value).padStart(2, '0')
  return {
    date_from: `${year}-${pad(month + 1)}-01`,
    date_to: `${year}-${pad(month + 1)}-${pad(lastDay)}`,
  }
})

function categoryName(id) {
  return categories.value.find((category) => category.id === id)?.name ?? '—'
}

function badgeVariant(movement) {
  if (movement.type === 'income') return 'income'
  if (movement.type === 'investment') return 'investment'
  return movement.expense_type
}

function typeLabel(movement) {
  if (movement.type === 'income') return 'Receita'
  if (movement.type === 'investment') return 'Investimento'
  return movement.expense_type === 'fixed' ? 'Despesa Fixa' : 'Despesa Variável'
}

function detailLabel(movement) {
  const parts = []
  if (movement.type === 'expense') {
    parts.push(movement.expense_type === 'fixed' ? 'Fixa' : 'Variável')
    if (movement.payment_method) {
      parts.push(paymentOptions.find((p) => p.value === movement.payment_method)?.label)
    }
  }
  return parts.filter(Boolean).join(' · ')
}

async function load() {
  loading.value = true
  const params = new URLSearchParams(monthBounds.value)
  if (typeFilter.value) params.set('type', typeFilter.value)
  if (categoryFilter.value) params.set('category_id', categoryFilter.value)
  if (paymentFilter.value) params.set('payment_method', paymentFilter.value)
  if (search.value) params.set('search', search.value)

  movements.value = await api.get(`/transactions?${params.toString()}`)
  loading.value = false
}

watch([period, typeFilter, categoryFilter, paymentFilter], load)
watch(search, load)

function openCreate() {
  editing.value = null
  formError.value = ''
  modalOpen.value = true
}

function openEdit(movement) {
  editing.value = movement
  formError.value = ''
  modalOpen.value = true
}

async function onSave(payload) {
  saving.value = true
  formError.value = ''
  try {
    if (editing.value) {
      await api.put(`/transactions/${editing.value.id}`, payload)
    } else {
      await api.post('/transactions', payload)
    }
    modalOpen.value = false
    await load()
  } catch (err) {
    formError.value = err.message || 'Não foi possível salvar a movimentação.'
  } finally {
    saving.value = false
  }
}

async function onConfirmDelete() {
  await api.delete(`/transactions/${confirmTarget.value.id}`)
  confirmTarget.value = null
  await load()
}

onMounted(async () => {
  categories.value = await api.get('/categories')
  await load()
  if (route.query.novo) {
    openCreate()
  }
})
</script>

<template>
  <section>
    <SectionHeader title="Movimentações" description="Gerencie suas receitas e despesas.">
      <template #actions>
        <BaseButton variant="secondary">
          <ArrowDownTrayIcon class="h-4 w-4" aria-hidden="true" />
          Exportar
        </BaseButton>
        <BaseButton @click="openCreate">
          <PlusIcon class="h-4 w-4" aria-hidden="true" />
          Nova Movimentação
        </BaseButton>
      </template>
    </SectionHeader>

    <div class="mb-4 flex flex-wrap items-center gap-3">
      <MonthSelector v-model="period" />

      <BaseSelect
        v-model="typeFilter"
        :options="typeOptions"
        class="w-44"
        aria-label="Filtrar por tipo"
        placeholder="Todos os tipos"
      />

      <BaseSelect
        v-model="categoryFilter"
        :options="categoryOptions"
        class="w-48"
        aria-label="Filtrar por categoria"
        placeholder="Todas as categorias"
      />

      <BaseSelect
        v-model="paymentFilter"
        :options="paymentOptions"
        class="w-44"
        aria-label="Filtrar por forma de pagamento"
        placeholder="Forma de pagamento"
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

    <LoadingState v-if="loading" />

    <EmptyState
      v-else-if="movements.length === 0"
      title="Nenhuma movimentação encontrada"
      description="Registre uma movimentação ou ajuste os filtros."
    >
      <template #actions>
        <BaseButton size="sm" @click="openCreate">Nova Movimentação</BaseButton>
      </template>
    </EmptyState>

    <div v-else class="overflow-x-auto rounded-card border border-neutral-200 bg-white shadow-card">
      <table class="w-full min-w-[44rem] text-left text-sm">
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
          <tr v-for="movement in movements" :key="movement.id">
            <td class="px-4 py-3 text-neutral-600">{{ formatDate(movement.transaction_date) }}</td>
            <td class="px-4 py-3">
              <p class="font-medium text-neutral-900">{{ movement.description }}</p>
              <p v-if="detailLabel(movement)" class="text-xs text-neutral-400">
                {{ detailLabel(movement) }}
              </p>
            </td>
            <td class="px-4 py-3 text-neutral-600">{{ categoryName(movement.category_id) }}</td>
            <td class="px-4 py-3">
              <BaseBadge :variant="badgeVariant(movement)">{{ typeLabel(movement) }}</BaseBadge>
            </td>
            <td class="px-4 py-3 text-right font-semibold tabular-nums">
              {{ formatCurrency(movement.amount) }}
            </td>
            <td class="px-4 py-3">
              <div class="flex items-center justify-end gap-2">
                <button
                  type="button"
                  class="text-primary hover:text-primary-dark"
                  aria-label="Editar"
                  @click="openEdit(movement)"
                >
                  <PencilSquareIcon class="h-4 w-4" />
                </button>
                <button
                  type="button"
                  class="text-negative hover:text-negative/80"
                  aria-label="Excluir"
                  @click="confirmTarget = movement"
                >
                  <TrashIcon class="h-4 w-4" />
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <BaseModal
      :open="modalOpen"
      :title="editing ? 'Editar movimentação' : 'Nova movimentação'"
      @update:open="modalOpen = $event"
    >
      <TransactionForm
        :categories="categories"
        :initial="editing"
        :loading="saving"
        :error="formError"
        @submit="onSave"
        @cancel="modalOpen = false"
      />
    </BaseModal>

    <ConfirmDialog
      :open="Boolean(confirmTarget)"
      title="Excluir movimentação"
      :message="`Deseja excluir &quot;${confirmTarget?.description}&quot;? Esta ação não pode ser desfeita.`"
      confirm-label="Excluir"
      @update:open="confirmTarget = null"
      @confirm="onConfirmDelete"
    />
  </section>
</template>
