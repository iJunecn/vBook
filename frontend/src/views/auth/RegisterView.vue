<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import NavBar from '@/components/NavBar.vue'
import { useUserStore } from '@/store/user'
import { ElMessage } from 'element-plus'

const router = useRouter()
const userStore = useUserStore()
const loading = ref(false)
const formRef = ref()

const form = reactive({
  username: '',
  email: '',
  password: '',
  confirm: '',
  nickname: '',
  campus: '',
})
const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 32, message: '长度 3-32', trigger: 'blur' },
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '邮箱格式不正确', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '至少 6 位', trigger: 'blur' },
  ],
  confirm: [
    { required: true, message: '请再次输入密码', trigger: 'blur' },
    {
      validator: (_, v, cb) =>
        v === form.password ? cb() : cb(new Error('两次密码不一致')),
      trigger: 'blur',
    },
  ],
}

async function submit() {
  await formRef.value.validate()
  loading.value = true
  try {
    const { confirm, ...payload } = form
    await userStore.register(payload)
    ElMessage.success('注册成功，已自动登录')
    router.push('/')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <NavBar />
  <main class="auth-page">
    <div class="auth-card">
      <h2>注册贝壳易书账号</h2>
      <p class="text-muted">仅需 30 秒，开启你的二手书交易</p>
      <el-form ref="formRef" :model="form" :rules="rules" label-position="top" @submit.prevent>
        <el-form-item label="用户名（字母/数字/下划线/短横线）" prop="username">
          <el-input v-model="form.username" placeholder="3-32 位" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="form.email" placeholder="用于找回密码" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="form.password" type="password" show-password placeholder="至少 6 位" />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirm">
          <el-input v-model="form.confirm" type="password" show-password />
        </el-form-item>
        <el-form-item label="昵称（选填）" prop="nickname">
          <el-input v-model="form.nickname" />
        </el-form-item>
        <el-form-item label="所在校区（选填）" prop="campus">
          <el-input v-model="form.campus" placeholder="如：海淀校区" />
        </el-form-item>
        <el-button type="primary" size="large" :loading="loading" style="width:100%" @click="submit">注册</el-button>
      </el-form>
      <div class="auth-foot">
        已有账号？<router-link to="/login">直接登录</router-link>
      </div>
    </div>
  </main>
</template>

<style scoped>
.auth-page {
  min-height: calc(100vh - 64px);
  display: flex; align-items: center; justify-content: center;
  padding: 40px 20px;
  background: linear-gradient(180deg, #EFF6FF 0%, #FFFFFF 100%);
}
.auth-card {
  width: 100%;
  max-width: 460px;
  background: #fff;
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
  padding: 32px;
  border: 1px solid var(--brand-100);
}
.auth-card h2 { margin: 0 0 4px; color: var(--brand-800); }
.auth-card .text-muted { margin: 0 0 20px; font-size: 14px; }
.auth-foot { margin-top: 16px; font-size: 14px; color: var(--ink-500); text-align: center; }
</style>
