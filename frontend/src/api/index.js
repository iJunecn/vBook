import { http, upload } from './request'

export const authApi = {
  wechatLogin: (data) => http.post('/auth/wechat-login', data), // { code }
  login: (data) => http.post('/auth/login', data), // 账号密码（保留备用）
  register: (data) => http.post('/auth/register', data),
  me: () => http.get('/auth/me'),
  updateMe: (data) => http.patch('/auth/me', data),
}

export const bookApi = {
  // 上传一张书脊照片 -> 识别书单（不落库）
  recognize: (filePath) => upload('/recognize', { filePath, name: 'file' }),
  // 封面 + 书单 JSON 一次性上架
  createListing: ({ coverPath, title, description, campus, default_price, books }) =>
    upload('/listings/with-image', {
      filePath: coverPath,
      name: 'cover',
      formData: {
        title,
        description: description || '',
        campus: campus || '',
        default_price: String(default_price ?? 5),
        books_json: JSON.stringify(books),
      },
    }),
  listListings: (params) => http.get('/listings', params),
  getListing: (id) => http.get(`/listings/${id}`),
  deleteListing: (id) => http.delete(`/listings/${id}`),
  updateBook: (id, data) => http.patch(`/books/${id}`, data),
  deleteBook: (id) => http.delete(`/books/${id}`),
  userListings: (userId) => http.get(`/users/${userId}/listings`),
}

export const orderApi = {
  create: (data) => http.post('/orders', data), // { book_id, note? }
  mine: () => http.get('/orders/mine'),
  sales: () => http.get('/orders/sales'),
}
