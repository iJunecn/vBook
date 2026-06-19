import { defineStore } from 'pinia'
import { authApi } from '@/api'

export const useUserStore = defineStore('user', {
  state: () => ({
    token: '',
    user: null,
  }),
  getters: {
    isLogin: (s) => !!s.token,
  },
  actions: {
    loadFromStorage() {
      this.token = localStorage.getItem('vbook_token') || ''
      const raw = localStorage.getItem('vbook_user')
      this.user = raw ? JSON.parse(raw) : null
    },
    async login(payload) {
      const data = await authApi.login(payload)
      this._setAuth(data)
      return data
    },
    async register(payload) {
      const data = await authApi.register(payload)
      this._setAuth(data)
      return data
    },
    async refreshMe() {
      if (!this.token) return null
      const me = await authApi.me()
      this.user = me
      localStorage.setItem('vbook_user', JSON.stringify(me))
      return me
    },
    logout() {
      this.token = ''
      this.user = null
      localStorage.removeItem('vbook_token')
      localStorage.removeItem('vbook_user')
    },
    _setAuth(data) {
      this.token = data.access_token
      this.user = data.user
      localStorage.setItem('vbook_token', data.access_token)
      localStorage.setItem('vbook_user', JSON.stringify(data.user))
    },
  },
})
