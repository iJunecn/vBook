/** 工具函数 */
export function formatPrice(p) {
  if (p == null) return '-'
  return `¥${Number(p).toFixed(2)}`
}

export function formatDate(d) {
  if (!d) return '-'
  const dt = new Date(d)
  const now = new Date()
  const diff = (now - dt) / 1000
  if (diff < 60) return '刚刚'
  if (diff < 3600) return `${Math.floor(diff / 60)} 分钟前`
  if (diff < 86400) return `${Math.floor(diff / 3600)} 小时前`
  if (diff < 86400 * 3) return `${Math.floor(diff / 86400)} 天前`
  return dt.toLocaleDateString('zh-CN')
}

export function fileToBase64(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = () => resolve(reader.result)
    reader.onerror = reject
    reader.readAsDataURL(file)
  })
}
