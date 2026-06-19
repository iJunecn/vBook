<script setup>
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
    <view v-if="!userStore.isLogin" class="guest vb-card">
      <text class="logo">📚</text>
      <text class="vb-muted">登录后管理你的书单与订单</text>
      <wd-button type="primary" @click="goLogin">微信一键登录</wd-button>
    </view>

    <template v-else>
      <!-- 用户卡片 -->
      <view class="profile vb-card">
        <image
          class="avatar"
          :src="user.avatar ? mediaUrl(user.avatar) : ''"
          mode="aspectFill"
        />
        <view class="info">
          <text class="nick">{{ user.nickname || user.username }}</text>
          <text v-if="user.campus" class="vb-badge">{{ user.campus }}</text>
        </view>
        <text class="edit-link" @tap="startEdit">编辑</text>
      </view>

      <!-- 编辑表单 -->
      <view v-if="editing" class="form vb-card">
        <text class="field-label">昵称</text>
        <input v-model="form.nickname" class="f" placeholder="昵称" />
        <text class="field-label">校区</text>
        <input v-model="form.campus" class="f" placeholder="校区" />
        <text class="field-label">头像地址（可选）</text>
        <input v-model="form.avatar" class="f" placeholder="https://..." />
        <view class="form-btns">
          <wd-button plain block @click="editing = false">取消</wd-button>
          <wd-button type="primary" block @click="save">保存</wd-button>
        </view>
      </view>

      <!-- 我的发布 -->
      <view class="section-title">我的发布 ({{ myListings.length }})</view>
      <view v-if="myListings.length" class="grid">
        <view v-for="item in myListings" :key="item.id" class="grid-item">
          <ListingCard :listing="item" />
        </view>
      </view>
      <view v-else class="empty vb-muted">还没有发布过书单</view>

      <wd-button class="logout" block plain @click="logout">退出登录</wd-button>
    </template>
  </view>
</template>

<style scoped lang="scss">
.page {
  padding: 24rpx;
}
.guest {
  padding: 80rpx 40rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 24rpx;
}
.guest .logo {
  font-size: 100rpx;
}
.profile {
  display: flex;
  align-items: center;
  gap: 20rpx;
  padding: 28rpx 24rpx;
  margin-bottom: 20rpx;
}
.avatar {
  width: 100rpx;
  height: 100rpx;
  border-radius: 50%;
  background: var(--vb-brand-50);
}
.info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 10rpx;
}
.nick {
  font-size: 32rpx;
  font-weight: 700;
}
.edit-link {
  font-size: 26rpx;
  color: var(--vb-brand-600);
}
.form {
  padding: 24rpx;
  margin-bottom: 24rpx;
}
.field-label {
  display: block;
  font-size: 24rpx;
  color: var(--vb-ink-700);
  margin-bottom: 8rpx;
}
.f {
  width: 100%;
  box-sizing: border-box;
  border: 1rpx solid var(--vb-brand-100);
  border-radius: 12rpx;
  padding: 16rpx;
  font-size: 26rpx;
  margin-bottom: 16rpx;
  background: #fff;
}
.form-btns {
  display: flex;
  gap: 16rpx;
}
.form-btns > * {
  flex: 1;
}
.section-title {
  font-size: 28rpx;
  font-weight: 700;
  margin: 12rpx 0 16rpx;
}
.grid {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
}
.grid-item {
  width: 48.5%;
  margin-bottom: 20rpx;
}
.empty {
  text-align: center;
  padding: 48rpx 0;
}
.logout {
  margin-top: 24rpx;
}
</style>
