import http from './http'

export const authApi = {
  register: (data) => http.post('/auth/register', data),
  login: (data) => http.post('/auth/login', data),
  me: () => http.get('/auth/me'),
  updateMe: (data) => http.patch('/auth/me', data),
}

export const bookApi = {
  recognize: (file, onProgress) => {
    const fd = new FormData()
    fd.append('file', file)
    return http.post('/recognize', fd, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: (e) => {
        if (onProgress && e.total) onProgress(Math.round((e.loaded * 100) / e.total))
      },
    })
  },
  createListing: (form, onProgress) => {
    return http.post('/listings/with-image', form, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: (e) => {
        if (onProgress && e.total) onProgress(Math.round((e.loaded * 100) / e.total))
      },
    })
  },
  listListings: (params) => http.get('/listings', { params }),
  getListing: (id) => http.get(`/listings/${id}`),
  deleteListing: (id) => http.delete(`/listings/${id}`),
  updateBook: (id, data) => http.patch(`/books/${id}`, data),
  deleteBook: (id) => http.delete(`/books/${id}`),
  userListings: (userId) => http.get(`/users/${userId}/listings`),
}

export const orderApi = {
  create: (data) => http.post('/orders', data),
  mine: () => http.get('/orders/mine'),
  sales: () => http.get('/orders/sales'),
}
