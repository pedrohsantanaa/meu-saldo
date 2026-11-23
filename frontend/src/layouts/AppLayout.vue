<script setup>
import { ref } from 'vue'

import SidebarNavigation from '../components/SidebarNavigation.vue'
import MobileNavigation from '../components/MobileNavigation.vue'

const menuOpen = ref(false)
</script>

<template>
  <div class="min-h-screen bg-neutral-50 md:flex">
    <aside class="hidden w-60 shrink-0 md:block">
      <div class="fixed h-screen w-60">
        <SidebarNavigation />
      </div>
    </aside>

    <div class="flex min-h-screen flex-1 flex-col">
      <header class="md:hidden">
        <MobileNavigation v-model:open="menuOpen" />
      </header>

      <main class="flex-1 p-4 md:p-8">
        <slot />
      </main>

      <footer class="px-4 py-3 text-center text-xs text-neutral-400 md:px-8">
        Cifaro by PHtech
      </footer>
    </div>
  </div>
</template>
