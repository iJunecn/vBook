<script setup>
/**
 * 注册页 - 邮箱 + 用户名 + 密码
 *  - username 3-32 位，字母数字下划线短横
 *  - email 标准邮箱
 *  - password 6-64 位
 *  - nickname / campus 可选
 * 成功后自动登录跳回首页
 */
import { ref, computed } from 'vue'
import { useUserStore } from '@/store/user'

const userStore = useUserStore()

const form = ref({
  username: '',
  email: '',
  password: '',
  password2: '',
  nickname: '',
  campus: '',
})
const loading = ref(false)
const errMsg = ref('')
const showPwd = ref(false)

const usernameOk = computed(() => /^[A-Za-z0-9_\-]{3,32}$/.test(form.value.username))
const emailOk = computed(() => /^[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}$/.test(form.value.email))
const pwdOk = computed(() => form.value.password.length >= 6 && form.value.password.length <= 64)
const pwdMatch = computed(() => form.value.password === form.value.password2)
const canSubmit = computed(
  () => usernameOk.value && emailOk.value && pwdOk.value && pwdMatch.value && !loading.value,
)

async function onSubmit() {
  if (!canSubmit.value) {
    if (!usernameOk.value) errMsg.value = '用户名需 3-32 位字母/数字/下划线/短横'
    else if (!emailOk.value) errMsg.value = '邮箱格式不正确'
    else if (!pwdOk.value) errMsg.value = '密码长度 6-64 位'
    else if (!pwdMatch.value) errMsg.value = '两次密码不一致'
    return
  }
  errMsg.value = ''
  loading.value = true
  uni.showLoading({ title: '注册中…' })
  try {
    await userStore.register({
      username: form.value.username,
      email: form.value.email,
      password: form.value.password,
      nickname: form.value.nickname || form.value.username,
      campus: form.value.campus || null,
    })
    uni.hideLoading()
    uni.showToast({ title: '注册成功，已登录', icon: 'success' })
    setTimeout(() => {
      const pages = getCurrentPages()
      if (pages.length > 1) uni.navigateBack()
      else uni.switchTab({ url: '/pages/index/index' })
    }, 700)
  } catch (e) {
    uni.hideLoading()
    errMsg.value = e?.detail || '注册失败'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <view class="page">
    <view class="card">
      <view class="head">
        <text class="title">注册账号</text>
        <text class="sub vb-muted">邮箱 + 密码就能用，小程序和 H5 通用</text>
      </view>

      <view class="form">
        <view class="field">
          <text class="lbl">用户名 <text class="req">*</text></text>
          <input
            v-model="form.username"
            class="ipt"
            placeholder="3-32 位，字母/数字/_/-"
            :maxlength="32"
            placeholder-class="ipt-ph"
          />
        </view>
        <view class="field">
          <text class="lbl">邮箱 <text class="req">*</text></text>
          <input
            v-model="form.email"
            class="ipt"
            type="text"
            placeholder="example@x.edu.cn"
            :maxlength="120"
            placeholder-class="ipt-ph"
          />
        </view>
        <view class="field">
          <text class="lbl">密码 <text class="req">*</text></text>
          <view class="pwd-row">
            <input
              v-model="form.password"
              class="ipt"
              :password="!showPwd"
              placeholder="6-64 位"
              :maxlength="64"
              placeholder-class="ipt-ph"
            />
            <text class="toggle" @tap="showPwd = !showPwd">{{ showPwd ? '隐藏' : '显示' }}</text>
          </view>
        </view>
        <view class="field">
          <text class="lbl">确认密码 <text class="req">*</text></text>
          <input
            v-model="form.password2"
            class="ipt"
            :password="!showPwd"
            placeholder="再输一次"
            :maxlength="64"
            placeholder-class="ipt-ph"
          />
        </view>
        <view class="field">
          <text class="lbl">昵称（可选）</text>
          <input
            v-model="form.nickname"
            class="ipt"
            placeholder="不填就用用户名"
            :maxlength="32"
            placeholder-class="ipt-ph"
          />
        </view>
        <view class="field">
          <text class="lbl">校区（可选）</text>
          <input
            v-model="form.campus"
            class="ipt"
            placeholder="例如：东校区"
            :maxlength="32"
            placeholder-class="ipt-ph"
          />
        </view>

        <view v-if="errMsg" class="err">{{ errMsg }}</view>

        <wd-button
          type="primary"
          block
          size="large"
          :loading="loading"
          :disabled="!canSubmit"
          @click="onSubmit"
        >
          注册并登录
        </wd-button>

        <view class="aux">
          <text class="link" @tap="uni.navigateBack()">已有账号？返回登录</text>
        </view>
      </view>
    </view>
  </view>
</template>

<style scoped lang="scss">
.page {
  min-height: 100vh;
  padding: 48rpx 32rpx 40rpx;
  display: flex;
  align-items: flex-start;
  justify-content: center;
}
.card {
  width: 100%;
  max-width: 560rpx;
  background: #fff;
  border-radius: 24rpx;
  padding: 48rpx 40rpx;
  box-shadow: 0 8rpx 32rpx rgba(37, 99, 235, 0.08);
}
.head {
  margin-bottom: 32rpx;
}
.title {
  font-size: 40rpx;
  font-weight: 700;
  color: var(--vb-brand-600);
}
.sub {
  display: block;
  font-size: 24rpx;
  margin-top: 8rpx;
}
.form {
  display: flex;
  flex-direction: column;
  gap: 20rpx;
}
.field {
  display: flex;
  flex-direction: column;
  gap: 8rpx;
}
.lbl {
  font-size: 24rpx;
  color: var(--vb-ink-700);
}
.req {
  color: #e23d3d;
}
.ipt {
  width: 100%;
  box-sizing: border-box;
  border: 1rpx solid var(--vb-brand-100);
  border-radius: 12rpx;
  padding: 18rpx 20rpx;
  font-size: 28rpx;
  background: #fff;
}
.ipt-ph {
  color: var(--vb-ink-300);
}
.pwd-row {
  position: relative;
}
.toggle {
  position: absolute;
  right: 20rpx;
  top: 50%;
  transform: translateY(-50%);
  font-size: 24rpx;
  color: var(--vb-brand-600);
}
.err {
  font-size: 24rpx;
  color: #e23d3d;
  background: #fdeaea;
  padding: 12rpx 16rpx;
  border-radius: 8rpx;
}
.aux {
  display: flex;
  justify-content: center;
  margin-top: 8rpx;
}
.link {
  font-size: 24rpx;
  color: var(--vb-brand-600);
}
</style>
