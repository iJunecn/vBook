import { defineStore } from 'pinia'
import { authApi } from '@/api'
import { TOKEN_KEY, USER_KEY } from '@/api/config'

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
      this.token = uni.getStorageSync(TOKEN_KEY) || ''
      const raw = uni.getStorageSync(USER_KEY)
      this.user = raw ? (typeof raw === 'string' ? JSON.parse(raw) : raw) : null
    },
    /** 微信一键登录：拿 code -> 换 token */
    async wechatLogin() {
      const code = await new Promise((resolve, reject) => {
        uni.login({
          provider: 'weixin',
          success: (res) => (res.code ? resolve(res.code) : reject(new Error('未获取到 code'))),
          fail: reject,
        })
      })
      const data = await authApi.wechatLogin({ code })
      this._setAuth(data)
      return data
    },
    /** 邮箱 / 用户名 + 密码登录（account 字段后端自动判别） */
    async login(payload) {
      const data = await authApi.login(payload)
      this._setAuth(data)
      return data
    },
    /** 邮箱注册（注册成功后后端会同时签发 token 自动登录） */
    async register(payload) {
      const data = await authApi.register(payload)
      this._setAuth(data)
      return data
    },
    async refreshMe() {
      if (!this.token) return null
      const me = await authApi.me()
      this.user = me
      uni.setStorageSync(USER_KEY, JSON.stringify(me))
      return me
    },
    async updateProfile(payload) {
      const me = await authApi.updateMe(payload)
      this.user = me
      uni.setStorageSync(USER_KEY, JSON.stringify(me))
      return me
    },
    logout() {
      this.token = ''
      this.user = null
      uni.removeStorageSync(TOKEN_KEY)
      uni.removeStorageSync(USER_KEY)
    },
    _setAuth(data) {
      this.token = data.access_token
      this.user = data.user
      uni.setStorageSync(TOKEN_KEY, data.access_token)
      uni.setStorageSync(USER_KEY, JSON.stringify(data.user))
    },
  },
})
