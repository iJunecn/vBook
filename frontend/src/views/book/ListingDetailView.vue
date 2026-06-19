<script setup>
import { onMounted, ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import NavBar from '@/components/NavBar.vue'
import PageFooter from '@/components/PageFooter.vue'
import { bookApi, orderApi } from '@/api'
import { useUserStore } from '@/store/user'
import { ElMessage, ElMessageBox } from 'element-plus'
import { formatPrice, formatDate } from '@/utils/format'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const listing = ref(null)
const loading = ref(false)
const isOwner = computed(
  () => userStore.isLogin && listing.value?.seller_id === userStore.user?.id
)

async function load() {
  loading.value = true
  try {
    listing.value = await bookApi.getListing(route.params.id)
  } finally {
    loading.value = false
  }
}

async function buyBook(book) {
  if (!userStore.isLogin) {
    ElMessage.warning('请先登录')
    return router.push({ name: 'login', query: { redirect: route.fullPath } })
  }
  if (isOwner.value) {
    ElMessage.warning('这是你自己的书')
    return
  }
  try {
    await ElMessageBox.confirm(
      `确定以 ${formatPrice(book.price)} 购买《${book.title}》？`,
      '确认购买',
      { confirmButtonText: '立即购买', cancelButtonText: '取消' }
    )
  } catch {
    return
  }
  try {
    await orderApi.create({ book_id: book.id })
    ElMessage.success('购买成功！请在「我的订单」查看')
    load()
  } catch (e) {
    ElMessage.error('购买失败：' + (e.response?.data?.detail || e.message))
  }
}

async function delist() {
  try {
    await ElMessageBox.confirm('确定下架整摞书？此操作会隐藏所有书籍。', '确认', {
      confirmButtonText: '下架', cancelButtonText: '取消', type: 'warning',
    })
  } catch { return }
  await bookApi.deleteListing(listing.value.id)
  ElMessage.success('已下架')
  router.push('/')
}

async function removeOneBook(book) {
  try {
    await ElMessageBox.confirm(`确定删除《${book.title}》？`, '确认', {
      confirmButtonText: '删除', cancelButtonText: '取消', type: 'warning',
    })
  } catch { return }
  await bookApi.deleteBook(book.id)
  ElMessage.success('已删除')
  load()
}

async function toggleSold(book) {
  const newStatus = book.status === 'available' ? 'sold' : 'available'
  try {
    await bookApi.updateBook(book.id, { status: newStatus })
    ElMessage.success(newStatus === 'sold' ? '已标记为已售' : '已重新上架')
    load()
  } catch (e) {
    ElMessage.error('操作失败：' + (e.response?.data?.detail || e.message))
  }
}

onMounted(load)
</script>

<template>
  <NavBar />
  <main class="detail">
    <div v-if="!listing" class="container">
      <el-skeleton :rows="8" animated />
    </div>
    <div v-else class="container content">
      <div class="vb-card hero">
        <img :src="listing.cover_image" class="cover" />
        <div class="info">
          <h1>{{ listing.title }}</h1>
          <div class="meta">
            <span class="vb-badge" v-if="listing.campus">{{ listing.campus }}</span>
            <span class="text-muted">{{ formatDate(listing.created_at) }} 上架</span>
            <span v-if="listing.seller" class="text-muted">
              卖家：<router-link v-if="!isOwner" :to="`/users/${listing.seller.id}`">
                @{{ listing.seller.nickname || listing.seller.username }}
              </router-link>
              <span v-else>@{{ listing.seller.nickname || listing.seller.username }}（我）</span>
            </span>
          </div>
          <p v-if="listing.description" class="desc">{{ listing.description }}</p>
          <div class="price-block">
            <div class="price-tag">
              {{ formatPrice(listing.default_price) }}<small> /本起</small>
            </div>
            <div class="text-muted">共 {{ listing.books.length }} 本</div>
          </div>
          <div v-if="isOwner" class="owner-actions">
            <el-button type="warning" @click="delist">下架整摞</el-button>
          </div>
        </div>
      </div>

      <div class="vb-card">
        <h2>📚 书籍清单</h2>
        <p class="text-muted">点击"购买"直接下单。已售的书会显示为灰色。</p>
        <div class="book-list">
          <div
            v-for="(book, i) in listing.books"
            :key="book.id"
            class="book-row"
            :class="{ sold: book.status === 'sold' }"
          >
            <div class="idx">{{ i + 1 }}</div>
            <div class="info">
              <div class="title">
                {{ book.title }}
                <span v-if="book.status === 'sold'" class="vb-badge sold">已售</span>
              </div>
              <div class="detail text-muted">
                <span v-if="book.author">{{ book.author }}</span>
                <span v-if="book.publisher"> · {{ book.publisher }}</span>
                <span v-if="book.edition"> · {{ book.edition }}</span>
                <span v-if="book.isbn"> · ISBN {{ book.isbn }}</span>
              </div>
            </div>
            <div class="price price-tag">{{ formatPrice(book.price) }}</div>
            <div class="actions">
              <el-button
                v-if="!isOwner && book.status === 'available'"
                type="primary"
                @click="buyBook(book)"
              >购买</el-button>
              <template v-else-if="isOwner">
                <el-button size="small" @click="toggleSold(book)">
                  {{ book.status === 'available' ? '标记已售' : '重新上架' }}
                </el-button>
                <el-button size="small" type="danger" link @click="removeOneBook(book)">删除</el-button>
              </template>
              <span v-else class="text-muted">已售出</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </main>
  <PageFooter />
</template>

<style scoped>
.detail { padding: 24px 0 60px; }
.content { display: flex; flex-direction: column; gap: 16px; }
.hero {
  display: grid;
  grid-template-columns: 320px 1fr;
  gap: 24px;
}
.cover {
  width: 100%;
  aspect-ratio: 1 / 1;
  object-fit: cover;
  border-radius: var(--radius);
}
.info h1 { margin: 0 0 8px; color: var(--ink-900); font-size: 24px; }
.meta { display: flex; gap: 10px; align-items: center; font-size: 13px; flex-wrap: wrap; }
.desc {
  margin: 12px 0;
  color: var(--ink-700);
  background: var(--brand-50);
  padding: 12px 14px;
  border-radius: var(--radius);
  font-size: 14px;
  line-height: 1.6;
}
.price-block {
  display: flex; align-items: baseline; justify-content: space-between;
  margin: 16px 0;
}
.owner-actions { display: flex; gap: 8px; }

.book-list { display: flex; flex-direction: column; }
.book-row {
  display: grid;
  grid-template-columns: 36px 1fr auto 160px;
  align-items: center;
  gap: 12px;
  padding: 14px 0;
  border-bottom: 1px solid var(--ink-100);
}
.book-row:last-child { border-bottom: none; }
.book-row.sold { opacity: 0.6; }
.idx {
  width: 28px; height: 28px; line-height: 28px; text-align: center;
  background: var(--brand-100); color: var(--brand-700);
  border-radius: 50%; font-weight: 700; font-size: 13px;
}
.title { font-weight: 600; font-size: 16px; }
.detail { font-size: 13px; margin-top: 4px; }
.price { font-size: 18px; }
.actions { text-align: right; }

@media (max-width: 720px) {
  .hero { grid-template-columns: 1fr; }
  .book-row { grid-template-columns: 28px 1fr; }
  .price, .actions { grid-column: 2; }
  .price { text-align: left; }
  .actions { text-align: left; }
}
</style>
