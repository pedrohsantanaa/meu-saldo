<script setup>
import { ref } from 'vue'

import BaseButton from '../components/BaseButton.vue'
import BaseMessage from '../components/BaseMessage.vue'
import EmptyState from '../components/EmptyState.vue'
import MonthSelector from '../components/MonthSelector.vue'
import SectionHeader from '../components/SectionHeader.vue'
import SummaryCard from '../components/SummaryCard.vue'

const period = ref(new Date())
const mode = ref('mensal')
</script>

<template>
  <section>
    <SectionHeader title="Visão geral" description="Resumo financeiro do período selecionado.">
      <template #actions>
        <BaseButton>Adicionar movimentação</BaseButton>
      </template>
    </SectionHeader>

    <div class="mb-6">
      <MonthSelector v-model="period" v-model:mode="mode" />
    </div>

    <BaseMessage type="info" class="mb-6">
      Dados de demonstração. Os cálculos reais serão implementados nas próximas fases.
    </BaseMessage>

    <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
      <SummaryCard label="Total de receitas" :value="5000" tone="positive" />
      <SummaryCard label="Despesas fixas" :value="2000" tone="negative" />
      <SummaryCard
        label="Despesas variáveis"
        :value="800"
        tone="negative"
        hint="Inclui as faturas de cartão do período"
      />
      <SummaryCard label="Restante" :value="1800" hint="Receitas − saídas do período" />
    </div>

    <h2 class="mb-3 mt-8 text-lg">Últimas movimentações</h2>

    <EmptyState
      title="Nenhuma movimentação registrada"
      description="As movimentações lançadas no período aparecerão aqui."
    >
      <template #actions>
        <BaseButton size="sm" variant="secondary">Adicionar movimentação</BaseButton>
      </template>
    </EmptyState>
  </section>
</template>
