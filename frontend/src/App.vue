<script setup>
import { useRoute } from 'vue-router'

import AppLayout from './layouts/AppLayout.vue'

const route = useRoute()
</script>

<template>
  <!-- Telas públicas (login/registro) ficam fora do layout do app; o
       :key força a remontagem por rota, evitando conteúdo obsoleto. -->
  <component :is="route.meta.public ? 'div' : AppLayout">
    <RouterView :key="route.fullPath" />
  </component>
</template>
