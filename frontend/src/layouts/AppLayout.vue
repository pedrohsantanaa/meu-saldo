<script setup>
import { ref } from 'vue'

import SidebarNavigation from '../components/SidebarNavigation.vue'
import MobileNavigation from '../components/MobileNavigation.vue'

const menuOpen = ref(false)
</script>

<template>
  <div class="min-h-screen md:flex">
    <aside class="hidden w-60 shrink-0 border-r border-neutral-200 bg-white md:block">
      <SidebarNavigation />
    </aside>

    <div class="flex min-h-screen flex-1 flex-col">
      <header class="border-b border-neutral-200 bg-white md:hidden">
        <MobileNavigation v-model:open="menuOpen" />
      </header>

      <main class="flex-1 p-4 md:p-8">
        <slot />
      </main>
    </div>
  </div>
</template>
