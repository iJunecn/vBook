import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/store/user'
import { ElMessage } from 'element-plus'

const routes = [
  { path: '/', name: 'home', component: () => import('@/views/home/HomeView.vue') },
  { path: '/login', name: 'login', component: () => import('@/views/auth/LoginView.vue') },
  { path: '/register', name: 'register', component: () => import('@/views/auth/RegisterView.vue') },
  {
    path: '/sell',
    name: 'sell',
    component: () => import('@/views/sell/SellView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/listings/:id',
    name: 'listing',
    component: () => import('@/views/book/ListingDetailView.vue'),
  },
  {
    path: '/me',
    name: 'me',
    component: () => import('@/views/user/ProfileView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/me/orders',
    name: 'orders',
    component: () => import('@/views/user/OrdersView.vue'),
    meta: { requiresAuth: true },
  },
  { path: '/:pathMatch(.*)*', redirect: '/' },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior: () => ({ top: 0 }),
})

router.beforeEach((to, from, next) => {
  const user = useUserStore()
  user.loadFromStorage()
  if (to.meta.requiresAuth && !user.isLogin) {
    ElMessage.warning('请先登录')
    return next({ name: 'login', query: { redirect: to.fullPath } })
  }
  next()
})

export default router
