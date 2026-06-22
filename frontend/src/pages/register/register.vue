<script setup>
/**
 * 注册页 - 邮箱 + 用户名 + 密码
 *  - username 3-32 位，字母数字下划线短横
 *  - email 标准邮箱
 *  - password 6-64 位
 *  - nickname / campus 可选
 * 成功后自动登录跳回首页
 *
 * 视觉风格：与登录页一致的 auth-panel + glass-card
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
  <view class="auth-shell">
    <view class="auth-panel glass-card animate-slide-up">
      <view class="head">
        <text class="name">注册账号</text>
        <text class="slogan">邮箱 + 密码就能用，小程序和 H5 通用</text>
      </view>

      <view class="form">
        <view class="field">
          <text class="lbl">用户名 <text class="req">*</text></text>
          <input
            v-model="form.username"
            class="input"
            placeholder="3-32 位，字母/数字/_/-"
            :maxlength="32"
            placeholder-class="ipt-ph"
          />
        </view>
        <view class="field">
          <text class="lbl">邮箱 <text class="req">*</text></text>
          <input
            v-model="form.email"
            class="input"
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
              class="input"
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
            class="input"
            :password="!showPwd"
            placeholder="再输一次"
            :maxlength="64"
            placeholder-class="ipt-ph"
          />
        </view>
        <view class="field-row">
          <view class="field">
            <text class="lbl">昵称（可选）</text>
            <input v-model="form.nickname" class="input" placeholder="不填就用用户名" :maxlength="32" placeholder-class="ipt-ph" />
          </view>
          <view class="field">
            <text class="lbl">校区（可选）</text>
            <input v-model="form.campus" class="input" placeholder="例如：东校区" :maxlength="32" placeholder-class="ipt-ph" />
          </view>
        </view>

        <view v-if="errMsg" class="err">{{ errMsg }}</view>

        <button class="btn-primary" :disabled="!canSubmit" @click="onSubmit">
          {{ loading ? '注册中…' : '注册并登录' }}
        </button>

        <view class="aux">
          <text class="muted">已有账号？</text>
          <text class="link" @tap="uni.navigateBack()">返回登录</text>
        </view>
      </view>
    </view>
  </view>
</template>

<style scoped lang="scss">
.auth-shell {
  min-height: 100vh;
  padding: 48rpx 32rpx 40rpx;
  display: flex;
  align-items: flex-start;
  justify-content: center;
}
.auth-panel {
  width: 100%;
  max-width: 580rpx;
  padding: 48rpx 40rpx;
}
.head {
  margin-bottom: 36rpx;
  text-align: center;
}
.name {
  display: block;
  font-size: 38rpx;
  font-weight: 700;
  color: var(--vb-heading);
  letter-spacing: 0.02em;
}
.slogan {
  display: block;
  font-size: 24rpx;
  color: var(--vb-ink-500);
  margin-top: 12rpx;
}
.form {
  display: flex;
  flex-direction: column;
  gap: 22rpx;
}
.field {
  display: flex;
  flex-direction: column;
  gap: 10rpx;
  flex: 1;
}
.field-row {
  display: flex;
  gap: 20rpx;
}
.lbl {
  font-size: 24rpx;
  color: var(--vb-ink-700);
  font-weight: 500;
}
.req {
  color: var(--vb-danger);
}
.pwd-row {
  position: relative;
}
.toggle {
  position: absolute;
  right: 24rpx;
  top: 50%;
  transform: translateY(-50%);
  font-size: 24rpx;
  color: var(--vb-brand-700);
  font-weight: 500;
  cursor: pointer;
}
.ipt-ph {
  color: var(--vb-ink-400);
}
.err {
  font-size: 24rpx;
  color: var(--vb-danger);
  background: #fdeaea;
  padding: 14rpx 18rpx;
  border-radius: 10rpx;
}
.aux {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 8rpx;
  font-size: 24rpx;
  margin-top: 4rpx;
}
.muted {
  color: var(--vb-ink-500);
}
.link {
  color: var(--vb-brand-700);
  font-weight: 600;
}

.btn-primary {
  width: 100%;
  border: none;
  font-family: inherit;
}
.btn-primary::after {
  border: none;
}

@media (max-width: 520px) {
  .field-row {
    flex-direction: column;
    gap: 22rpx;
  }
}
</style>