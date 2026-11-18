<script setup>
import { navItems } from '../utils/navigation'

defineProps({ open: { type: Boolean, default: false } })
defineEmits(['update:open'])
</script>

<template>
  <div>
    <div class="flex items-center justify-between p-4">
      <RouterLink to="/" class="text-lg font-semibold text-primary">meuSaldo</RouterLink>
      <button
        type="button"
        class="rounded-md border border-neutral-200 px-3 py-1.5 text-sm"
        :aria-expanded="open"
        aria-label="Abrir ou fechar menu"
        @click="$emit('update:open', !open)"
      >
        Menu
      </button>
    </div>

    <nav v-show="open" class="border-t border-neutral-200 p-2">
      <ul class="space-y-1">
        <li v-for="item in navItems" :key="item.name">
          <RouterLink
            :to="item.to"
            class="block rounded-md px-3 py-2 text-sm font-medium text-neutral-700 hover:bg-neutral-100"
            active-class="bg-primary/10 text-primary"
            @click="$emit('update:open', false)"
          >
            {{ item.title }}
          </RouterLink>
        </li>
      </ul>
    </nav>
  </div>
</template>
