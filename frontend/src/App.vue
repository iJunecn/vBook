<script setup>
import { onMounted } from 'vue'
import { useUserStore } from '@/store/user'
import { RouterView } from 'vue-router'

const userStore = useUserStore()
onMounted(() => {
  userStore.loadFromStorage()
})
</script>

<template>
  <router-view />
</template>
