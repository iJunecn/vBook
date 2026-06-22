<script setup>
/**
 * 注册页 - 邮箱 + 用户名 + 密码
 *  - username 3-32 位，字母数字下划线短横
 *  - email 标准邮箱
 *  - password 6-64 位
 *  - nickname / campus 可选
 * 成功后自动登录跳到首页
 *
 * 视觉对齐 vUSTB /login：label-wrapped input + 大圆角玻璃态面板 + 返回按钮
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
    setTimeout(goHome, 700)
  } catch (e) {
    uni.hideLoading()
    errMsg.value = e?.detail || '注册失败'
  } finally {
    loading.value = false
  }
}

function goLogin() {
  uni.redirectTo({ url: '/pages/login/login' })
}

function goHome() {
  uni.switchTab({ url: '/pages/index/index' })
}

function goBack() {
  // 不允许栈里再卡一层登录
  uni.switchTab({ url: '/pages/index/index' })
}
</script>

<template>
  <view class="auth-shell">
    <view class="back-bar">
      <view class="back-btn" @tap="goBack">
        <text class="back-arrow">←</text>
        <text class="back-text">返回</text>
      </view>
    </view>

    <view class="auth-panel glass-card animate-slide-up">
      <view class="head">
        <text class="title">注册账号</text>
        <text class="sub">邮箱 + 密码就能用，H5 和小程序通用</text>
      </view>

      <view class="form">
        <label class="field">
          <span class="lbl">用户名 <text class="req">*</text></span>
          <input
            v-model="form.username"
            class="input"
            placeholder="3-32 位，字母/数字/_/-"
            :maxlength="32"
            placeholder-class="ipt-ph"
            confirm-type="next"
          />
        </label>

        <label class="field">
          <span class="lbl">邮箱 <text class="req">*</text></span>
          <input
            v-model="form.email"
            class="input"
            type="text"
            placeholder="example@x.edu.cn"
            :maxlength="120"
            placeholder-class="ipt-ph"
            confirm-type="next"
          />
        </label>

        <label class="field">
          <span class="lbl">密码 <text class="req">*</text></span>
          <view class="pwd-row">
            <input
              v-model="form.password"
              class="input"
              :password="!showPwd"
              placeholder="6-64 位"
              :maxlength="64"
              placeholder-class="ipt-ph"
              confirm-type="next"
            />
            <text class="toggle" @tap="showPwd = !showPwd">
              {{ showPwd ? '隐藏' : '显示' }}
            </text>
          </view>
        </label>

        <label class="field">
          <span class="lbl">确认密码 <text class="req">*</text></span>
          <input
            v-model="form.password2"
            class="input"
            :password="!showPwd"
            placeholder="再输一次"
            :maxlength="64"
            placeholder-class="ipt-ph"
            confirm-type="next"
          />
        </label>

        <view class="field-row">
          <label class="field">
            <span class="lbl">昵称</span>
            <input
              v-model="form.nickname"
              class="input"
              placeholder="不填就用用户名"
              :maxlength="32"
              placeholder-class="ipt-ph"
            />
          </label>
          <label class="field">
            <span class="lbl">校区</span>
            <input
              v-model="form.campus"
              class="input"
              placeholder="例如：东校区"
              :maxlength="32"
              placeholder-class="ipt-ph"
            />
          </label>
        </view>

        <view v-if="errMsg" class="err">{{ errMsg }}</view>

        <button
          class="btn-primary submit"
          :disabled="!canSubmit"
          @click="onSubmit"
        >
          {{ loading ? '注册中…' : '注册并登录' }}
        </button>

        <view class="meta-row">
          <text class="muted">已有账号？</text>
          <text class="link" @tap="goLogin">返回登录</text>
        </view>
      </view>
    </view>
  </view>
</template>

<style scoped lang="scss">
.auth-shell {
  position: relative;
  min-height: 100vh;
  padding: 80rpx 32rpx 40rpx;
  display: flex;
  align-items: flex-start;
  justify-content: center;
}

.back-bar {
  position: absolute;
  top: 24rpx;
  left: 24rpx;
  z-index: 10;
}
.back-btn {
  display: inline-flex;
  align-items: center;
  gap: 6rpx;
  padding: 12rpx 22rpx;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.75);
  border: 1px solid var(--vb-border);
  box-shadow: var(--vb-shadow-sm);
  font-size: 26rpx;
  color: var(--vb-ink-700);
  font-weight: 500;
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
}
.back-btn:active {
  background: var(--vb-bg-mute);
}
.back-arrow {
  font-size: 30rpx;
  line-height: 1;
  color: var(--vb-brand-700);
}

.auth-panel {
  width: 100%;
  max-width: 540rpx;
  padding: 48rpx 44rpx;
  border-radius: 26px;
}
.head {
  text-align: center;
  margin-bottom: 36rpx;
}
.title {
  display: block;
  font-size: 34rpx;
  font-weight: 700;
  color: var(--vb-heading);
  letter-spacing: 0.01em;
  margin-bottom: 8rpx;
}
.sub {
  display: block;
  font-size: 24rpx;
  color: var(--vb-ink-500);
}

.form {
  display: flex;
  flex-direction: column;
  gap: 20rpx;
}
.field {
  display: flex;
  flex-direction: column;
  gap: 10rpx;
  flex: 1;
}
.field-row {
  display: flex;
  gap: 18rpx;
}
.lbl {
  font-size: 26rpx;
  font-weight: 500;
  color: var(--vb-ink-700);
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
  padding: 6rpx 10rpx;
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
  border: 1px solid rgba(220, 38, 38, 0.18);
}
.submit {
  width: 100%;
  padding: 22rpx 0;
  font-size: 28rpx;
  border: none;
  font-weight: 600;
  margin-top: 8rpx;
}
.submit::after {
  border: none;
}
.meta-row {
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

@media (max-width: 540px) {
  .field-row {
    flex-direction: column;
    gap: 20rpx;
  }
}
</style>
