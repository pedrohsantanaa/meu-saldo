<script setup>
import { formatCurrency } from '../utils/formatCurrency'
</script>

<template>
  <section>
    <h1 class="mb-1 text-2xl font-semibold">Visão geral</h1>
    <p class="mb-6 text-sm text-neutral-500">
      Resumo financeiro do mês. As funcionalidades serão implementadas nas próximas fases.
    </p>

    <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
      <div class="rounded-lg border border-neutral-200 bg-white p-4">
        <p class="text-sm text-neutral-500">Total de receitas</p>
        <p class="text-xl font-semibold text-positive">{{ formatCurrency(0) }}</p>
      </div>
      <div class="rounded-lg border border-neutral-200 bg-white p-4">
        <p class="text-sm text-neutral-500">Despesas fixas</p>
        <p class="text-xl font-semibold text-negative">{{ formatCurrency(0) }}</p>
      </div>
      <div class="rounded-lg border border-neutral-200 bg-white p-4">
        <p class="text-sm text-neutral-500">Despesas variáveis</p>
        <p class="text-xl font-semibold text-negative">{{ formatCurrency(0) }}</p>
      </div>
      <div class="rounded-lg border border-neutral-200 bg-white p-4">
        <p class="text-sm text-neutral-500">Restante</p>
        <p class="text-xl font-semibold">{{ formatCurrency(0) }}</p>
      </div>
    </div>

    <div class="mt-8 rounded-lg border border-dashed border-neutral-300 bg-white p-8 text-center">
      <p class="text-neutral-600">Nenhuma movimentação registrada.</p>
    </div>
  </section>
</template>
