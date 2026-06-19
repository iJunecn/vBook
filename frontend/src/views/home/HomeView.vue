<script setup>
import { onMounted, ref, watch } from 'vue'
import NavBar from '@/components/NavBar.vue'
import PageFooter from '@/components/PageFooter.vue'
import ListingCard from '@/components/ListingCard.vue'
import { bookApi } from '@/api'
import { useRouter } from 'vue-router'

const router = useRouter()
const listings = ref([])
const loading = ref(false)
const keyword = ref('')
const campus = ref('')

async function load() {
  loading.value = true
  try {
    const data = await bookApi.listListings({
      q: keyword.value || undefined,
      campus: campus.value || undefined,
      page: 1,
      page_size: 24,
    })
    listings.value = data
  } finally {
    loading.value = false
  }
}

let timer
function onSearch() {
  clearTimeout(timer)
  timer = setTimeout(load, 300)
}

function goSell() {
  router.push('/sell')
}

onMounted(load)
</script>

<template>
  <NavBar />
  <main>
    <section class="hero">
      <div class="container hero-inner">
        <div class="hero-text">
          <h1>把书脊上那摞旧书<br />变成 <span class="hl">¥5 一本</span> 的小生意</h1>
          <p class="lead">拍一张书脊照片，AI 自动识别成书单，一键上架。<br />学弟学妹按书名搜索，按需购买。</p>
          <div class="cta">
            <el-button type="primary" size="large" @click="goSell">📚 我要卖书</el-button>
            <el-button size="large" plain @click="router.push('/login')">先注册账号</el-button>
          </div>
        </div>
        <div class="hero-illu">
          <div class="books-stack">
            <div v-for="i in 5" :key="i" class="book" :style="`--i:${i}`">
              <div class="spine" />
            </div>
          </div>
        </div>
      </div>
    </section>

    <section class="container section">
      <div class="vb-card filter-bar">
        <el-input
          v-model="keyword"
          placeholder="按书名 / 作者 / 出版社搜索"
          clearable
          @input="onSearch"
          @clear="onSearch"
        >
          <template #prefix><el-icon><Search /></el-icon></template>
        </el-input>
        <el-input
          v-model="campus"
          placeholder="校区（如：海淀校区）"
          clearable
          @input="onSearch"
          @clear="onSearch"
          style="max-width: 200px;"
        />
        <el-button type="primary" @click="load">搜索</el-button>
      </div>

      <div class="list-head">
        <h2>正在交易的书</h2>
        <span class="text-muted">共 {{ listings.length }} 条</span>
      </div>

      <el-empty v-if="!loading && listings.length === 0" description="还没有上架的书，快来当第一个卖家吧" />
      <el-skeleton v-else-if="loading" :rows="6" animated />

      <div v-else class="grid">
        <ListingCard v-for="l in listings" :key="l.id" :listing="l" />
      </div>
    </section>
  </main>
  <PageFooter />
</template>

<style scoped>
.hero {
  background: linear-gradient(135deg, #DBEAFE 0%, #EFF6FF 50%, #FFFFFF 100%);
  padding: 56px 0 32px;
}
.hero-inner {
  display: grid;
  grid-template-columns: 1.2fr 1fr;
  gap: 32px;
  align-items: center;
}
.hero-text h1 {
  font-size: 40px;
  line-height: 1.3;
  margin: 0 0 16px;
  color: var(--ink-900);
}
.hero-text .hl {
  color: var(--brand-700);
  background: linear-gradient(180deg, transparent 60%, var(--brand-200) 60%);
  padding: 0 4px;
}
.lead { color: var(--ink-700); font-size: 16px; line-height: 1.7; margin: 0 0 24px; }
.cta { display: flex; gap: 12px; flex-wrap: wrap; }

.hero-illu { display: flex; justify-content: center; }
.books-stack {
  position: relative;
  width: 220px;
  height: 280px;
}
.book {
  position: absolute;
  width: 200px;
  height: 36px;
  left: calc(50% - 100px);
  top: calc(var(--i) * 42px);
  background: linear-gradient(180deg, var(--brand-400), var(--brand-700));
  border-radius: 4px 8px 8px 4px;
  box-shadow: 0 4px 12px rgba(30, 64, 175, 0.2);
  transform: rotate(-1.5deg);
}
.book:nth-child(2n) { background: linear-gradient(180deg, var(--brand-500), var(--brand-800)); }
.book:nth-child(3n) { background: linear-gradient(180deg, var(--brand-300), var(--brand-600)); }
.book .spine {
  width: 100%; height: 100%;
  background: repeating-linear-gradient(90deg, transparent 0 30px, rgba(255,255,255,0.15) 30px 31px);
  border-radius: inherit;
}

.filter-bar {
  display: flex;
  gap: 12px;
  align-items: center;
  margin-bottom: 16px;
}

.list-head {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  margin: 20px 0 12px;
}
.list-head h2 { margin: 0; font-size: 22px; color: var(--ink-900); }

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 16px;
}

@media (max-width: 720px) {
  .hero-inner { grid-template-columns: 1fr; }
  .hero-text h1 { font-size: 28px; }
  .books-stack { transform: scale(0.8); }
}
</style>
