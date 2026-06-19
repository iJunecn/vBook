<script setup>
import { onMounted, ref } from 'vue'
import NavBar from '@/components/NavBar.vue'
import PageFooter from '@/components/PageFooter.vue'
import { useUserStore } from '@/store/user'
import { bookApi } from '@/api'
import { useRouter } from 'vue-router'
import ListingCard from '@/components/ListingCard.vue'

const userStore = useUserStore()
const router = useRouter()
const listings = ref([])
const loading = ref(false)

const edit = ref({ nickname: '', campus: '', avatar: '' })
const saving = ref(false)

async function load() {
  if (!userStore.user) {
    await userStore.refreshMe()
  }
  edit.value.nickname = userStore.user?.nickname || ''
  edit.value.campus = userStore.user?.campus || ''
  edit.value.avatar = userStore.user?.avatar || ''
  loading.value = true
  try {
    listings.value = await bookApi.userListings(userStore.user.id)
  } finally {
    loading.value = false
  }
}

async function save() {
  saving.value = true
  try {
    await userStore.refreshMe()
    const { authApi } = await import('@/api')
    await authApi.updateMe(edit.value)
    await userStore.refreshMe()
    alert('保存成功')
  } finally {
    saving.value = false
  }
}

onMounted(load)
</script>

<template>
  <NavBar />
  <main class="profile">
    <div class="container">
      <div class="vb-card header">
        <div class="avatar-wrap">
          <el-avatar :size="64" :src="userStore.user?.avatar">
            {{ (userStore.user?.nickname || userStore.user?.username || '?')[0] }}
          </el-avatar>
        </div>
        <div>
          <h2>{{ userStore.user?.nickname || userStore.user?.username }}</h2>
          <div class="text-muted">@{{ userStore.user?.username }} · {{ userStore.user?.email }}</div>
          <div v-if="userStore.user?.campus" class="vb-badge">{{ userStore.user.campus }}</div>
        </div>
      </div>

      <div class="vb-card">
        <h2>编辑资料</h2>
        <el-form label-position="top" style="max-width: 480px;">
          <el-form-item label="昵称">
            <el-input v-model="edit.nickname" />
          </el-form-item>
          <el-form-item label="所在校区">
            <el-input v-model="edit.campus" />
          </el-form-item>
          <el-form-item label="头像 URL">
            <el-input v-model="edit.avatar" placeholder="https://..." />
          </el-form-item>
          <el-button type="primary" :loading="saving" @click="save">保存</el-button>
        </el-form>
      </div>

      <div class="vb-card">
        <div class="head">
          <h2>我的上架</h2>
          <el-button type="primary" @click="router.push('/sell')">+ 上架新书</el-button>
        </div>
        <el-empty v-if="!loading && listings.length === 0" description="还没有上架过书" />
        <div v-else class="grid">
          <ListingCard v-for="l in listings" :key="l.id" :listing="l" />
        </div>
      </div>
    </div>
  </main>
  <PageFooter />
</template>

<style scoped>
.profile { padding: 24px 0 60px; }
.container > .vb-card { margin-bottom: 16px; }
.header {
  display: flex; align-items: center; gap: 16px;
}
.head {
  display: flex; align-items: center; justify-content: space-between;
  margin-bottom: 16px;
}
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 16px;
}
h2 { margin: 0 0 12px; color: var(--brand-800); }
</style>
