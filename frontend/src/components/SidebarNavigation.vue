<script setup>
import { navItems } from '../utils/navigation'
</script>

<template>
  <nav class="flex h-full flex-col p-4">
    <RouterLink to="/" class="mb-6 flex items-center gap-2">
      <span
        class="flex h-8 w-8 items-center justify-center rounded-card bg-primary text-sm font-semibold text-white"
        aria-hidden="true"
      >
        m$
      </span>
      <span class="text-xl font-semibold text-neutral-900">meuSaldo</span>
    </RouterLink>

    <ul class="space-y-1">
      <li v-for="item in navItems" :key="item.name">
        <RouterLink
          :to="item.to"
          class="block rounded-md px-3 py-2 text-sm font-medium text-neutral-700 hover:bg-neutral-100"
          active-class="bg-primary/10 text-primary"
        >
          {{ item.title }}
        </RouterLink>
      </li>
    </ul>
  </nav>
</template>
