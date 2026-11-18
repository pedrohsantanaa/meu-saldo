<script setup>
import { computed, ref } from 'vue'
import { useRoute } from 'vue-router'

import { navItems } from '../utils/navigation'

const route = useRoute()
const dashboardOpen = ref(true)

const dashboardActive = computed(() =>
  navItems.find((item) => item.name === 'dashboard')?.children?.some((child) => child.name === route.name)
)
</script>

<template>
  <nav class="flex h-full flex-col bg-sidebar text-sidebar-text">
    <div class="flex items-center gap-2 px-4 py-5">
      <svg class="h-7 w-7" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
        <rect x="3" y="12" width="4" height="8" rx="1" class="fill-action" />
        <rect x="10" y="8" width="4" height="12" rx="1" class="fill-action" />
        <rect x="17" y="4" width="4" height="16" rx="1" class="fill-action" />
      </svg>
      <span class="text-lg font-semibold text-white">meuSaldo</span>
    </div>

    <ul class="flex-1 space-y-1 px-3">
      <li v-for="item in navItems" :key="item.name">
        <template v-if="item.children">
          <button
            type="button"
            class="flex w-full items-center gap-3 rounded-md px-3 py-2 text-sm font-medium hover:bg-sidebar-hover"
            :class="dashboardActive ? 'text-white' : ''"
            :aria-expanded="dashboardOpen"
            @click="dashboardOpen = !dashboardOpen"
          >
            <component :is="item.icon" class="h-5 w-5" aria-hidden="true" />
            {{ item.title }}
            <svg
              class="ml-auto h-4 w-4 transition-transform"
              :class="dashboardOpen ? 'rotate-90' : ''"
              viewBox="0 0 20 20"
              fill="currentColor"
              aria-hidden="true"
            >
              <path
                fill-rule="evenodd"
                d="M7.21 14.77a.75.75 0 0 1 .02-1.06L11.168 10 7.23 6.29a.75.75 0 1 1 1.04-1.08l4.5 4.25a.75.75 0 0 1 0 1.08l-4.5 4.25a.75.75 0 0 1-1.06-.02Z"
                clip-rule="evenodd"
              />
            </svg>
          </button>

          <ul v-show="dashboardOpen" class="mt-1 space-y-1 pl-10">
            <li v-for="child in item.children" :key="child.name">
              <RouterLink
                :to="child.to"
                class="block rounded-md px-3 py-1.5 text-sm hover:bg-sidebar-hover"
                :class="child.name === route.name ? 'bg-primary font-medium text-white' : ''"
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
        >
          <component :is="item.icon" class="h-5 w-5" aria-hidden="true" />
          {{ item.title }}
        </RouterLink>
      </li>
    </ul>

    <div class="flex items-center gap-3 border-t border-white/10 px-4 py-3">
      <span
        class="flex h-9 w-9 items-center justify-center rounded-full bg-primary text-sm font-semibold text-white"
        aria-hidden="true"
      >
        P
      </span>
      <div class="min-w-0 flex-1">
        <p class="truncate text-sm font-medium text-white">Pedro Henrique</p>
        <p class="text-xs text-sidebar-text">Minha conta</p>
      </div>
    </div>
  </nav>
</template>
