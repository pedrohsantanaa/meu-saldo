<script setup>
import { ref } from 'vue'
import { useRoute } from 'vue-router'

import { navItems } from '../utils/navigation'

defineProps({ open: { type: Boolean, default: false } })
const emit = defineEmits(['update:open'])

const route = useRoute()
const dashboardOpen = ref(true)

function close() {
  emit('update:open', false)
}
</script>

<template>
  <div class="bg-sidebar text-sidebar-text">
    <div class="flex items-center justify-between p-4">
      <RouterLink to="/" class="flex items-center gap-2" @click="close">
        <svg class="h-7 w-7" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
          <rect x="3" y="12" width="4" height="8" rx="1" class="fill-action" />
          <rect x="10" y="8" width="4" height="12" rx="1" class="fill-action" />
          <rect x="17" y="4" width="4" height="16" rx="1" class="fill-action" />
        </svg>
        <div class="leading-tight">
          <span class="block text-lg font-semibold text-white">Cifaro</span>
          <span class="block text-[10px] tracking-wide text-white/60">by PHtech</span>
        </div>
      </RouterLink>

      <button
        type="button"
        class="rounded-md border border-white/20 px-3 py-1.5 text-sm text-white"
        :aria-expanded="open"
        aria-label="Abrir ou fechar menu"
        @click="emit('update:open', !open)"
      >
        Menu
      </button>
    </div>

    <nav v-show="open" class="border-t border-white/10 p-2">
      <ul class="space-y-1">
        <li v-for="item in navItems" :key="item.name">
          <template v-if="item.children">
            <button
              type="button"
              class="flex w-full items-center gap-3 rounded-md px-3 py-2 text-sm font-medium hover:bg-sidebar-hover"
              :aria-expanded="dashboardOpen"
              @click="dashboardOpen = !dashboardOpen"
            >
              <component :is="item.icon" class="h-5 w-5" aria-hidden="true" />
              {{ item.title }}
            </button>

            <ul v-show="dashboardOpen" class="space-y-1 pl-10">
              <li v-for="child in item.children" :key="child.name">
                <RouterLink
                  :to="child.to"
                  class="block rounded-md px-3 py-1.5 text-sm hover:bg-sidebar-hover"
                  :class="child.name === route.name ? 'bg-primary font-medium text-white' : ''"
                  @click="close"
                >
                  {{ child.title }}
                </RouterLink>
              </li>
            </ul>
          </template>

          <RouterLink
            v-else
            :to="item.to"
            class="flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium hover:bg-sidebar-hover"
            :class="item.name === route.name ? 'bg-primary text-white' : ''"
            @click="close"
          >
            <component :is="item.icon" class="h-5 w-5" aria-hidden="true" />
            {{ item.title }}
          </RouterLink>
        </li>
      </ul>
    </nav>
  </div>
</template>
