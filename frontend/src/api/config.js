/**
 * 接口地址配置
 * - 开发：指向本地后端。微信小程序真机调试需改成局域网 IP，
 *   并在「微信开发者工具 - 详情 - 本地设置」勾选「不校验合法域名」。
 * - 生产：必须是已 ICP 备案的 HTTPS 域名，并在小程序后台「服务器域名」中配置。
 */
// #ifdef MP-WEIXIN
const HOST = 'http://localhost:8000'
// #endif
// #ifndef MP-WEIXIN
const HOST = import.meta.env.VITE_API_HOST || 'http://localhost:8000'
// #endif

export const API_BASE = `${HOST}/api/v1`
export const STATIC_BASE = HOST

export const TOKEN_KEY = 'vbook_token'
export const USER_KEY = 'vbook_user'
