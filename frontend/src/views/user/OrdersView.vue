<script setup>
import { onMounted, ref, computed } from 'vue'
import NavBar from '@/components/NavBar.vue'
import PageFooter from '@/components/PageFooter.vue'
import { orderApi } from '@/api'
import { useUserStore } from '@/store/user'
import { formatPrice, formatDate } from '@/utils/format'

const userStore = useUserStore()
const tab = ref('bought')
const bought = ref([])
const sold = ref([])
const loading = ref(false)

const list = computed(() => (tab.value === 'bought' ? bought.value : sold.value))

async function load() {
  loading.value = true
  try {
    const [b, s] = await Promise.all([orderApi.mine(), orderApi.sales()])
    bought.value = b.filter((o) => o.buyer_id === userStore.user?.id)
    sold.value = s
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<template>
  <NavBar />
  <main class="orders">
    <div class="container">
      <div class="vb-card">
        <h2>我的订单</h2>
        <el-tabs v-model="tab" @tab-change="load">
          <el-tab-pane label="我购买的" name="bought" />
          <el-tab-pane label="我卖出的" name="sold" />
        </el-tabs>

        <el-empty v-if="!loading && list.length === 0" :description="tab === 'bought' ? '还没有购买记录' : '还没有卖出记录'" />
        <el-skeleton v-else-if="loading" :rows="4" animated />

        <div v-else class="order-list">
          <div v-for="o in list" :key="o.id" class="order">
            <div class="left">
              <div class="title">
                {{ o.book?.title || `书 #${o.book_id}` }}
                <span v-if="o.status === 'paid'" class="vb-badge">{{ tab === 'bought' ? '已支付' : '待交付' }}</span>
              </div>
              <div class="text-muted">
                {{ tab === 'bought' ? '卖家' : '买家' }} #{{ o.seller_id === userStore.user?.id ? o.buyer_id : o.seller_id }}
                · {{ formatDate(o.created_at) }}
              </div>
              <div v-if="o.note" class="text-muted">备注：{{ o.note }}</div>
            </div>
            <div class="right">
              <div class="price-tag">{{ formatPrice(o.price) }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </main>
  <PageFooter />
</template>

<style scoped>
.orders { padding: 24px 0 60px; }
h2 { margin: 0 0 12px; color: var(--brand-800); }
.order-list { display: flex; flex-direction: column; }
.order {
  display: flex; align-items: center; justify-content: space-between;
  padding: 14px 0;
  border-bottom: 1px solid var(--ink-100);
}
.order:last-child { border-bottom: none; }
.title { font-weight: 600; font-size: 15px; }
</style>
