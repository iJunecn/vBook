/**
 * 接口地址配置
 *
 * 设计原则：H5 走「同源代理」而不是直接暴露后端端口
 *  - VITE_API_HOST 留空：API_BASE = '/api/v1'（相对路径），由前端 nginx 反代到后端，
 *    浏览器始终跟 6628 同一个源，免 CORS、可从任何 IP（localhost / 局域网 / 公网）访问。
 *  - VITE_API_HOST = 'http://localhost:6627'：直连后端，仅限「本机 H5 联调」用。
 *
 * 微信小程序不受影响：始终走真机/模拟器能访问到的后端地址（在 MP-WEIXIN 块里写死）。
 */
// #ifdef MP-WEIXIN
const HOST = 'http://localhost:6627'
// #endif
// #ifndef MP-WEIXIN
// 注意：保留原值（包括空字符串），不要用 `||` 兜底成默认值，
// 这样显式留空 = 同源代理；不设置 = 直连本机后端（仅本地联调）。
const HOST =
  import.meta.env.VITE_API_HOST !== undefined && import.meta.env.VITE_API_HOST !== null
    ? String(import.meta.env.VITE_API_HOST)
    : ''
// #endif

export const API_BASE = `${HOST}/api/v1`
// 静态资源（H5 用同源由 nginx 反代；小程序走完整域名）
export const STATIC_BASE = HOST

export const TOKEN_KEY = 'vbook_token'
export const USER_KEY = 'vbook_user'
