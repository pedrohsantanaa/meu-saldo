<script setup>
import EmptyState from '../components/EmptyState.vue'
import SectionHeader from '../components/SectionHeader.vue'

defineProps({ title: { type: String, default: '' } })
</script>

<template>
  <section>
    <SectionHeader :title="title || $route.meta.title" />

    <EmptyState
      title="Funcionalidade em construção"
      description="Esta seção será implementada nas próximas fases do plano."
    />
  </section>
</template>
