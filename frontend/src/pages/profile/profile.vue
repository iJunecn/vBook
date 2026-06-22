<script setup>
/**
 * 我的页（vUSTB 风格）
 *  - 顶部用户卡（头像 / 昵称 / 校区）
 *  - 我的发布（surface-card 网格）
 *  - 退出登录
 */
import { ref, computed } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { bookApi } from '@/api'
import { useUserStore } from '@/store/user'
import ListingCard from '@/components/ListingCard.vue'
import { mediaUrl } from '@/utils/format'

const userStore = useUserStore()
const editing = ref(false)
const form = ref({ nickname: '', campus: '', avatar: '' })
const myListings = ref([])

const user = computed(() => userStore.user)

onShow(() => {
  if (userStore.isLogin) {
    userStore.refreshMe().then(syncForm).catch(() => {})
    loadMyListings()
  }
})

function syncForm() {
  form.value = {
    nickname: user.value?.nickname || '',
    campus: user.value?.campus || '',
    avatar: user.value?.avatar || '',
  }
}

async function loadMyListings() {
  if (!user.value?.id) return
  try {
    myListings.value = await bookApi.userListings(user.value.id)
  } catch (e) {
    /* 拦截器已提示 */
  }
}

function startEdit() {
  syncForm()
  editing.value = true
}

async function save() {
  try {
    await userStore.updateProfile(form.value)
    editing.value = false
    uni.showToast({ title: '已保存', icon: 'success' })
  } catch (e) {
    /* 拦截器已提示 */
  }
}

function goLogin() {
  uni.navigateTo({ url: '/pages/login/login' })
}

function logout() {
  uni.showModal({
    title: '退出登录？',
    success: (r) => {
      if (r.confirm) {
        userStore.logout()
        myListings.value = []
      }
    },
  })
}
</script>

<template>
  <view class="page">
    <!-- 未登录 -->
    <view v-if="!userStore.isLogin" class="guest glass-card">
      <text class="logo">📚</text>
      <text class="nick muted">登录后管理你的书单与订单</text>
      <button class="btn-primary guest-btn" @click="goLogin">登录 / 注册</button>
    </view>

    <template v-else>
      <!-- 用户卡片 -->
      <view class="profile surface-card">
        <view class="avatar-wrap">
          <image
            v-if="user.avatar"
            class="avatar"
            :src="mediaUrl(user.avatar)"
            mode="aspectFill"
          />
          <view v-else class="avatar avatar-fallback">{{ (user.nickname || user.username || '?').slice(0, 1).toUpperCase() }}</view>
        </view>
        <view class="info">
          <text class="nick">{{ user.nickname || user.username }}</text>
          <view class="badges">
            <text v-if="user.campus" class="campus-badge">{{ user.campus }}</text>
            <text class="muted username">@{{ user.username }}</text>
          </view>
        </view>
        <text class="edit-link" @tap="startEdit">编辑</text>
      </view>

      <!-- 编辑表单 -->
      <view v-if="editing" class="form surface-card">
        <view class="field">
          <text class="field-label">昵称</text>
          <input v-model="form.nickname" class="input" placeholder="昵称" />
        </view>
        <view class="field">
          <text class="field-label">校区</text>
          <input v-model="form.campus" class="input" placeholder="校区" />
        </view>
        <view class="field">
          <text class="field-label">头像地址（可选）</text>
          <input v-model="form.avatar" class="input" placeholder="https://..." />
        </view>
        <view class="form-btns">
          <button class="btn-ghost" @click="editing = false">取消</button>
          <button class="btn-primary" @click="save">保存</button>
        </view>
      </view>

      <!-- 数据概览 -->
      <view class="stats">
        <view class="stat surface-card">
          <text class="stat-value">{{ myListings.length }}</text>
          <text class="stat-label muted">发布</text>
        </view>
        <view class="stat surface-card">
          <text class="stat-value">¥{{ myListings.reduce((s, l) => s + (Number(l.default_price) || 0) * (l.book_count || 0), 0).toFixed(0) }}</text>
          <text class="stat-label muted">在售总额</text>
        </view>
      </view>

      <!-- 我的发布 -->
      <view class="section-head">
        <text class="section-kicker">我的发布</text>
        <text class="muted">{{ myListings.length }} 单</text>
      </view>

      <view v-if="myListings.length" class="grid">
        <view v-for="item in myListings" :key="item.id" class="grid-item">
          <ListingCard :listing="item" />
        </view>
      </view>
      <view v-else class="empty">
        <text class="empty-icon">📦</text>
        <text class="muted">还没有发布过书单</text>
      </view>

      <button class="btn-ghost logout-btn" @click="logout">退出登录</button>
    </template>
  </view>
</template>

<style scoped lang="scss">
.page {
  padding: 24rpx;
  display: flex;
  flex-direction: column;
  gap: 20rpx;
}

/* ===== Guest ===== */
.guest {
  padding: 80rpx 40rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 18rpx;
  border-radius: 18px;
  text-align: center;
}
.guest .logo {
  font-size: 90rpx;
}
.guest .nick {
  font-size: 26rpx;
}
.guest-btn {
  padding: 18rpx 56rpx;
  margin-top: 12rpx;
  border: none;
}
.guest-btn::after {
  border: none;
}

/* ===== Profile ===== */
.profile {
  display: flex;
  align-items: center;
  gap: 20rpx;
  padding: 28rpx 24rpx;
}
.avatar-wrap {
  width: 96rpx;
  height: 96rpx;
  flex-shrink: 0;
}
.avatar {
  width: 96rpx;
  height: 96rpx;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--vb-brand-600), var(--vb-accent-500));
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 40rpx;
  font-weight: 700;
  color: #fff;
  overflow: hidden;
}
.info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8rpx;
  min-width: 0;
}
.nick {
  font-size: 32rpx;
  font-weight: 700;
  color: var(--vb-heading);
}
.badges {
  display: flex;
  align-items: center;
  gap: 10rpx;
  flex-wrap: wrap;
}
.campus-badge {
  display: inline-block;
  padding: 2rpx 12rpx;
  border-radius: 999px;
  font-size: 20rpx;
  font-weight: 500;
  background: var(--vb-brand-50);
  color: var(--vb-brand-700);
}
.username {
  font-size: 22rpx;
}
.edit-link {
  font-size: 26rpx;
  color: var(--vb-brand-700);
  font-weight: 600;
  padding: 6rpx 14rpx;
  border-radius: 8rpx;
  background: var(--vb-brand-50);
}

/* ===== Form ===== */
.form {
  padding: 28rpx 24rpx;
  display: flex;
  flex-direction: column;
  gap: 18rpx;
}
.field {
  display: flex;
  flex-direction: column;
  gap: 8rpx;
}
.field-label {
  font-size: 24rpx;
  color: var(--vb-ink-700);
  font-weight: 500;
}
.form-btns {
  display: flex;
  gap: 16rpx;
  margin-top: 8rpx;
}
.form-btns > * {
  flex: 1;
  border: none;
}
.form-btns > ::after {
  border: none;
}

/* ===== Stats ===== */
.stats {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16rpx;
}
.stat {
  padding: 24rpx 20rpx;
  display: flex;
  flex-direction: column;
  gap: 6rpx;
  border-radius: 12px;
}
.stat-value {
  font-size: 36rpx;
  font-weight: 700;
  color: var(--vb-heading);
}
.stat-label {
  font-size: 22rpx;
}
.muted {
  color: var(--vb-ink-500);
}

/* ===== Section ===== */
.section-head {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  margin-top: 4rpx;
}
.section-kicker {
  font-size: 24rpx;
  font-weight: 700;
  letter-spacing: 0.04em;
  color: var(--vb-heading);
}
.grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20rpx;
}
.grid-item {
  width: 100%;
}
.empty {
  text-align: center;
  padding: 60rpx 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12rpx;
}
.empty-icon {
  font-size: 70rpx;
  opacity: 0.5;
}

/* ===== Logout ===== */
.logout-btn {
  width: 100%;
  padding: 18rpx;
  margin-top: 12rpx;
  border: none;
  font-size: 26rpx;
}
.logout-btn::after {
  border: none;
}
</style>