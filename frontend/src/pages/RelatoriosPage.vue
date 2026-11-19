<script setup>
import EmptyState from '../components/EmptyState.vue'
import SectionHeader from '../components/SectionHeader.vue'
</script>

<template>
  <section>
    <SectionHeader
      title="Relatórios"
      description="Análises detalhadas do seu histórico financeiro."
    />

    <EmptyState
      title="Relatórios em construção"
      description="Esta seção está prevista para uma versão futura, conforme o escopo do MVP."
    />
  </section>
</template>
