<script setup>
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/store/user'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const isLogin = computed(() => userStore.isLogin)
const username = computed(() => userStore.user?.nickname || userStore.user?.username)

const activeMenu = computed(() => {
  if (route.path === '/') return 'home'
  if (route.path.startsWith('/sell')) return 'sell'
  if (route.path.startsWith('/me')) return 'me'
  return ''
})

function logout() {
  userStore.logout()
  router.push('/login')
}
</script>

<template>
  <header class="navbar">
    <div class="container nav-inner">
      <div class="brand" @click="router.push('/')">
        <img src="/favicon.svg" alt="" class="brand-logo" />
        <span class="brand-name">贝壳易书</span>
        <span class="brand-slogan">校园二手书交易</span>
      </div>

      <nav class="nav-links">
        <router-link to="/" :class="{ active: activeMenu === 'home' }">首页</router-link>
        <router-link to="/sell" :class="{ active: activeMenu === 'sell' }">我要卖书</router-link>
      </nav>

      <div class="nav-user">
        <template v-if="isLogin">
          <el-dropdown @command="(c) => c === 'logout' ? logout() : router.push('/me')">
            <span class="user-trigger">
              <el-avatar :size="32" :src="userStore.user?.avatar">{{ (username || '?')[0] }}</el-avatar>
              <span class="user-name">{{ username }}</span>
              <el-icon><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="me">个人中心</el-dropdown-item>
                <el-dropdown-item command="orders" @click="router.push('/me/orders')">我的订单</el-dropdown-item>
                <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </template>
        <template v-else>
          <el-button type="primary" plain @click="router.push('/login')">登录</el-button>
          <el-button type="primary" @click="router.push('/register')">注册</el-button>
        </template>
      </div>
    </div>
  </header>
</template>

<style scoped>
.navbar {
  position: sticky;
  top: 0;
  z-index: 100;
  background: rgba(255, 255, 255, 0.92);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--brand-100);
  box-shadow: var(--shadow-sm);
}
.nav-inner {
  display: flex;
  align-items: center;
  height: 64px;
  gap: 32px;
}
.brand {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  user-select: none;
}
.brand-logo { width: 32px; height: 32px; }
.brand-name {
  font-size: 20px;
  font-weight: 700;
  color: var(--brand-800);
  letter-spacing: 0.5px;
}
.brand-slogan {
  font-size: 12px;
  color: var(--ink-500);
  margin-left: 4px;
}
.nav-links {
  display: flex;
  gap: 24px;
  flex: 1;
}
.nav-links a {
  color: var(--ink-700);
  font-size: 15px;
  padding: 8px 4px;
  border-bottom: 2px solid transparent;
  transition: all 0.2s;
}
.nav-links a:hover { color: var(--brand-600); }
.nav-links a.active {
  color: var(--brand-700);
  border-bottom-color: var(--brand-600);
  font-weight: 600;
}
.nav-user { display: flex; gap: 8px; align-items: center; }
.user-trigger {
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  color: var(--ink-700);
}
.user-name { font-size: 14px; }
@media (max-width: 720px) {
  .brand-slogan { display: none; }
  .nav-links { gap: 12px; }
}
</style>
