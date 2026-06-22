<script setup>
/**
 * 卖书页 - 三步流程：拍照 → 核对书单 → 发布
 * 视觉：vUSTB 风格 —— 步骤指示器 + surface-card + btn-primary
 */
import { ref, computed } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { bookApi } from '@/api'
import { useUserStore } from '@/store/user'

const userStore = useUserStore()

// step: 'pick' | 'edit' | 'publish'
const step = ref('pick')
const coverPath = ref('')
const books = ref([])
const bulkPrice = ref('')

const meta = ref({
  title: '',
  description: '',
  campus: '',
  default_price: 5,
})

const submitting = ref(false)

const availableBooks = computed(() => books.value.filter((b) => b.title && b.title.trim()))
const totalPrice = computed(() =>
  availableBooks.value.reduce((s, b) => s + (Number(b.price) || 0), 0),
)

onShow(() => {
  if (!userStore.isLogin) {
    uni.showToast({ title: '请先登录', icon: 'none' })
    // 用 reLaunch 替换整栈，避免浏览器后退时回到本页再次触发跳转（无限循环）
    setTimeout(() => uni.reLaunch({ url: '/pages/login/login?from=sell' }), 300)
  }
})

function chooseImage() {
  uni.chooseImage({
    count: 1,
    sizeType: ['original', 'compressed'],
    sourceType: ['album', 'camera'],
    success: (res) => {
      const file = res.tempFiles && res.tempFiles[0]
      const path = res.tempFilePaths[0]
      if (file && file.size > 20 * 1024 * 1024) {
        uni.showToast({ title: '图片不能超过 20MB', icon: 'none' })
        return
      }
      coverPath.value = path
      recognize(path)
    },
  })
}

async function recognize(path) {
  uni.showLoading({ title: 'AI 识别中…', mask: true })
  try {
    const result = await bookApi.recognize(path)
    books.value = (result.books || []).map((b, i) => ({
      title: b.title || '',
      author: b.author || '',
      publisher: b.publisher || '',
      isbn: b.isbn || '',
      edition: b.edition || '',
      price: b.price ?? 5,
      raw_ocr: b.raw_ocr || '',
      confidence: b.confidence ?? null,
      position: i,
    }))
    meta.value.title = books.value[0]?.title ? `${books.value[0].title} 等${books.value.length}本` : '我的二手书'
    uni.hideLoading()
    if (!books.value.length) {
      uni.showToast({ title: '未识别到书目，可手动添加', icon: 'none' })
      addBook()
    }
    step.value = 'edit'
  } catch (e) {
    uni.hideLoading()
    /* 拦截器已提示 */
  }
}

function addBook() {
  books.value.push({
    title: '',
    author: '',
    publisher: '',
    isbn: '',
    edition: '',
    price: Number(meta.value.default_price) || 5,
    raw_ocr: '',
    confidence: null,
    position: books.value.length,
  })
}

function removeBook(idx) {
  books.value.splice(idx, 1)
}

function applyBulkPrice() {
  const p = Number(bulkPrice.value)
  if (Number.isNaN(p) || p < 0) {
    uni.showToast({ title: '请输入有效价格', icon: 'none' })
    return
  }
  books.value.forEach((b) => (b.price = p))
  uni.showToast({ title: '已应用到全部', icon: 'none' })
}

function toPublish() {
  if (!availableBooks.value.length) {
    uni.showToast({ title: '至少保留一本有书名的书', icon: 'none' })
    return
  }
  step.value = 'publish'
}

async function submit() {
  if (submitting.value) return
  if (!meta.value.title.trim()) {
    uni.showToast({ title: '请填写书单标题', icon: 'none' })
    return
  }
  submitting.value = true
  uni.showLoading({ title: '发布中…', mask: true })
  try {
    const listing = await bookApi.createListing({
      coverPath: coverPath.value,
      title: meta.value.title.trim(),
      description: meta.value.description,
      campus: meta.value.campus,
      default_price: Number(meta.value.default_price) || 5,
      books: availableBooks.value.map((b, i) => ({ ...b, position: i })),
    })
    uni.hideLoading()
    uni.showToast({ title: '发布成功', icon: 'success' })
    reset()
    setTimeout(() => uni.navigateTo({ url: `/pages/listing/detail?id=${listing.id}` }), 700)
  } catch (e) {
    uni.hideLoading()
  } finally {
    submitting.value = false
  }
}

function reset() {
  step.value = 'pick'
  coverPath.value = ''
  books.value = []
  bulkPrice.value = ''
  meta.value = { title: '', description: '', campus: '', default_price: 5 }
}
</script>

<template>
  <view class="page">
    <!-- 步骤指示 -->
    <view class="steps surface-card">
      <view :class="['step', step === 'pick' ? 'on' : 'done']">
        <text class="step-no">1</text>
        <text class="step-label">拍照</text>
      </view>
      <text class="step-line" />
      <view :class="['step', step === 'edit' ? 'on' : (step === 'publish' ? 'done' : '')]">
        <text class="step-no">2</text>
        <text class="step-label">核对</text>
      </view>
      <text class="step-line" />
      <view :class="['step', step === 'publish' ? 'on' : '']">
        <text class="step-no">3</text>
        <text class="step-label">发布</text>
      </view>
    </view>

    <!-- 第一步：选图 -->
    <view v-if="step === 'pick'" class="pick surface-card hoverable" @tap="chooseImage">
      <text class="pick-icon">📷</text>
      <text class="pick-title">上传一摞书的书脊照片</text>
      <text class="pick-tip muted">支持 JPG / PNG / WEBP，单张 ≤ 20MB</text>
    </view>

    <!-- 第二步：核对书单 -->
    <template v-else-if="step === 'edit'">
      <view v-if="coverPath" class="preview-wrap surface-card">
        <image :src="coverPath" mode="widthFix" class="preview" />
      </view>

      <view class="bulk surface-card">
        <text class="bulk-icon">💰</text>
        <input v-model="bulkPrice" type="digit" class="input bulk-input" placeholder="统一定价（元）" />
        <button class="btn-ghost bulk-btn" @click="applyBulkPrice">应用</button>
        <button class="btn-primary bulk-btn" @click="addBook">+ 加一本</button>
      </view>

      <view v-for="(b, idx) in books" :key="idx" class="book surface-card">
        <view class="book-head">
          <text class="book-no">第 {{ idx + 1 }} 本</text>
          <text class="del" @tap="removeBook(idx)">删除</text>
        </view>
        <view class="field">
          <text class="field-label">书名 <text class="req">*</text></text>
          <input v-model="b.title" class="input" placeholder="必填" />
        </view>
        <view class="row2">
          <view class="field">
            <text class="field-label">作者</text>
            <input v-model="b.author" class="input" placeholder="作者" />
          </view>
          <view class="field">
            <text class="field-label">出版社</text>
            <input v-model="b.publisher" class="input" placeholder="出版社" />
          </view>
        </view>
        <view class="row2">
          <view class="field">
            <text class="field-label">ISBN</text>
            <input v-model="b.isbn" class="input" placeholder="ISBN" />
          </view>
          <view class="field">
            <text class="field-label">版次</text>
            <input v-model="b.edition" class="input" placeholder="版次" />
          </view>
        </view>
        <view class="field">
          <text class="field-label">价格（元）</text>
          <input v-model="b.price" type="digit" class="input" placeholder="价格" />
        </view>
      </view>

      <view class="summary surface-card">
        <text class="muted">共 {{ availableBooks.length }} 本</text>
        <text class="price">合计 ¥{{ totalPrice.toFixed(2) }}</text>
      </view>

      <view class="footer-btns">
        <button class="btn-ghost" @click="reset">重新拍照</button>
        <button class="btn-primary" @click="toPublish">下一步</button>
      </view>
    </template>

    <!-- 第三步：发布信息 -->
    <template v-else>
      <view class="form surface-card">
        <view class="field">
          <text class="field-label">书单标题 <text class="req">*</text></text>
          <input v-model="meta.title" class="input" placeholder="例如：考研数学全套 9 成新" />
        </view>
        <view class="field">
          <text class="field-label">描述（可选）</text>
          <textarea v-model="meta.description" class="input area" placeholder="成色、使用情况、交易方式等" />
        </view>
        <view class="row2">
          <view class="field">
            <text class="field-label">校区（可选）</text>
            <input v-model="meta.campus" class="input" placeholder="例如：东校区" />
          </view>
          <view class="field">
            <text class="field-label">默认单价（元）</text>
            <input v-model="meta.default_price" type="digit" class="input" placeholder="5" />
          </view>
        </view>
      </view>

      <view class="summary surface-card">
        <text class="muted">{{ availableBooks.length }} 本</text>
        <text class="price">合计 ¥{{ totalPrice.toFixed(2) }}</text>
      </view>

      <view class="footer-btns">
        <button class="btn-ghost" @click="step = 'edit'">上一步</button>
        <button class="btn-primary" :disabled="submitting" @click="submit">
          {{ submitting ? '发布中…' : '确认发布' }}
        </button>
      </view>
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

/* ===== Steps ===== */
.steps {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 18rpx 24rpx;
  border-radius: 12px;
}
.step {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6rpx;
  flex: 0 0 auto;
}
.step-no {
  width: 48rpx;
  height: 48rpx;
  border-radius: 50%;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 26rpx;
  font-weight: 700;
  background: var(--vb-bg-mute);
  color: var(--vb-ink-400);
}
.step-label {
  font-size: 22rpx;
  color: var(--vb-ink-400);
}
.step.on .step-no {
  background: var(--vb-brand-600);
  color: #fff;
  box-shadow: 0 4rpx 12rpx rgba(47, 120, 186, 0.3);
}
.step.on .step-label {
  color: var(--vb-brand-700);
  font-weight: 600;
}
.step.done .step-no {
  background: var(--vb-success);
  color: #fff;
}
.step.done .step-label {
  color: var(--vb-ink-700);
}
.step-line {
  flex: 1;
  height: 2rpx;
  background: var(--vb-border);
  margin: 0 12rpx;
  margin-bottom: 24rpx;
}

/* ===== Pick ===== */
.pick {
  padding: 96rpx 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 14rpx;
  border-radius: 16px;
  text-align: center;
}
.pick-icon {
  font-size: 96rpx;
}
.pick-title {
  font-size: 30rpx;
  font-weight: 600;
  color: var(--vb-heading);
}
.pick-tip {
  font-size: 22rpx;
}
.muted {
  color: var(--vb-ink-500);
}

/* ===== Preview ===== */
.preview-wrap {
  padding: 0;
  overflow: hidden;
}
.preview {
  width: 100%;
  display: block;
}

/* ===== Bulk ===== */
.bulk {
  display: flex;
  align-items: center;
  gap: 12rpx;
  padding: 18rpx 20rpx;
  border-radius: 12px;
}
.bulk-icon {
  font-size: 28rpx;
}
.bulk-input {
  flex: 1;
}
.bulk-btn {
  padding: 10rpx 20rpx;
  font-size: 24rpx;
  border: none;
}
.bulk-btn::after {
  border: none;
}

/* ===== Book ===== */
.book {
  padding: 22rpx 24rpx;
  display: flex;
  flex-direction: column;
  gap: 14rpx;
  border-radius: 12px;
}
.book-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.book-no {
  font-size: 24rpx;
  color: var(--vb-brand-700);
  font-weight: 600;
  padding: 4rpx 14rpx;
  background: var(--vb-brand-50);
  border-radius: 999px;
}
.del {
  font-size: 24rpx;
  color: var(--vb-danger);
  font-weight: 500;
}
.field {
  display: flex;
  flex-direction: column;
  gap: 8rpx;
  flex: 1;
}
.field-label {
  font-size: 22rpx;
  color: var(--vb-ink-700);
  font-weight: 500;
}
.req {
  color: var(--vb-danger);
}
.row2 {
  display: flex;
  gap: 14rpx;
}
.area {
  min-height: 140rpx;
  line-height: 1.5;
}

/* ===== Summary ===== */
.summary {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24rpx;
  border-radius: 12px;
  font-size: 26rpx;
}
.price {
  font-size: 30rpx;
  font-weight: 700;
  color: var(--vb-danger);
}

/* ===== Form ===== */
.form {
  padding: 24rpx;
  display: flex;
  flex-direction: column;
  gap: 18rpx;
  border-radius: 12px;
}

/* ===== Footer buttons ===== */
.footer-btns {
  display: flex;
  gap: 16rpx;
}
.footer-btns > * {
  flex: 1;
  padding: 18rpx;
  border: none;
  font-size: 28rpx;
}
.footer-btns > ::after {
  border: none;
}
</style>