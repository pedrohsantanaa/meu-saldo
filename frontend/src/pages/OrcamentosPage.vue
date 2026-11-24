<script setup>
import { computed, onMounted, ref } from 'vue'
import { BanknotesIcon, CreditCardIcon } from '@heroicons/vue/24/outline'

import BaseSelect from '../components/BaseSelect.vue'
import BudgetSection from '../components/BudgetSection.vue'
import LoadErrorState from '../components/LoadErrorState.vue'
import LoadingState from '../components/LoadingState.vue'
import MonthSelector from '../components/MonthSelector.vue'
import SectionHeader from '../components/SectionHeader.vue'
import { api } from '../services/api'

const GENERAL_SCOPE = 'general'

const period = ref(new Date())
const cards = ref([])
const selectedScope = ref('')
const loading = ref(true)
const error = ref('')

const scopeOptions = computed(() => [
  { value: GENERAL_SCOPE, label: 'Despesas gerais (sem cartão)' },
  ...cards.value.map((card) => ({ value: String(card.id), label: card.name })),
])

const isGeneralScope = computed(() => selectedScope.value === GENERAL_SCOPE)

async function load() {
  loading.value = true
  error.value = ''
  try {
    cards.value = await api.get('/cards')
    // Mantém a escolha do usuário; sem cartões, começa nas despesas gerais.
    selectedScope.value = selectedScope.value || String(cards.value[0]?.id ?? GENERAL_SCOPE)
  } catch (err) {
    // AC-080: erro visível com nova tentativa, nunca spinner eterno.
    error.value = err.message || 'Não foi possível carregar os cartões.'
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<template>
  <section>
    <SectionHeader
      title="Orçamentos"
      description="Defina um orçamento por categoria — em cada cartão ou para as despesas gerais — e acompanhe os gastos do mês."
    />

    <LoadingState v-if="loading" />

    <LoadErrorState v-else-if="error" :message="error" @retry="load" />

    <template v-else>
      <div class="mb-4 flex flex-wrap items-center gap-3">
        <MonthSelector v-model="period" />

        <div class="flex items-center gap-2">
          <span
            class="flex h-8 w-8 items-center justify-center rounded-full bg-attention-light text-attention"
          >
            <BanknotesIcon v-if="isGeneralScope" class="h-4 w-4" aria-hidden="true" />
            <CreditCardIcon v-else class="h-4 w-4" aria-hidden="true" />
          </span>
          <BaseSelect
            v-model="selectedScope"
            :options="scopeOptions"
            class="w-64"
            aria-label="Selecionar escopo do orçamento"
          />
        </div>
      </div>

      <BudgetSection v-if="isGeneralScope" mode="general" :period="period" />
      <BudgetSection
        v-else-if="selectedScope"
        :card-id="Number(selectedScope)"
        mode="card"
        :period="period"
      />
    </template>
  </section>
</template>
