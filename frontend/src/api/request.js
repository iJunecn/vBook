/**
 * 基于 uni.request / uni.uploadFile 的请求封装
 * 替代旧 Web 版的 axios http.js（注入 token、统一解包、401 拦截）
 */
import { API_BASE, TOKEN_KEY, USER_KEY } from './config'

export function getToken() {
  return uni.getStorageSync(TOKEN_KEY) || ''
}

function handleUnauthorized() {
  uni.removeStorageSync(TOKEN_KEY)
  uni.removeStorageSync(USER_KEY)
  const pages = getCurrentPages()
  const current = pages.length ? pages[pages.length - 1].route : ''
  if (current !== 'pages/login/login') {
    uni.showToast({ title: '请先登录', icon: 'none' })
    setTimeout(() => uni.navigateTo({ url: '/pages/login/login' }), 300)
  }
}

function toQuery(params) {
  if (!params) return ''
  const q = Object.entries(params)
    .filter(([, v]) => v !== undefined && v !== null && v !== '')
    .map(([k, v]) => `${encodeURIComponent(k)}=${encodeURIComponent(v)}`)
    .join('&')
  return q ? `?${q}` : ''
}

export function request(url, { method = 'GET', data, header = {} } = {}) {
  const token = getToken()
  return new Promise((resolve, reject) => {
    uni.request({
      url: API_BASE + url,
      method,
      data,
      header: {
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
        ...header,
      },
      success: (res) => {
        const { statusCode, data: body } = res
        if (statusCode >= 200 && statusCode < 300) {
          resolve(body)
        } else if (statusCode === 401) {
          handleUnauthorized()
          reject(body)
        } else {
          uni.showToast({ title: body?.detail || `请求失败(${statusCode})`, icon: 'none' })
          reject(body)
        }
      },
      fail: (err) => {
        uni.showToast({ title: '网络异常，请检查后端地址', icon: 'none' })
        reject(err)
      },
    })
  })
}

/** multipart 上传：name 为文件字段名，formData 为其余文本字段 */
export function upload(url, { filePath, name = 'file', formData = {} } = {}) {
  const token = getToken()
  return new Promise((resolve, reject) => {
    uni.uploadFile({
      url: API_BASE + url,
      filePath,
      name,
      formData,
      header: token ? { Authorization: `Bearer ${token}` } : {},
      success: (res) => {
        let body = res.data
        try {
          body = JSON.parse(res.data)
        } catch (e) {
          /* 保持原始字符串 */
        }
        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(body)
        } else if (res.statusCode === 401) {
          handleUnauthorized()
          reject(body)
        } else {
          uni.showToast({ title: body?.detail || '上传失败', icon: 'none' })
          reject(body)
        }
      },
      fail: (err) => {
        uni.showToast({ title: '上传失败', icon: 'none' })
        reject(err)
      },
    })
  })
}

export const http = {
  get: (url, params) => request(url + toQuery(params), { method: 'GET' }),
  post: (url, data) => request(url, { method: 'POST', data }),
  patch: (url, data) => request(url, { method: 'PATCH', data }),
  delete: (url) => request(url, { method: 'DELETE' }),
}
