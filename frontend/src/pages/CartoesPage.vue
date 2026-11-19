<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import {
  BanknotesIcon,
  CheckCircleIcon,
  CreditCardIcon,
  PencilSquareIcon,
  PlusIcon,
  ShoppingCartIcon,
  TrashIcon,
} from '@heroicons/vue/24/outline'

import BaseBadge from '../components/BaseBadge.vue'
import BaseButton from '../components/BaseButton.vue'
import BaseInput from '../components/BaseInput.vue'
import BaseModal from '../components/BaseModal.vue'
import BaseSelect from '../components/BaseSelect.vue'
import BaseTabs from '../components/BaseTabs.vue'
import ConfirmDialog from '../components/ConfirmDialog.vue'
import CurrencyInput from '../components/CurrencyInput.vue'
import EmptyState from '../components/EmptyState.vue'
import LoadingState from '../components/LoadingState.vue'
import MonthSelector from '../components/MonthSelector.vue'
import ProgressBar from '../components/ProgressBar.vue'
import SectionHeader from '../components/SectionHeader.vue'
import SummaryCard from '../components/SummaryCard.vue'
import { api } from '../services/api'
import { formatCurrency } from '../utils/formatCurrency'
import { formatDate } from '../utils/formatDate'

const cards = ref([])
const categories = ref([])
const purchases = ref([])
const invoices = ref([])
const invoiceOverview = ref(null)
const loading = ref(true)
const loadingDetails = ref(false)

const selectedCardId = ref(null)
const period = ref(new Date())
const activeTab = ref('compras')

const cardModalOpen = ref(false)
const cardEditing = ref(null)
const cardSaving = ref(false)
const cardError = ref('')
const cardForm = reactive({
  name: '',
  issuer: '',
  credit_limit: 0,
  closing_day: 1,
  due_day: 10,
})

const purchaseModalOpen = ref(false)
const purchaseEditing = ref(null)
const purchaseSaving = ref(false)
const purchaseError = ref('')
const purchaseForm = reactive({
  description: '',
  total_amount: 0,
  purchase_date: new Date().toISOString().slice(0, 10),
  category_id: '',
  notes: '',
})

const paymentTarget = ref(null)
const paymentSaving = ref(false)
const paymentError = ref('')
const paymentForm = reactive({ amount: 0, paid_at: new Date().toISOString().slice(0, 10) })

const confirmPurchaseTarget = ref(null)
const confirmCardTarget = ref(null)

const tabs = [
  { value: 'compras', label: 'Compras' },
  { value: 'orcamento', label: 'Orçamento por Categoria' },
  { value: 'faturas', label: 'Faturas' },
]

const cardGradients = [
  'from-purple-500 to-purple-700',
  'from-blue-500 to-blue-700',
  'from-orange-400 to-orange-600',
  'from-emerald-500 to-emerald-700',
  'from-rose-500 to-rose-700',
]

const selectedCard = computed(
  () => cards.value.find((card) => card.id === selectedCardId.value) ?? null,
)

const categoryOptions = computed(() =>
  categories.value
    .filter((category) => category.is_active && category.group_type === 'expense')
    .map((category) => ({ value: String(category.id), label: category.name })),
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

const invoiceStatusLabel = { open: 'Em aberto', partial: 'Parcial', paid: 'Paga' }
const invoiceStatusVariant = { open: 'expense', partial: 'variable', paid: 'income' }

function categoryName(id) {
  return categories.value.find((category) => category.id === id)?.name ?? '—'
}

function invoiceMonth(invoice) {
  if (!invoice) return '—'
  const [year, month] = invoice.reference_month.split('-')
  return `${month}/${year}`
}

function gradientOf(card) {
  return cardGradients[card.id % cardGradients.length]
}

async function loadCards() {
  cards.value = await api.get('/cards')
  if (!cards.value.some((card) => card.id === selectedCardId.value)) {
    selectedCardId.value = cards.value[0]?.id ?? null
  }
}

async function loadDetails() {
  if (!selectedCardId.value) {
    purchases.value = []
    invoices.value = []
    invoiceOverview.value = null
    return
  }
  loadingDetails.value = true
  const params = new URLSearchParams(monthBounds.value)
  const [purchaseList, invoiceList, overview] = await Promise.all([
    api.get(`/cards/${selectedCardId.value}/purchases?${params.toString()}`),
    api.get(`/cards/${selectedCardId.value}/invoices`),
    api.get(`/cards/${selectedCardId.value}/invoices/overview`),
  ])
  purchases.value = purchaseList
  invoices.value = invoiceList
  invoiceOverview.value = overview
  loadingDetails.value = false
}

watch([selectedCardId, period], loadDetails)

function openCreateCard() {
  cardEditing.value = null
  cardError.value = ''
  Object.assign(cardForm, {
    name: '',
    issuer: '',
    credit_limit: 0,
    closing_day: 1,
    due_day: 10,
  })
  cardModalOpen.value = true
}

function openEditCard(card) {
  cardEditing.value = card
  cardError.value = ''
  Object.assign(cardForm, {
    name: card.name,
    issuer: card.issuer ?? '',
    credit_limit: Number(card.credit_limit),
    closing_day: card.closing_day,
    due_day: card.due_day,
  })
  cardModalOpen.value = true
}

async function onSaveCard() {
  cardSaving.value = true
  cardError.value = ''
  const payload = {
    name: cardForm.name,
    issuer: cardForm.issuer || null,
    credit_limit: cardForm.credit_limit,
    closing_day: Number(cardForm.closing_day),
    due_day: Number(cardForm.due_day),
  }
  try {
    const saved = cardEditing.value
      ? await api.put(`/cards/${cardEditing.value.id}`, payload)
      : await api.post('/cards', payload)
    cardModalOpen.value = false
    selectedCardId.value = saved.id
    await loadCards()
    await loadDetails()
  } catch (err) {
    cardError.value = err.message || 'Não foi possível salvar o cartão.'
  } finally {
    cardSaving.value = false
  }
}

async function onConfirmToggleCard() {
  const card = confirmCardTarget.value
  confirmCardTarget.value = null
  await api.patch(`/cards/${card.id}/status`, { is_active: !card.is_active })
  await loadCards()
  await loadDetails()
}

function openCreatePurchase() {
  purchaseEditing.value = null
  purchaseError.value = ''
  Object.assign(purchaseForm, {
    description: '',
    total_amount: 0,
    purchase_date: new Date().toISOString().slice(0, 10),
    category_id: '',
    notes: '',
  })
  purchaseModalOpen.value = true
}

function openEditPurchase(purchase) {
  purchaseEditing.value = purchase
  purchaseError.value = ''
  Object.assign(purchaseForm, {
    description: purchase.description,
    total_amount: Number(purchase.total_amount),
    purchase_date: purchase.purchase_date,
    category_id: String(purchase.category_id),
    notes: purchase.notes ?? '',
  })
  purchaseModalOpen.value = true
}

async function onSavePurchase() {
  purchaseSaving.value = true
  purchaseError.value = ''
  const payload = {
    description: purchaseForm.description,
    total_amount: purchaseForm.total_amount,
    purchase_date: purchaseForm.purchase_date,
    category_id: Number(purchaseForm.category_id),
    notes: purchaseForm.notes || null,
  }
  try {
    const base = `/cards/${selectedCardId.value}/purchases`
    if (purchaseEditing.value) {
      await api.put(`${base}/${purchaseEditing.value.id}`, payload)
    } else {
      await api.post(base, payload)
    }
    purchaseModalOpen.value = false
    await Promise.all([loadDetails(), loadCards()])
  } catch (err) {
    purchaseError.value = err.message || 'Não foi possível salvar a compra.'
  } finally {
    purchaseSaving.value = false
  }
}

async function onConfirmDeletePurchase() {
  const purchase = confirmPurchaseTarget.value
  confirmPurchaseTarget.value = null
  await api.delete(`/cards/${selectedCardId.value}/purchases/${purchase.id}`)
  await Promise.all([loadDetails(), loadCards()])
}

function openPayment(invoice) {
  paymentTarget.value = invoice
  paymentError.value = ''
  Object.assign(paymentForm, {
    amount: Number(invoice.open_amount),
    paid_at: new Date().toISOString().slice(0, 10),
  })
}

async function onSavePayment() {
  paymentSaving.value = true
  paymentError.value = ''
  try {
    await api.post(`/cards/${selectedCardId.value}/invoices/${paymentTarget.value.id}/payments`, {
      amount: paymentForm.amount,
      paid_at: paymentForm.paid_at,
    })
    paymentTarget.value = null
    await Promise.all([loadDetails(), loadCards()])
  } catch (err) {
    paymentError.value = err.message || 'Não foi possível registrar o pagamento.'
  } finally {
    paymentSaving.value = false
  }
}

onMounted(async () => {
  categories.value = await api.get('/categories')
  await loadCards()
  loading.value = false
  await loadDetails()
})
</script>

<template>
  <section>
    <SectionHeader title="Cartões" description="Gerencie seus cartões, compras e faturas.">
      <template #actions>
        <BaseButton @click="openCreateCard">
          <PlusIcon class="h-4 w-4" aria-hidden="true" />
          Novo Cartão
        </BaseButton>
      </template>
    </SectionHeader>

    <LoadingState v-if="loading" />

    <EmptyState
      v-else-if="cards.length === 0"
      title="Nenhum cartão cadastrado"
      description="Cadastre um cartão para acompanhar compras e faturas."
    >
      <template #actions>
        <BaseButton size="sm" @click="openCreateCard">Novo Cartão</BaseButton>
      </template>
    </EmptyState>

    <div v-else class="grid grid-cols-1 gap-4 lg:grid-cols-3">
      <div class="space-y-3">
        <button
          v-for="card in cards"
          :key="card.id"
          type="button"
          class="w-full rounded-card bg-gradient-to-r p-4 text-left text-white shadow-card transition-transform"
          :class="[
            gradientOf(card),
            selectedCardId === card.id ? 'ring-2 ring-primary ring-offset-2' : '',
          ]"
          @click="selectedCardId = card.id"
        >
          <p class="flex items-center justify-between gap-2 font-semibold">
            <span class="flex items-center gap-2">
              <CreditCardIcon class="h-5 w-5" aria-hidden="true" />
              {{ card.name }}
            </span>
            <span
              v-if="!card.is_active"
              class="rounded-full bg-white/20 px-2 py-0.5 text-xs font-normal"
            >
              Inativo
            </span>
          </p>
          <p class="mt-2 text-sm text-white/80">
            {{ card.issuer || 'Sem emissor' }} · fecha dia {{ card.closing_day }}
          </p>
        </button>

        <button
          type="button"
          class="flex w-full items-center justify-center gap-2 rounded-card border border-dashed border-neutral-300 bg-white p-3 text-sm text-neutral-500 hover:border-primary hover:text-primary"
          @click="openCreateCard"
        >
          <PlusIcon class="h-4 w-4" aria-hidden="true" />
          Adicionar cartão
        </button>
      </div>

      <div v-if="selectedCard" class="lg:col-span-2">
        <div class="rounded-card border border-neutral-200 bg-white p-4 shadow-card">
          <div class="flex flex-wrap items-center justify-between gap-3">
            <div class="flex items-center gap-3">
              <span
                class="flex h-10 w-10 items-center justify-center rounded-full bg-attention-light text-attention"
              >
                <CreditCardIcon class="h-5 w-5" aria-hidden="true" />
              </span>
              <div>
                <h2 class="flex items-center gap-2 font-semibold text-neutral-900">
                  Cartão {{ selectedCard.name }}
                  <BaseBadge :variant="selectedCard.is_active ? 'income' : 'neutral'">
                    {{ selectedCard.is_active ? 'Ativo' : 'Inativo' }}
                  </BaseBadge>
                </h2>
                <p class="text-sm text-neutral-500">
                  {{ selectedCard.issuer || 'Sem emissor' }} · fecha dia
                  {{ selectedCard.closing_day }} · vence dia {{ selectedCard.due_day }}
                </p>
              </div>
            </div>
            <div class="flex items-center gap-2">
              <BaseButton variant="secondary" size="sm" @click="openEditCard(selectedCard)">
                <PencilSquareIcon class="h-4 w-4" aria-hidden="true" />
                Editar
              </BaseButton>
              <BaseButton variant="secondary" size="sm" @click="confirmCardTarget = selectedCard">
                {{ selectedCard.is_active ? 'Inativar' : 'Reativar' }}
              </BaseButton>
              <MonthSelector v-model="period" />
            </div>
          </div>

          <div class="mt-4 grid grid-cols-1 gap-3 sm:grid-cols-3">
            <SummaryCard
              label="Limite total"
              :value="Number(selectedCard.credit_limit)"
              tone="neutral"
              :icon="BanknotesIcon"
            />
            <SummaryCard
              label="Comprometido"
              :value="Number(selectedCard.committed_amount)"
              tone="negative"
              :icon="ShoppingCartIcon"
            />
            <SummaryCard
              label="Disponível"
              :value="Number(selectedCard.available_limit)"
              tone="positive"
              :icon="CheckCircleIcon"
            />
          </div>

          <div class="mt-4">
            <ProgressBar
              :value="Number(selectedCard.committed_amount)"
              :max="Number(selectedCard.credit_limit)"
            />
          </div>

          <div class="mt-6">
            <BaseTabs v-model="activeTab" :items="tabs" />

            <div v-if="activeTab === 'compras'" class="mt-4">
              <div class="mb-3 flex items-center justify-between gap-3">
                <p class="text-sm text-neutral-500">Compras registradas no período selecionado.</p>
                <BaseButton
                  size="sm"
                  :disabled="!selectedCard.is_active"
                  :title="
                    selectedCard.is_active ? '' : 'Cartões inativos não aceitam novas compras'
                  "
                  @click="openCreatePurchase"
                >
                  <PlusIcon class="h-4 w-4" aria-hidden="true" />
                  Nova Compra
                </BaseButton>
              </div>

              <LoadingState v-if="loadingDetails" />

              <div
                v-else-if="purchases.length === 0"
                class="rounded-card border border-dashed border-neutral-200 p-6 text-center text-sm text-neutral-500"
              >
                Nenhuma compra registrada neste período.
              </div>

              <div v-else class="overflow-x-auto">
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
                    <tr v-for="purchase in purchases" :key="purchase.id">
                      <td class="px-3 py-2 text-neutral-600">
                        {{ formatDate(purchase.purchase_date) }}
                      </td>
                      <td class="px-3 py-2 font-medium text-neutral-900">
                        {{ purchase.description }}
                      </td>
                      <td class="px-3 py-2">
                        <BaseBadge variant="variable">
                          {{ categoryName(purchase.category_id) }}
                        </BaseBadge>
                      </td>
                      <td class="px-3 py-2 text-right font-semibold tabular-nums">
                        {{ formatCurrency(purchase.total_amount) }}
                      </td>
                      <td class="px-3 py-2">
                        <div class="flex items-center justify-end gap-2">
                          <button
                            type="button"
                            class="text-primary hover:text-primary-dark"
                            aria-label="Editar"
                            @click="openEditPurchase(purchase)"
                          >
                            <PencilSquareIcon class="h-4 w-4" />
                          </button>
                          <button
                            type="button"
                            class="text-negative hover:text-negative/80"
                            aria-label="Excluir"
                            @click="confirmPurchaseTarget = purchase"
                          >
                            <TrashIcon class="h-4 w-4" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            <div v-else-if="activeTab === 'faturas'" class="mt-4">
              <div class="mb-4 grid grid-cols-1 gap-3 sm:grid-cols-2">
                <div class="rounded-card border border-neutral-200 bg-neutral-50 p-3">
                  <p class="text-xs uppercase text-neutral-500">Fatura atual</p>
                  <template v-if="invoiceOverview?.current">
                    <p class="mt-1 font-semibold text-neutral-900">
                      {{ invoiceMonth(invoiceOverview.current) }}
                    </p>
                    <p class="text-sm text-neutral-500">
                      Vence em {{ formatDate(invoiceOverview.current.due_date) }} ·
                      {{ formatCurrency(invoiceOverview.current.total) }}
                    </p>
                  </template>
                  <p v-else class="mt-1 text-sm text-neutral-500">Sem faturas.</p>
                </div>
                <div class="rounded-card border border-neutral-200 bg-neutral-50 p-3">
                  <p class="text-xs uppercase text-neutral-500">Próxima fatura</p>
                  <template v-if="invoiceOverview?.next">
                    <p class="mt-1 font-semibold text-neutral-900">
                      {{ invoiceMonth(invoiceOverview.next) }}
                    </p>
                    <p class="text-sm text-neutral-500">
                      Vence em {{ formatDate(invoiceOverview.next.due_date) }} ·
                      {{ formatCurrency(invoiceOverview.next.total) }}
                    </p>
                  </template>
                  <p v-else class="mt-1 text-sm text-neutral-500">Sem próxima fatura.</p>
                </div>
              </div>

              <LoadingState v-if="loadingDetails" />

              <div
                v-else-if="invoices.length === 0"
                class="rounded-card border border-dashed border-neutral-200 p-6 text-center text-sm text-neutral-500"
              >
                Nenhuma fatura registrada.
              </div>

              <div v-else class="overflow-x-auto">
                <table class="w-full min-w-[42rem] text-left text-sm">
                  <thead class="border-b border-neutral-200 text-xs uppercase text-neutral-500">
                    <tr>
                      <th class="px-3 py-2">Fatura</th>
                      <th class="px-3 py-2">Fechamento</th>
                      <th class="px-3 py-2">Vencimento</th>
                      <th class="px-3 py-2 text-right">Total</th>
                      <th class="px-3 py-2 text-right">Pago</th>
                      <th class="px-3 py-2 text-right">Em aberto</th>
                      <th class="px-3 py-2">Situação</th>
                      <th class="px-3 py-2 text-right">Ações</th>
                    </tr>
                  </thead>
                  <tbody class="divide-y divide-neutral-100">
                    <tr v-for="invoice in invoices" :key="invoice.id">
                      <td class="px-3 py-2 font-medium text-neutral-900">
                        {{ invoiceMonth(invoice) }}
                      </td>
                      <td class="px-3 py-2 text-neutral-600">
                        {{ formatDate(invoice.closing_date) }}
                      </td>
                      <td class="px-3 py-2 text-neutral-600">
                        {{ formatDate(invoice.due_date) }}
                      </td>
                      <td class="px-3 py-2 text-right font-semibold tabular-nums">
                        {{ formatCurrency(invoice.total) }}
                      </td>
                      <td class="px-3 py-2 text-right tabular-nums">
                        {{ formatCurrency(invoice.paid_amount) }}
                      </td>
                      <td class="px-3 py-2 text-right tabular-nums">
                        {{ formatCurrency(invoice.open_amount) }}
                      </td>
                      <td class="px-3 py-2">
                        <BaseBadge :variant="invoiceStatusVariant[invoice.status]">
                          {{ invoiceStatusLabel[invoice.status] }}
                        </BaseBadge>
                      </td>
                      <td class="px-3 py-2 text-right">
                        <BaseButton
                          v-if="Number(invoice.open_amount) > 0"
                          size="sm"
                          variant="secondary"
                          @click="openPayment(invoice)"
                        >
                          Registrar pagamento
                        </BaseButton>
                        <span v-else class="text-xs text-neutral-400">Liquidada</span>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            <p
              v-else
              class="mt-4 rounded-card border border-dashed border-neutral-200 p-6 text-center text-sm text-neutral-500"
            >
              O orçamento por categoria será implementado na próxima fase (T-053 a T-059).
            </p>
          </div>
        </div>
      </div>
    </div>

    <BaseModal
      :open="cardModalOpen"
      :title="cardEditing ? 'Editar cartão' : 'Novo cartão'"
      @update:open="cardModalOpen = $event"
    >
      <form class="space-y-4" @submit.prevent="onSaveCard">
        <BaseInput
          v-model="cardForm.name"
          label="Nome do cartão"
          placeholder="Ex.: Nubank, Banco do Brasil..."
          required
        />
        <BaseInput v-model="cardForm.issuer" label="Emissor" placeholder="Opcional" />
        <CurrencyInput v-model="cardForm.credit_limit" label="Limite total" />
        <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <BaseInput
            v-model="cardForm.closing_day"
            label="Dia de fechamento"
            type="number"
            min="1"
            max="31"
            required
          />
          <BaseInput
            v-model="cardForm.due_day"
            label="Dia de vencimento"
            type="number"
            min="1"
            max="31"
            required
          />
        </div>

        <p
          v-if="cardError"
          role="alert"
          class="rounded-md bg-negative-light px-3 py-2 text-sm text-negative"
        >
          {{ cardError }}
        </p>

        <div class="flex justify-end gap-2">
          <BaseButton variant="secondary" type="button" @click="cardModalOpen = false">
            Cancelar
          </BaseButton>
          <BaseButton type="submit" :loading="cardSaving">Salvar</BaseButton>
        </div>
      </form>
    </BaseModal>

    <BaseModal
      :open="purchaseModalOpen"
      :title="purchaseEditing ? 'Editar compra' : 'Nova compra'"
      @update:open="purchaseModalOpen = $event"
    >
      <form class="space-y-4" @submit.prevent="onSavePurchase">
        <BaseInput
          v-model="purchaseForm.description"
          label="Descrição"
          placeholder="Ex.: Supermercado, Combustível..."
          required
        />
        <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <CurrencyInput v-model="purchaseForm.total_amount" label="Valor" />
          <BaseInput
            v-model="purchaseForm.purchase_date"
            label="Data da compra"
            type="date"
            required
          />
        </div>
        <BaseSelect
          v-model="purchaseForm.category_id"
          label="Categoria"
          :options="categoryOptions"
          placeholder="Selecione a categoria"
          required
        />
        <BaseInput v-model="purchaseForm.notes" label="Observações" placeholder="Opcional" />

        <p
          v-if="purchaseError"
          role="alert"
          class="rounded-md bg-negative-light px-3 py-2 text-sm text-negative"
        >
          {{ purchaseError }}
        </p>

        <div class="flex justify-end gap-2">
          <BaseButton variant="secondary" type="button" @click="purchaseModalOpen = false">
            Cancelar
          </BaseButton>
          <BaseButton type="submit" :loading="purchaseSaving">Salvar</BaseButton>
        </div>
      </form>
    </BaseModal>

    <BaseModal
      :open="Boolean(paymentTarget)"
      title="Registrar pagamento de fatura"
      @update:open="paymentTarget = null"
    >
      <form class="space-y-4" @submit.prevent="onSavePayment">
        <p class="text-sm text-neutral-600">
          Fatura de {{ invoiceMonth(paymentTarget) }} · em aberto
          {{ formatCurrency(paymentTarget?.open_amount ?? 0) }}. O pagamento liquidia a obrigação e
          não gera nova despesa.
        </p>
        <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <CurrencyInput v-model="paymentForm.amount" label="Valor do pagamento" />
          <BaseInput v-model="paymentForm.paid_at" label="Data" type="date" required />
        </div>

        <p
          v-if="paymentError"
          role="alert"
          class="rounded-md bg-negative-light px-3 py-2 text-sm text-negative"
        >
          {{ paymentError }}
        </p>

        <div class="flex justify-end gap-2">
          <BaseButton variant="secondary" type="button" @click="paymentTarget = null">
            Cancelar
          </BaseButton>
          <BaseButton type="submit" :loading="paymentSaving">Pagar</BaseButton>
        </div>
      </form>
    </BaseModal>

    <ConfirmDialog
      :open="Boolean(confirmPurchaseTarget)"
      title="Excluir compra"
      :message="`Deseja excluir &quot;${confirmPurchaseTarget?.description}&quot;? A fatura e o limite serão recalculados.`"
      confirm-label="Excluir"
      @update:open="confirmPurchaseTarget = null"
      @confirm="onConfirmDeletePurchase"
    />

    <ConfirmDialog
      :open="Boolean(confirmCardTarget)"
      :title="confirmCardTarget?.is_active ? 'Inativar cartão' : 'Reativar cartão'"
      :message="
        confirmCardTarget?.is_active
          ? 'O histórico de compras e faturas será preservado, mas novas compras serão impedidas.'
          : 'O cartão voltará a aceitar novas compras.'
      "
      :confirm-label="confirmCardTarget?.is_active ? 'Inativar' : 'Reativar'"
      @update:open="confirmCardTarget = null"
      @confirm="onConfirmToggleCard"
    />
  </section>
</template>
