import { STATIC_BASE } from '@/api/config'

export function formatPrice(p) {
  if (p == null) return '-'
  return `¥${Number(p).toFixed(2)}`
}

export function formatDate(d) {
  if (!d) return '-'
  // iOS / 小程序对 'YYYY-MM-DD HH:mm:ss' 兼容差，统一替换为 'YYYY/MM/DD'
  const dt = new Date(String(d).replace(/-/g, '/').replace('T', ' ').split('.')[0])
  const now = new Date()
  const diff = (now.getTime() - dt.getTime()) / 1000
  if (Number.isNaN(diff)) return String(d)
  if (diff < 60) return '刚刚'
  if (diff < 3600) return `${Math.floor(diff / 60)} 分钟前`
  if (diff < 86400) return `${Math.floor(diff / 3600)} 小时前`
  if (diff < 86400 * 3) return `${Math.floor(diff / 86400)} 天前`
  return dt.toLocaleDateString('zh-CN')
}

/** 把后端返回的相对图片路径（/uploads/xxx）补全为可访问的绝对地址 */
export function mediaUrl(path) {
  if (!path) return ''
  if (/^https?:\/\//.test(path) || path.startsWith('data:')) return path
  return `${STATIC_BASE}${path.startsWith('/') ? '' : '/'}${path}`
}
