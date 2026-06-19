<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import NavBar from '@/components/NavBar.vue'
import PageFooter from '@/components/PageFooter.vue'
import { bookApi } from '@/api'
import { ElMessage, ElMessageBox } from 'element-plus'
import { formatPrice } from '@/utils/format'

const router = useRouter()

// 步骤：1 上传 2 识别中 3 确认书单 4 完成
const step = ref(1)
const previewUrl = ref('')
const currentFile = ref(null)
const recognizing = ref(false)
const recognizeProgress = ref(0)
const uploadProgress = ref(0)
const recognizedBooks = ref([])
const recognizedImage = ref('')
const rawText = ref('')

const listingTitle = ref('')
const listingDescription = ref('')
const listingCampus = ref('')
const defaultPrice = ref(5)
const coverFile = ref(null)
const submitting = ref(false)

const availableCount = computed(
  () => recognizedBooks.value.filter((b) => !b._removed && b.title).length
)
const totalPrice = computed(() =>
  recognizedBooks.value
    .filter((b) => !b._removed)
    .reduce((sum, b) => sum + Number(b.price || defaultPrice.value), 0)
)

// ---- Step 1: 选择文件 ----
function onFileChange(file) {
  if (!file) return
  if (!/^image\/(jpe?g|png|webp)$/i.test(file.raw?.type || file.type)) {
    ElMessage.error('仅支持 JPG / PNG / WEBP')
    return
  }
  currentFile.value = file.raw
  previewUrl.value = URL.createObjectURL(file.raw)
  step.value = 1
}

function clearFile() {
  currentFile.value = null
  previewUrl.value = ''
  recognizedBooks.value = []
  rawText.value = ''
  recognizedImage.value = ''
}

// ---- Step 2: 识别 ----
async function startRecognize() {
  if (!currentFile.value) return
  step.value = 2
  recognizing.value = true
  recognizeProgress.value = 0
  try {
    const data = await bookApi.recognize(currentFile.value, (p) => {
      recognizeProgress.value = p
    })
    recognizedBooks.value = (data.books || []).map((b, i) => ({
      ...b,
      position: i,
      price: b.price ?? defaultPrice.value,
      _removed: false,
    }))
    rawText.value = data.raw_text || ''
    recognizedImage.value = data.image_url
    listingTitle.value = listingTitle.value || `一摞二手书（${recognizedBooks.value.length} 本）`
    if (recognizedBooks.value.length === 0) {
      ElMessage.warning('未识别出任何书，请尝试更清晰的图片')
    } else {
      ElMessage.success(`成功识别出 ${recognizedBooks.value.length} 本书`)
    }
    step.value = 3
  } catch (e) {
    ElMessage.error('识别失败：' + (e.response?.data?.detail || e.message))
    step.value = 1
  } finally {
    recognizing.value = false
  }
}

// ---- Step 3: 编辑书单 ----
function addBlankBook() {
  recognizedBooks.value.push({
    title: '',
    author: '',
    publisher: '',
    isbn: '',
    edition: '',
    price: defaultPrice.value,
    _removed: false,
  })
}

function removeBook(idx) {
  recognizedBooks.value[idx]._removed = true
}

function applyDefaultPrice() {
  recognizedBooks.value.forEach((b) => {
    if (!b._removed) b.price = defaultPrice.value
  })
  ElMessage.success('已应用默认价格')
}

function restoreBook(idx) {
  recognizedBooks.value[idx]._removed = false
}

function onCoverChange(file) {
  coverFile.value = file?.raw || null
}

// ---- Step 4: 提交上架 ----
async function submit() {
  const validBooks = recognizedBooks.value.filter((b) => !b._removed && b.title?.trim())
  if (validBooks.length === 0) {
    ElMessage.error('至少保留一本书')
    return
  }
  if (!listingTitle.value.trim()) {
    ElMessage.error('请输入上架标题')
    return
  }
  submitting.value = true
  uploadProgress.value = 0
  try {
    const form = new FormData()
    form.append('title', listingTitle.value.trim())
    if (listingDescription.value) form.append('description', listingDescription.value)
    if (listingCampus.value) form.append('campus', listingCampus.value)
    form.append('default_price', String(defaultPrice.value))
    // 封面：用户没传就用识别图
    if (coverFile.value) {
      form.append('cover', coverFile.value)
    } else {
      // 拉取远程识别图转 Blob 上传
      const resp = await fetch(recognizedImage.value)
      const blob = await resp.blob()
      const ext = blob.type.split('/')[1] || 'jpg'
      form.append('cover', new File([blob], `cover.${ext}`, { type: blob.type }))
    }
    form.append('books_json', JSON.stringify(
      validBooks.map((b) => ({
        title: b.title,
        author: b.author,
        publisher: b.publisher,
        isbn: b.isbn,
        edition: b.edition,
        price: b.price,
        raw_ocr: b.raw_ocr,
        confidence: b.confidence,
      }))
    ))

    const data = await bookApi.createListing(form, (p) => {
      uploadProgress.value = p
    })
    ElMessage.success('上架成功！')
    step.value = 4
    setTimeout(() => router.push(`/listings/${data.id}`), 800)
  } catch (e) {
    ElMessage.error('上架失败：' + (e.response?.data?.detail || e.message))
  } finally {
    submitting.value = false
  }
}

function reset() {
  clearFile()
  step.value = 1
  listingTitle.value = ''
  listingDescription.value = ''
  listingCampus.value = ''
  defaultPrice.value = 5
  coverFile.value = null
}
</script>

<template>
  <NavBar />
  <main class="sell">
    <div class="container">
      <el-steps :active="step - 1" align-center class="steps">
        <el-step title="上传图片" />
        <el-step title="AI 识别" />
        <el-step title="确认书单" />
        <el-step title="上架完成" />
      </el-steps>

      <!-- Step 1 -->
      <div v-if="step === 1" class="vb-card upload-card">
        <h2>📚 拍一张书脊照片</h2>
        <p class="text-muted">把要卖的书摞成一摞，露出所有书脊（即书侧面印有书名/作者/出版社的一侧），然后拍照上传。</p>
        <ul class="tips">
          <li>✅ 顺光拍摄，避免反光</li>
          <li>✅ 尽量填满画面，文字清晰</li>
          <li>✅ 按顺序从左到右 / 从上到下整齐摆放，AI 也会按这个顺序识别</li>
          <li>✅ 一次最多几十本，过多可能识别不准</li>
        </ul>

        <el-upload
          v-if="!previewUrl"
          drag
          :auto-upload="false"
          :show-file-list="false"
          accept="image/jpeg,image/png,image/webp"
          :on-change="onFileChange"
        >
          <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
          <div class="el-upload__text">拖拽图片到此处，或<em>点击选择</em></div>
          <template #tip>
            <div class="el-upload__tip text-muted">支持 JPG / PNG / WEBP，建议 5MB 以内</div>
          </template>
        </el-upload>

        <div v-else class="preview-block">
          <img :src="previewUrl" class="preview" />
          <div class="preview-actions">
            <el-button @click="clearFile">重新选择</el-button>
            <el-button type="primary" @click="startRecognize">下一步：开始识别 →</el-button>
          </div>
        </div>
      </div>

      <!-- Step 2 -->
      <div v-if="step === 2" class="vb-card recognizing">
        <h2>🤖 AI 正在识别书脊</h2>
        <p class="text-muted">流程：上传图片 → OCR 识别 → 大模型结构化 → 导师纠错</p>
        <el-progress :percentage="recognizeProgress" :indeterminate="recognizeProgress === 0" />
        <div class="recognize-spinner">
          <el-icon class="is-loading"><Loading /></el-icon>
          <span>正在处理中，请稍候...</span>
        </div>
      </div>

      <!-- Step 3 -->
      <div v-if="step === 3" class="step3">
        <div class="vb-card">
          <h2>📝 确认书单与价格</h2>
          <p class="text-muted">检查 AI 识别结果，修改书名、作者、出版社或单独定价。点击"删除"可剔除不需要的。</p>

          <div class="bulk-actions">
            <span>批量设置每本价格：</span>
            <el-input-number v-model="defaultPrice" :min="0" :max="9999" :step="0.5" :precision="2" />
            <el-button @click="applyDefaultPrice">应用到全部</el-button>
            <span class="grow"></span>
            <el-button @click="addBlankBook">+ 手动添加</el-button>
          </div>

          <el-table :data="recognizedBooks" border style="width: 100%" :row-class-name="(r) => r.row._removed ? 'is-removed' : ''">
            <el-table-column type="index" label="#" width="50" />
            <el-table-column label="书名" min-width="200">
              <template #default="{ row, $index }">
                <el-input v-model="row.title" :disabled="row._removed" placeholder="书名" />
              </template>
            </el-table-column>
            <el-table-column label="作者" min-width="120">
              <template #default="{ row }">
                <el-input v-model="row.author" :disabled="row._removed" />
              </template>
            </el-table-column>
            <el-table-column label="出版社" min-width="140">
              <template #default="{ row }">
                <el-input v-model="row.publisher" :disabled="row._removed" />
              </template>
            </el-table-column>
            <el-table-column label="ISBN" min-width="130">
              <template #default="{ row }">
                <el-input v-model="row.isbn" :disabled="row._removed" />
              </template>
            </el-table-column>
            <el-table-column label="单价 (元)" width="110">
              <template #default="{ row }">
                <el-input-number v-model="row.price" :min="0" :max="9999" :precision="2" :step="0.5" :disabled="row._removed" size="small" />
              </template>
            </el-table-column>
            <el-table-column label="操作" width="100" fixed="right">
              <template #default="{ row, $index }">
                <el-button v-if="!row._removed" size="small" type="danger" link @click="removeBook($index)">删除</el-button>
                <el-button v-else size="small" type="primary" link @click="restoreBook($index)">恢复</el-button>
              </template>
            </el-table-column>
          </el-table>

          <div class="summary">
            <span>共 {{ recognizedBooks.length }} 本，保留 {{ availableCount }} 本</span>
            <span class="price-tag">合计：{{ formatPrice(totalPrice) }}</span>
          </div>
        </div>

        <div class="vb-card">
          <h2>🛒 上架信息</h2>
          <el-form label-position="top">
            <el-form-item label="上架标题" required>
              <el-input v-model="listingTitle" placeholder="例如：大三上学期全部教材（8 成新）" />
            </el-form-item>
            <el-form-item label="简介（选填）">
              <el-input v-model="listingDescription" type="textarea" :rows="3" placeholder="书的来源、新旧程度、有无笔记等" />
            </el-form-item>
            <el-form-item label="所在校区">
              <el-input v-model="listingCampus" placeholder="如：海淀校区" />
            </el-form-item>
            <el-form-item label="封面图">
              <el-upload
                :auto-upload="false"
                :show-file-list="false"
                :limit="1"
                accept="image/*"
                :on-change="onCoverChange"
              >
                <el-button>更换封面</el-button>
                <template #tip>
                  <span class="text-muted">默认使用书脊照片作为封面</span>
                </template>
              </el-upload>
              <div v-if="recognizedImage" class="cover-preview">
                <img :src="recognizedImage" alt="封面预览" />
                <div v-if="coverFile" class="cover-overlay">新封面已选择 ✓</div>
              </div>
            </el-form-item>
          </el-form>

          <div class="submit-bar">
            <el-button @click="reset">放弃</el-button>
            <el-button type="primary" size="large" :loading="submitting" @click="submit">
              立即上架（{{ availableCount }} 本）
            </el-button>
          </div>
          <el-progress v-if="submitting" :percentage="uploadProgress" :show-text="false" style="margin-top: 8px;" />
        </div>
      </div>

      <!-- Step 4 -->
      <div v-if="step === 4" class="vb-card done">
        <el-result icon="success" title="上架成功！" sub-title="正在跳转到详情页...">
          <template #icon>
            <el-icon class="big-icon"><CircleCheckFilled /></el-icon>
          </template>
        </el-result>
      </div>
    </div>
  </main>
  <PageFooter />
</template>

<style scoped>
.sell { padding: 24px 0 60px; }
.steps { margin-bottom: 24px; }

.upload-card, .recognizing, .done {
  max-width: 720px;
  margin: 0 auto;
  text-align: center;
}
.upload-card h2, .recognizing h2 { color: var(--brand-800); margin-top: 0; }
.tips {
  list-style: none;
  padding: 0;
  margin: 12px 0 20px;
  text-align: left;
  display: inline-block;
  color: var(--ink-700);
  font-size: 14px;
  line-height: 1.9;
}

.preview-block {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}
.preview {
  max-width: 100%;
  max-height: 480px;
  border-radius: var(--radius);
  box-shadow: var(--shadow-md);
}
.preview-actions { display: flex; gap: 12px; }

.recognize-spinner {
  margin-top: 24px;
  color: var(--brand-700);
  display: flex; align-items: center; justify-content: center; gap: 8px;
}

.step3 {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.bulk-actions {
  display: flex; align-items: center; gap: 12px;
  margin: 12px 0 16px;
  flex-wrap: wrap;
}
.bulk-actions .grow { flex: 1; }
.summary {
  display: flex; justify-content: space-between;
  margin-top: 12px;
  font-size: 14px;
  color: var(--ink-700);
}
.cover-preview {
  position: relative;
  margin-top: 8px;
  width: 240px;
  border: 1px solid var(--brand-200);
  border-radius: var(--radius);
  overflow: hidden;
}
.cover-preview img { width: 100%; display: block; }
.cover-overlay {
  position: absolute; bottom: 0; left: 0; right: 0;
  background: rgba(30, 64, 175, 0.85);
  color: white; text-align: center; padding: 6px;
  font-size: 13px;
}
.submit-bar {
  display: flex; justify-content: flex-end; gap: 12px;
  margin-top: 16px;
}
:deep(.is-removed) { opacity: 0.5; }
.big-icon { font-size: 72px; color: var(--brand-600); }
</style>
