<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import {
  ArrowPathIcon,
  BanknotesIcon,
  PencilSquareIcon,
  PlusIcon,
  ShoppingCartIcon,
  TrashIcon,
} from '@heroicons/vue/24/outline'

import BaseBadge from './BaseBadge.vue'
import BaseButton from './BaseButton.vue'
import BaseInput from './BaseInput.vue'
import BaseMessage from './BaseMessage.vue'
import BaseModal from './BaseModal.vue'
import BaseSelect from './BaseSelect.vue'
import ConfirmDialog from './ConfirmDialog.vue'
import CurrencyInput from './CurrencyInput.vue'
import EmptyState from './EmptyState.vue'
import LoadErrorState from './LoadErrorState.vue'
import LoadingState from './LoadingState.vue'
import ProgressBar from './ProgressBar.vue'
import PurchaseForm from './PurchaseForm.vue'
import TransactionForm from './TransactionForm.vue'
import { api } from '../services/api'
import { budgetStatus, statusLabels, usagePercent } from '../utils/budget'
import { formatCurrency } from '../utils/formatCurrency'
import { formatMonthYear } from '../utils/period'

const props = defineProps({
  cardId: { type: Number, default: null },
  mode: { type: String, default: 'card' },
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
const budgetForm = ref({ category_id: '', budget_amount: 0, mode: 'single', count: 3 })
const categoryLocked = ref(false)

const seriesNotice = ref('')
const seriesTarget = ref(null)

const purchaseTarget = ref(null)
const purchaseSaving = ref(false)
const purchaseError = ref('')

const movementTarget = ref(null)
const movementSaving = ref(false)
const movementError = ref('')

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

const isGeneral = computed(() => props.mode === 'general')

const spentHint = computed(() =>
  isGeneral.value
    ? 'Gastos do mês seguem as movimentações comuns lançadas no período.'
    : 'Gastos do mês seguem o ciclo da fatura com vencimento no período.',
)

const budgetModeOptions = [
  { value: 'single', label: 'Valor único (este mês)' },
  { value: 'installments', label: 'Parcelar valor total em meses' },
  { value: 'monthly', label: 'Repetir valor mensal' },
]

const budgetAmountLabel = computed(() => {
  if (!budgetEditing.value && budgetForm.value.mode === 'installments') {
    return 'Valor total'
  }
  if (!budgetEditing.value && budgetForm.value.mode === 'monthly') {
    return 'Valor mensal'
  }
  return 'Valor planejado'
})

const budgetModeHint = computed(() => {
  const amount = Number(budgetForm.value.budget_amount) || 0
  const count = Number(budgetForm.value.count) || 0
  if (count <= 0) return ''
  if (budgetForm.value.mode === 'installments') {
    return `Aproximadamente ${formatCurrency(amount / count)} por mês, em ${count} meses.`
  }
  if (budgetForm.value.mode === 'monthly') {
    return `Total de ${formatCurrency(amount * count)} em ${count} meses.`
  }
  return ''
})

const categoryOptions = computed(() =>
  categories.value
    .filter((category) => category.is_active && category.group_type === 'expense')
    .map((category) => ({ value: String(category.id), label: category.name })),
)

async function load() {
  loading.value = true
  loadError.value = ''
  seriesNotice.value = ''
  try {
    const query = isGeneral.value
      ? `/budgets/general?month=${month.value}`
      : `/budgets?month=${month.value}&card_id=${props.cardId}`
    summary.value = await api.get(query)
  } catch (err) {
    loadError.value = err.message || 'Não foi possível carregar os orçamentos.'
  } finally {
    loading.value = false
  }
}

watch(() => [props.cardId, props.period, props.mode], load)

const budgetBase = computed(() => (isGeneral.value ? '/budgets/general' : '/budgets'))

function openCreateBudget(row = null) {
  budgetEditing.value = null
  budgetError.value = ''
  categoryLocked.value = Boolean(row)
  budgetForm.value = {
    category_id: row ? String(row.category_id) : '',
    budget_amount: 0,
    mode: 'single',
    count: 3,
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
    mode: 'single',
    count: 3,
  }
  budgetModalOpen.value = true
}

async function onSaveBudget() {
  budgetSaving.value = true
  budgetError.value = ''
  const isSeries = !budgetEditing.value && budgetForm.value.mode !== 'single'
  const count = Number(budgetForm.value.count)
  if (isSeries && (!Number.isInteger(count) || count < 2 || count > 60)) {
    budgetError.value = 'Informe um número de meses entre 2 e 60.'
    budgetSaving.value = false
    return
  }
  const payload = {
    budget_amount: budgetForm.value.budget_amount,
  }
  let notice = ''
  try {
    if (budgetEditing.value) {
      await api.put(`${budgetBase.value}/${budgetEditing.value.id}`, payload)
    } else if (isSeries) {
      // T-075: série de orçamentos (parcelas ou valor repetido).
      const body = await api.post(`${budgetBase.value}/recurrences`, {
        ...(isGeneral.value ? {} : { card_id: props.cardId }),
        category_id: Number(budgetForm.value.category_id),
        month: month.value,
        recurrence: {
          mode: budgetForm.value.mode,
          amount: budgetForm.value.budget_amount,
          count,
        },
      })
      notice = seriesNoticeText(body)
    } else {
      await api.post(budgetBase.value, {
        ...(isGeneral.value ? {} : { card_id: props.cardId }),
        category_id: Number(budgetForm.value.category_id),
        month: month.value,
        ...payload,
      })
    }
    budgetModalOpen.value = false
    await load()
    seriesNotice.value = notice
  } catch (err) {
    budgetError.value = err.message || 'Não foi possível salvar o orçamento.'
  } finally {
    budgetSaving.value = false
  }
}

function parseMonth(month) {
  const [year, monthNumber] = month.split('-').map(Number)
  return new Date(year, monthNumber - 1, 1)
}

function seriesNoticeText(body) {
  const first = formatMonthYear(parseMonth(body.months[0]))
  const last = formatMonthYear(parseMonth(body.months[body.months.length - 1]))
  return `Orçamento criado para ${body.months.length} meses (${first} a ${last}).`
}

function recurrenceLabel(recurrence) {
  return recurrence.mode === 'installments'
    ? `Parcela ${recurrence.position}/${recurrence.total}`
    : 'Recorrente'
}

async function onConfirmDeleteSeries() {
  const row = seriesTarget.value
  seriesTarget.value = null
  try {
    await api.delete(`${budgetBase.value}/recurrences/${row.recurrence.id}`)
    await load()
  } catch (err) {
    loadError.value = err.message || 'Não foi possível excluir a série.'
  }
}

async function onConfirmDeleteBudget() {
  const row = confirmTarget.value
  confirmTarget.value = null
  await api.delete(`${budgetBase.value}/${row.id}`)
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

function openMovement(row) {
  movementError.value = ''
  movementTarget.value = row
}

async function onSaveMovement(payload) {
  movementSaving.value = true
  movementError.value = ''
  try {
    // T-074: atalho de movimentação comum a partir da categoria orçada.
    await api.post('/transactions', payload)
    movementTarget.value = null
    await load()
  } catch (err) {
    movementError.value = err.message || 'Não foi possível salvar a movimentação.'
  } finally {
    movementSaving.value = false
  }
}

function categoryExpenseLabel(row) {
  const category = categories.value.find((item) => item.id === row.category_id)
  return category?.expense_type === 'fixed' ? 'Fixa' : 'Variável'
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
        {{ spentHint }}
      </p>
      <BaseButton size="sm" @click="openCreateBudget()">
        <PlusIcon class="h-4 w-4" aria-hidden="true" />
        Novo Orçamento
      </BaseButton>
    </div>

    <BaseMessage v-if="seriesNotice" type="success" class="mb-4">
      {{ seriesNotice }}
    </BaseMessage>

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
          {{
            isGeneral
              ? 'Orçamento por categoria das despesas gerais no mês selecionado'
              : 'Orçamento por categoria do cartão no mês selecionado'
          }}
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
              <div class="mt-1 flex flex-wrap gap-1">
                <BaseBadge :variant="statusVariant[budgetStatus(row)]">
                  {{ statusLabels[budgetStatus(row)] }}
                </BaseBadge>
                <BaseBadge v-if="row.recurrence" variant="fixed">
                  {{ recurrenceLabel(row.recurrence) }}
                </BaseBadge>
                <BaseBadge v-if="isGeneral" variant="neutral">
                  {{ categoryExpenseLabel(row) }}
                </BaseBadge>
              </div>
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
                  v-if="isGeneral"
                  type="button"
                  class="text-positive hover:text-positive/80"
                  aria-label="Adicionar movimentação"
                  @click="openMovement(row)"
                >
                  <BanknotesIcon class="h-4 w-4" />
                </button>
                <button
                  v-else
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
                    v-if="row.recurrence"
                    type="button"
                    class="text-negative hover:text-negative/80"
                    aria-label="Excluir série"
                    title="Excluir todos os meses da série"
                    @click="seriesTarget = row"
                  >
                    <ArrowPathIcon class="h-4 w-4" />
                  </button>
                  <button
                    type="button"
                    class="text-negative hover:text-negative/80"
                    aria-label="Remover orçamento"
                    title="Remover somente este mês"
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
        <BaseSelect
          v-if="!budgetEditing"
          v-model="budgetForm.mode"
          label="Tipo de orçamento"
          :options="budgetModeOptions"
        />
        <CurrencyInput
          v-model="budgetForm.budget_amount"
          :label="budgetAmountLabel"
        />
        <BaseInput
          v-if="!budgetEditing && budgetForm.mode !== 'single'"
          v-model.number="budgetForm.count"
          :label="
            budgetForm.mode === 'installments'
              ? 'Número de parcelas (meses)'
              : 'Repetir por (meses)'
          "
          type="number"
          min="2"
          max="60"
          required
        />
        <p v-if="budgetModeHint" class="text-sm text-neutral-500">
          {{ budgetModeHint }}
        </p>

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

    <BaseModal
      :open="Boolean(movementTarget)"
      :title="`Nova movimentação — ${movementTarget?.category_name ?? ''}`"
      @update:open="movementTarget = null"
    >
      <TransactionForm
        :categories="categories"
        :initial="
          movementTarget
            ? { type: 'expense', category_id: movementTarget.category_id }
            : null
        "
        :loading="movementSaving"
        :error="movementError"
        @submit="onSaveMovement"
        @cancel="movementTarget = null"
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

    <ConfirmDialog
      :open="Boolean(seriesTarget)"
      title="Excluir série de orçamentos"
      :message="`Deseja excluir a série de &quot;${seriesTarget?.category_name}&quot;? Todos os meses gerados serão removidos.`"
      confirm-label="Excluir série"
      @update:open="seriesTarget = null"
      @confirm="onConfirmDeleteSeries"
    />
  </div>
</template>
