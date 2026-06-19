<script setup>
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
    setTimeout(() => uni.navigateTo({ url: '/pages/login/login' }), 300)
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
    <view class="steps">
      <text :class="['step', step === 'pick' ? 'on' : 'done']">1 拍照</text>
      <text :class="['step', step === 'edit' ? 'on' : step === 'publish' ? 'done' : '']">2 核对</text>
      <text :class="['step', step === 'publish' ? 'on' : '']">3 发布</text>
    </view>

    <!-- 第一步：选图 -->
    <view v-if="step === 'pick'" class="pick vb-card">
      <view class="pick-inner" @tap="chooseImage">
        <text class="pick-icon">📷</text>
        <text class="pick-title">上传一摞书的书脊照片</text>
        <text class="vb-muted">支持 JPG / PNG / WEBP，单张 ≤ 20MB</text>
      </view>
    </view>

    <!-- 第二步：核对书单 -->
    <template v-else-if="step === 'edit'">
      <image v-if="coverPath" :src="coverPath" mode="widthFix" class="preview" />

      <view class="bulk vb-card">
        <input v-model="bulkPrice" type="digit" class="bulk-input" placeholder="统一定价" />
        <wd-button size="small" @click="applyBulkPrice">应用到全部</wd-button>
        <wd-button size="small" plain @click="addBook">+ 加一本</wd-button>
      </view>

      <view v-for="(b, idx) in books" :key="idx" class="book vb-card">
        <view class="book-head">
          <text class="book-no">第 {{ idx + 1 }} 本</text>
          <text class="del" @tap="removeBook(idx)">删除</text>
        </view>
        <input v-model="b.title" class="f" placeholder="书名（必填）" />
        <view class="row2">
          <input v-model="b.author" class="f half" placeholder="作者" />
          <input v-model="b.publisher" class="f half" placeholder="出版社" />
        </view>
        <view class="row2">
          <input v-model="b.isbn" class="f half" placeholder="ISBN" />
          <input v-model="b.edition" class="f half" placeholder="版次" />
        </view>
        <input v-model="b.price" type="digit" class="f" placeholder="价格" />
      </view>

      <view class="summary vb-card">
        <text>共 {{ availableBooks.length }} 本</text>
        <text class="vb-price">合计 ¥{{ totalPrice.toFixed(2) }}</text>
      </view>

      <view class="footer-btns">
        <wd-button plain block @click="reset">重新拍照</wd-button>
        <wd-button type="primary" block @click="toPublish">下一步</wd-button>
      </view>
    </template>

    <!-- 第三步：发布信息 -->
    <template v-else>
      <view class="form vb-card">
        <text class="field-label">书单标题</text>
        <input v-model="meta.title" class="f" placeholder="例如：考研数学全套 9 成新" />

        <text class="field-label">描述（可选）</text>
        <textarea v-model="meta.description" class="f area" placeholder="成色、使用情况、交易方式等" />

        <text class="field-label">校区（可选）</text>
        <input v-model="meta.campus" class="f" placeholder="例如：东校区" />

        <text class="field-label">默认单价</text>
        <input v-model="meta.default_price" type="digit" class="f" placeholder="5" />
      </view>

      <view class="summary vb-card">
        <text>{{ availableBooks.length }} 本 · 合计 ¥{{ totalPrice.toFixed(2) }}</text>
      </view>

      <view class="footer-btns">
        <wd-button plain block @click="step = 'edit'">上一步</wd-button>
        <wd-button type="primary" block :loading="submitting" @click="submit">确认发布</wd-button>
      </view>
    </template>
  </view>
</template>

<style scoped lang="scss">
.page {
  padding: 24rpx;
}
.steps {
  display: flex;
  justify-content: space-around;
  margin-bottom: 24rpx;
}
.step {
  font-size: 26rpx;
  color: var(--vb-ink-300);
}
.step.on {
  color: var(--vb-brand-600);
  font-weight: 700;
}
.step.done {
  color: var(--vb-ink-700);
}
.pick {
  padding: 0;
}
.pick-inner {
  padding: 96rpx 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12rpx;
}
.pick-icon {
  font-size: 96rpx;
}
.pick-title {
  font-size: 30rpx;
  font-weight: 600;
}
.preview {
  width: 100%;
  border-radius: 16rpx;
  margin-bottom: 20rpx;
}
.bulk {
  display: flex;
  align-items: center;
  gap: 16rpx;
  padding: 18rpx;
  margin-bottom: 20rpx;
}
.bulk-input {
  flex: 1;
  border: 1rpx solid var(--vb-brand-100);
  border-radius: 12rpx;
  padding: 12rpx 16rpx;
  font-size: 26rpx;
}
.book {
  padding: 20rpx;
  margin-bottom: 20rpx;
}
.book-head {
  display: flex;
  justify-content: space-between;
  margin-bottom: 12rpx;
}
.book-no {
  font-size: 24rpx;
  color: var(--vb-brand-600);
  font-weight: 600;
}
.del {
  font-size: 24rpx;
  color: #e23d3d;
}
.f {
  width: 100%;
  box-sizing: border-box;
  border: 1rpx solid var(--vb-brand-100);
  border-radius: 12rpx;
  padding: 16rpx;
  font-size: 26rpx;
  margin-bottom: 12rpx;
  background: #fff;
}
.row2 {
  display: flex;
  gap: 12rpx;
}
.half {
  flex: 1;
}
.area {
  height: 140rpx;
}
.field-label {
  display: block;
  font-size: 24rpx;
  color: var(--vb-ink-700);
  margin-bottom: 8rpx;
}
.form {
  padding: 20rpx;
  margin-bottom: 20rpx;
}
.summary {
  display: flex;
  justify-content: space-between;
  padding: 24rpx;
  margin-bottom: 20rpx;
  font-size: 28rpx;
}
.footer-btns {
  display: flex;
  gap: 20rpx;
}
.footer-btns > * {
  flex: 1;
}
</style>
