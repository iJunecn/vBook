import axios from 'axios'
import { ElMessage } from 'element-plus'

const http = axios.create({
  baseURL: import.meta.env.VITE_API_BASE || '/api/v1',
  timeout: 120000,
})

http.interceptors.request.use((config) => {
  const token = localStorage.getItem('vbook_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

http.interceptors.response.use(
  (resp) => resp.data,
  (err) => {
    const status = err.response?.status
    const detail =
      err.response?.data?.detail ||
      err.message ||
      '请求失败'
    if (status === 401) {
      localStorage.removeItem('vbook_token')
      localStorage.removeItem('vbook_user')
      if (!location.pathname.startsWith('/login')) {
        ElMessage.error('请先登录')
        setTimeout(() => (location.href = '/login'), 400)
      }
    } else if (status >= 500) {
      ElMessage.error(`服务异常: ${detail}`)
    } else if (status && status !== 401) {
      ElMessage.error(detail)
    }
    return Promise.reject(err)
  }
)

export default http
