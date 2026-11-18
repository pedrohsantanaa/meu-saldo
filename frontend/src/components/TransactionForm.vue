<script setup>
import { computed, reactive, watch } from 'vue'

import BaseButton from './BaseButton.vue'
import BaseInput from './BaseInput.vue'
import BaseSelect from './BaseSelect.vue'
import CurrencyInput from './CurrencyInput.vue'

const props = defineProps({
  categories: { type: Array, default: () => [] },
  initial: { type: Object, default: null },
  loading: { type: Boolean, default: false },
  error: { type: String, default: '' },
})

const emit = defineEmits(['submit', 'cancel'])

const typeOptions = [
  { value: 'income', label: 'Receita' },
  { value: 'expense', label: 'Despesa' },
  { value: 'investment', label: 'Investimento' },
]

const expenseTypeOptions = [
  { value: 'fixed', label: 'Fixa' },
  { value: 'variable', label: 'Variável' },
]

const paymentOptions = [
  { value: 'dinheiro', label: 'Dinheiro' },
  { value: 'pix', label: 'Pix' },
  { value: 'debito', label: 'Débito' },
  { value: 'outra', label: 'Outra' },
]

const form = reactive({
  type: 'expense',
  description: '',
  amount: 0,
  transaction_date: new Date().toISOString().slice(0, 10),
  category_id: '',
  expense_type: 'variable',
  payment_method: 'pix',
  notes: '',
})

watch(
  () => props.initial,
  (value) => {
    if (!value) return
    Object.assign(form, {
      type: value.type,
      description: value.description,
      amount: Number(value.amount),
      transaction_date: value.transaction_date,
      category_id: String(value.category_id),
      expense_type: value.expense_type ?? 'variable',
      payment_method: value.payment_method ?? 'pix',
      notes: value.notes ?? '',
    })
  },
  { immediate: true }
)

const categoryOptions = computed(() =>
  props.categories
    .filter((category) => category.is_active && category.group_type === form.type)
    .map((category) => ({ value: String(category.id), label: category.name }))
)

const isExpense = computed(() => form.type === 'expense')

watch(
  () => form.type,
  () => {
    const visible = categoryOptions.value.some((option) => option.value === form.category_id)
    if (!visible) form.category_id = ''
  }
)

function onSubmit() {
  emit('submit', {
    type: form.type,
    description: form.description,
    amount: form.amount,
    transaction_date: form.transaction_date,
    category_id: Number(form.category_id),
    expense_type: isExpense.value ? form.expense_type : null,
    payment_method: isExpense.value ? form.payment_method : null,
    notes: form.notes || null,
  })
}
</script>

<template>
  <form class="space-y-4" @submit.prevent="onSubmit">
    <BaseSelect
      v-model="form.type"
      label="Tipo"
      :options="typeOptions"
    />

    <BaseInput
      v-model="form.description"
      label="Descrição"
      placeholder="Ex.: Supermercado, Salário..."
      required
    />

    <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
      <CurrencyInput v-model="form.amount" label="Valor" />
      <BaseInput
        v-model="form.transaction_date"
        label="Data"
        type="date"
        required
      />
    </div>

    <BaseSelect
      v-model="form.category_id"
      label="Categoria"
      :options="categoryOptions"
      placeholder="Selecione a categoria"
      required
    />

    <div v-if="isExpense" class="grid grid-cols-1 gap-4 sm:grid-cols-2">
      <BaseSelect
        v-model="form.expense_type"
        label="Classificação"
        :options="expenseTypeOptions"
      />
      <BaseSelect
        v-model="form.payment_method"
        label="Forma de pagamento"
        :options="paymentOptions"
      />
    </div>

    <BaseInput v-model="form.notes" label="Observações" placeholder="Opcional" />

    <p
      v-if="error"
      role="alert"
      class="rounded-md bg-negative-light px-3 py-2 text-sm text-negative"
    >
      {{ error }}
    </p>

    <div class="flex justify-end gap-2">
      <BaseButton variant="secondary" type="button" @click="emit('cancel')">
        Cancelar
      </BaseButton>
      <BaseButton type="submit" :loading="loading">Salvar</BaseButton>
    </div>
  </form>
</template>
