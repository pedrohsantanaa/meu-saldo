<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { PencilSquareIcon, PlusIcon, ShoppingCartIcon, TrashIcon } from '@heroicons/vue/24/outline'

import BaseBadge from './BaseBadge.vue'
import BaseButton from './BaseButton.vue'
import BaseModal from './BaseModal.vue'
import BaseSelect from './BaseSelect.vue'
import ConfirmDialog from './ConfirmDialog.vue'
import CurrencyInput from './CurrencyInput.vue'
import EmptyState from './EmptyState.vue'
import LoadErrorState from './LoadErrorState.vue'
import LoadingState from './LoadingState.vue'
import ProgressBar from './ProgressBar.vue'
import PurchaseForm from './PurchaseForm.vue'
import { api } from '../services/api'
import { budgetStatus, statusLabels, usagePercent } from '../utils/budget'
import { formatCurrency } from '../utils/formatCurrency'

const props = defineProps({
  cardId: { type: Number, required: true },
  period: { type: Date, required: true },
  compact: { type: Boolean, default: false },
})

const summary = ref(null)
const categories = ref([])
const loading = ref(true)
const loadError = ref('')

const budgetModalOpen = ref(false)
const budgetEditing = ref(null)
const budgetSaving = ref(false)
const budgetError = ref('')
const budgetForm = ref({ category_id: '', budget_amount: 0 })
const categoryLocked = ref(false)

const purchaseTarget = ref(null)
const purchaseSaving = ref(false)
const purchaseError = ref('')

const confirmTarget = ref(null)

const statusVariant = {
  undefined: 'neutral',
  ok: 'income',
  near: 'variable',
  full: 'variable',
  over: 'expense',
}

const month = computed(() => {
  const year = props.period.getFullYear()
  const monthNumber = String(props.period.getMonth() + 1).padStart(2, '0')
  return `${year}-${monthNumber}`
})

const categoryOptions = computed(() =>
  categories.value
    .filter((category) => category.is_active && category.group_type === 'expense')
    .map((category) => ({ value: String(category.id), label: category.name })),
)

async function load() {
  loading.value = true
  loadError.value = ''
  try {
    summary.value = await api.get(`/budgets?month=${month.value}&card_id=${props.cardId}`)
  } catch (err) {
    loadError.value = err.message || 'Não foi possível carregar os orçamentos.'
  } finally {
    loading.value = false
  }
}

watch(() => [props.cardId, props.period], load)

function openCreateBudget(row = null) {
  budgetEditing.value = null
  budgetError.value = ''
  categoryLocked.value = Boolean(row)
  budgetForm.value = {
    category_id: row ? String(row.category_id) : '',
    budget_amount: 0,
  }
  budgetModalOpen.value = true
}

function openEditBudget(row) {
  budgetEditing.value = row
  budgetError.value = ''
  categoryLocked.value = true
  budgetForm.value = {
    category_id: String(row.category_id),
    budget_amount: Number(row.budget_amount),
  }
  budgetModalOpen.value = true
}

async function onSaveBudget() {
  budgetSaving.value = true
  budgetError.value = ''
  const payload = {
    budget_amount: budgetForm.value.budget_amount,
  }
  try {
    if (budgetEditing.value) {
      await api.put(`/budgets/${budgetEditing.value.id}`, payload)
    } else {
      await api.post('/budgets', {
        card_id: props.cardId,
        category_id: Number(budgetForm.value.category_id),
        month: month.value,
        ...payload,
      })
    }
    budgetModalOpen.value = false
    await load()
  } catch (err) {
    budgetError.value = err.message || 'Não foi possível salvar o orçamento.'
  } finally {
    budgetSaving.value = false
  }
}

async function onConfirmDeleteBudget() {
  const row = confirmTarget.value
  confirmTarget.value = null
  await api.delete(`/budgets/${row.id}`)
  await load()
}

function openPurchase(row) {
  purchaseError.value = ''
  purchaseTarget.value = row
}

async function onSavePurchase(payload) {
  purchaseSaving.value = true
  purchaseError.value = ''
  try {
    // T-059: compra iniciada a partir da categoria orçada.
    await api.post(`/cards/${props.cardId}/purchases`, payload)
    purchaseTarget.value = null
    await load()
  } catch (err) {
    purchaseError.value = err.message || 'Não foi possível salvar a compra.'
  } finally {
    purchaseSaving.value = false
  }
}

function percentOf(row) {
  const percent = usagePercent(row)
  return percent === null ? null : `${percent}%`
}

onMounted(async () => {
  categories.value = await api.get('/categories')
  await load()
})
</script>

<template>
  <div>
    <div class="mb-3 flex items-center justify-between gap-3">
      <p class="text-sm text-neutral-500">
        Gastos do mês seguem o ciclo da fatura com vencimento no período.
      </p>
      <BaseButton size="sm" @click="openCreateBudget()">
        <PlusIcon class="h-4 w-4" aria-hidden="true" />
        Novo Orçamento
      </BaseButton>
    </div>

    <LoadErrorState v-if="loadError" class="mb-4" :message="loadError" @retry="load" />

    <LoadingState v-if="loading" />

    <EmptyState
      v-else-if="summary && summary.rows.length === 0"
      title="Nenhum orçamento ou gasto neste mês"
      description="Defina um orçamento por categoria para acompanhar seus gastos."
    >
      <template #actions>
        <BaseButton size="sm" @click="openCreateBudget()">Novo Orçamento</BaseButton>
      </template>
    </EmptyState>

    <div
      v-else-if="summary"
      class="overflow-x-auto rounded-card border border-neutral-200 bg-white shadow-card"
    >
      <table class="w-full min-w-[44rem] text-left text-sm">
        <caption class="sr-only">
          Orçamento por categoria do cartão no mês selecionado
        </caption>
        <thead class="border-b border-neutral-200 bg-neutral-50 text-xs uppercase text-neutral-500">
          <tr>
            <th class="px-4 py-3">Categoria</th>
            <th class="px-4 py-3 text-right">Orçamento</th>
            <th class="px-4 py-3 text-right">Gastos</th>
            <th class="px-4 py-3 text-right">Restante</th>
            <th class="px-4 py-3">Uso</th>
            <th class="px-4 py-3 text-right">Ações</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-neutral-100">
          <tr v-for="row in summary.rows" :key="row.category_id">
            <td class="px-4 py-3">
              <p class="font-medium text-neutral-900">{{ row.category_name }}</p>
              <BaseBadge :variant="statusVariant[budgetStatus(row)]" class="mt-1">
                {{ statusLabels[budgetStatus(row)] }}
              </BaseBadge>
            </td>
            <td class="px-4 py-3 text-right tabular-nums">
              <template v-if="row.budget_amount !== null">
                {{ formatCurrency(row.budget_amount) }}
              </template>
              <span v-else class="text-neutral-400">Não definido</span>
            </td>
            <td class="px-4 py-3 text-right font-semibold tabular-nums">
              {{ formatCurrency(row.spent) }}
            </td>
            <td
              class="px-4 py-3 text-right font-semibold tabular-nums"
              :class="Number(row.remaining) < 0 ? 'text-negative' : 'text-neutral-900'"
            >
              <template v-if="row.remaining !== null">
                {{ formatCurrency(row.remaining) }}
              </template>
              <span v-else class="font-normal text-neutral-400">Não definido</span>
            </td>
            <td class="px-4 py-3">
              <div v-if="row.usage_percent !== null" class="flex items-center gap-3">
                <ProgressBar
                  :value="Number(row.spent)"
                  :max="Number(row.budget_amount)"
                  :show-label="false"
                  class="flex-1"
                />
                <span class="w-12 text-right text-xs tabular-nums text-neutral-500">
                  {{ percentOf(row) }}
                </span>
              </div>
              <span v-else class="text-xs text-neutral-400">—</span>
            </td>
            <td class="px-4 py-3">
              <div class="flex items-center justify-end gap-2">
                <button
                  type="button"
                  class="text-positive hover:text-positive/80"
                  aria-label="Adicionar compra"
                  @click="openPurchase(row)"
                >
                  <ShoppingCartIcon class="h-4 w-4" />
                </button>
                <template v-if="row.budget_amount !== null">
                  <button
                    type="button"
                    class="text-primary hover:text-primary-dark"
                    aria-label="Editar orçamento"
                    @click="openEditBudget(row)"
                  >
                    <PencilSquareIcon class="h-4 w-4" />
                  </button>
                  <button
                    type="button"
                    class="text-negative hover:text-negative/80"
                    aria-label="Remover orçamento"
                    @click="confirmTarget = row"
                  >
                    <TrashIcon class="h-4 w-4" />
                  </button>
                </template>
                <BaseButton v-else size="sm" variant="secondary" @click="openCreateBudget(row)">
                  Definir orçamento
                </BaseButton>
              </div>
            </td>
          </tr>
        </tbody>
        <tfoot class="border-t border-neutral-200 bg-neutral-50 text-sm font-semibold">
          <tr>
            <td class="px-4 py-3">Total</td>
            <td class="px-4 py-3 text-right tabular-nums">
              {{ formatCurrency(summary.totals.budget_amount) }}
            </td>
            <td class="px-4 py-3 text-right tabular-nums">
              {{ formatCurrency(summary.totals.spent) }}
            </td>
            <td
              class="px-4 py-3 text-right tabular-nums"
              :class="Number(summary.totals.remaining) < 0 ? 'text-negative' : ''"
            >
              {{ formatCurrency(summary.totals.remaining) }}
            </td>
            <td class="px-4 py-3"></td>
            <td class="px-4 py-3"></td>
          </tr>
        </tfoot>
      </table>
    </div>

    <BaseModal
      :open="budgetModalOpen"
      :title="budgetEditing ? 'Editar orçamento' : 'Novo orçamento'"
      @update:open="budgetModalOpen = $event"
    >
      <form class="space-y-4" @submit.prevent="onSaveBudget">
        <BaseSelect
          v-model="budgetForm.category_id"
          label="Categoria"
          :options="categoryOptions"
          placeholder="Selecione a categoria"
          :disabled="categoryLocked"
          required
        />
        <CurrencyInput v-model="budgetForm.budget_amount" label="Valor planejado" />

        <p
          v-if="budgetError"
          role="alert"
          class="rounded-md bg-negative-light px-3 py-2 text-sm text-negative"
        >
          {{ budgetError }}
        </p>

        <div class="flex justify-end gap-2">
          <BaseButton variant="secondary" type="button" @click="budgetModalOpen = false">
            Cancelar
          </BaseButton>
          <BaseButton type="submit" :loading="budgetSaving">Salvar</BaseButton>
        </div>
      </form>
    </BaseModal>

    <BaseModal
      :open="Boolean(purchaseTarget)"
      :title="`Nova compra — ${purchaseTarget?.category_name ?? ''}`"
      @update:open="purchaseTarget = null"
    >
      <PurchaseForm
        :categories="categories"
        :initial="purchaseTarget ? { category_id: purchaseTarget.category_id } : null"
        :loading="purchaseSaving"
        :error="purchaseError"
        @submit="onSavePurchase"
        @cancel="purchaseTarget = null"
      />
    </BaseModal>

    <ConfirmDialog
      :open="Boolean(confirmTarget)"
      title="Remover orçamento"
      :message="`Deseja remover o orçamento de &quot;${confirmTarget?.category_name}&quot;? As compras registradas não serão excluídas.`"
      confirm-label="Remover"
      @update:open="confirmTarget = null"
      @confirm="onConfirmDeleteBudget"
    />
  </div>
</template>
