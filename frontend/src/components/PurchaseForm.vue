<script setup>
import { computed, reactive, watch } from 'vue'

import BaseButton from './BaseButton.vue'
import BaseInput from './BaseInput.vue'
import BaseSelect from './BaseSelect.vue'
import CurrencyInput from './CurrencyInput.vue'

const props = defineProps({
  categories: { type: Array, default: () => [] },
  cards: { type: Array, default: () => [] },
  initial: { type: Object, default: null },
  loading: { type: Boolean, default: false },
  error: { type: String, default: '' },
})

const emit = defineEmits(['submit', 'cancel'])

const form = reactive({
  card_id: '',
  description: '',
  total_amount: 0,
  purchase_date: new Date().toISOString().slice(0, 10),
  category_id: '',
  notes: '',
})

watch(
  () => props.initial,
  (value) => {
    // Sem `initial` (criação), o formulário volta ao estado inicial.
    Object.assign(form, {
      card_id: '',
      description: value?.description ?? '',
      total_amount: Number(value?.total_amount ?? 0),
      purchase_date: value?.purchase_date ?? new Date().toISOString().slice(0, 10),
      category_id: value?.category_id != null ? String(value.category_id) : '',
      notes: value?.notes ?? '',
    })
  },
  { immediate: true },
)

const categoryOptions = props.categories
  .filter((category) => category.is_active && category.group_type === 'expense')
  .map((category) => ({ value: String(category.id), label: category.name }))

const cardOptions = computed(() =>
  props.cards.map((card) => ({ value: String(card.id), label: card.name })),
)

const withCardSelect = computed(() => props.cards.length > 0)

function onSubmit() {
  const payload = {
    description: form.description,
    total_amount: form.total_amount,
    purchase_date: form.purchase_date,
    category_id: Number(form.category_id),
    notes: form.notes || null,
  }
  // Com seletor de cartão (Movimentações), o cartão faz parte do payload;
  // sem ele, o cartão vem do contexto (tela de Cartões/Orçamentos).
  if (withCardSelect.value) payload.card_id = Number(form.card_id)
  emit('submit', payload)
}
</script>

<template>
  <form class="space-y-4" @submit.prevent="onSubmit">
    <BaseSelect
      v-if="withCardSelect"
      v-model="form.card_id"
      label="Cartão"
      :options="cardOptions"
      placeholder="Selecione o cartão"
      required
    />
    <BaseInput
      v-model="form.description"
      label="Descrição"
      placeholder="Ex.: Supermercado, Combustível..."
      required
    />
    <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
      <CurrencyInput v-model="form.total_amount" label="Valor" />
      <BaseInput v-model="form.purchase_date" label="Data da compra" type="date" required />
    </div>
    <BaseSelect
      v-model="form.category_id"
      label="Categoria"
      :options="categoryOptions"
      placeholder="Selecione a categoria"
      required
    />
    <BaseInput v-model="form.notes" label="Observações" placeholder="Opcional" />

    <p
      v-if="error"
      role="alert"
      class="rounded-md bg-negative-light px-3 py-2 text-sm text-negative"
    >
      {{ error }}
    </p>

    <div class="flex justify-end gap-2">
      <BaseButton variant="secondary" type="button" @click="emit('cancel')"> Cancelar </BaseButton>
      <BaseButton type="submit" :loading="loading">Salvar</BaseButton>
    </div>
  </form>
</template>
