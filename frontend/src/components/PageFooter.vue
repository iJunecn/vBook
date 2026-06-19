<script setup>
const year = new Date().getFullYear()
</script>

<template>
  <footer class="footer">
    <div class="container foot-inner">
      <div class="foot-brand">
        <div class="brand-line">贝壳易书</div>
        <div class="brand-desc">让校园二手书流转更简单</div>
      </div>
      <div class="foot-meta">
        <div>© {{ year }} 贝壳易书 · 由 OCR + 大模型驱动</div>
        <div class="text-muted">仅供学习与个人项目使用</div>
      </div>
    </div>
  </footer>
</template>

<style scoped>
.footer {
  background: linear-gradient(180deg, #FFFFFF 0%, #EFF6FF 100%);
  border-top: 1px solid var(--brand-100);
  margin-top: 40px;
  padding: 24px 0;
}
.foot-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 12px;
}
.brand-line { font-weight: 700; color: var(--brand-800); font-size: 16px; }
.brand-desc { color: var(--ink-500); font-size: 13px; }
.foot-meta { color: var(--ink-500); font-size: 13px; text-align: right; }
</style>
