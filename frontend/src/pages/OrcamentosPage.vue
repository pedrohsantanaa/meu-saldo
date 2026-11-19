<script setup>
import { computed, onMounted, ref } from 'vue'
import { CreditCardIcon } from '@heroicons/vue/24/outline'

import BaseSelect from '../components/BaseSelect.vue'
import BudgetSection from '../components/BudgetSection.vue'
import EmptyState from '../components/EmptyState.vue'
import LoadingState from '../components/LoadingState.vue'
import MonthSelector from '../components/MonthSelector.vue'
import SectionHeader from '../components/SectionHeader.vue'
import { api } from '../services/api'

const period = ref(new Date())
const cards = ref([])
const selectedCardId = ref('')
const loading = ref(true)

const cardOptions = computed(() =>
  cards.value.map((card) => ({ value: String(card.id), label: card.name })),
)

onMounted(async () => {
  cards.value = await api.get('/cards')
  selectedCardId.value = String(cards.value[0]?.id ?? '')
  loading.value = false
})
</script>

<template>
  <section>
    <SectionHeader
      title="Orçamentos"
      description="Defina um orçamento por categoria em cada cartão e acompanhe os gastos do mês."
    />

    <LoadingState v-if="loading" />

    <EmptyState
      v-else-if="cards.length === 0"
      title="Nenhum cartão cadastrado"
      description="Cadastre um cartão em Cartões para definir orçamentos por categoria."
    />

    <template v-else>
      <div class="mb-4 flex flex-wrap items-center gap-3">
        <MonthSelector v-model="period" />

        <div class="flex items-center gap-2">
          <span
            class="flex h-8 w-8 items-center justify-center rounded-full bg-attention-light text-attention"
          >
            <CreditCardIcon class="h-4 w-4" aria-hidden="true" />
          </span>
          <BaseSelect
            v-model="selectedCardId"
            :options="cardOptions"
            class="w-56"
            aria-label="Selecionar cartão"
          />
        </div>
      </div>

      <BudgetSection v-if="selectedCardId" :card-id="Number(selectedCardId)" :period="period" />
    </template>
  </section>
</template>
