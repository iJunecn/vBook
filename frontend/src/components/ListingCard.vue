<script setup>
/**
 * 书单卡片（vUSTB surface-card 风格）
 *  - 圆角 12px + 边框 + 阴影 + 悬浮上浮
 *  - 封面 16:10 自适应
 *  - 状态徽章（已售罄 / 已下架）左上角
 */
import { formatPrice, formatDate, mediaUrl } from '@/utils/format'

const props = defineProps({
  listing: { type: Object, required: true },
})

function open() {
  uni.navigateTo({ url: `/pages/listing/detail?id=${props.listing.id}` })
}
</script>

<template>
  <view class="card surface-card hoverable" @tap="open">
    <view class="cover">
      <image
        class="cover-img"
        :src="mediaUrl(listing.cover_image)"
        mode="aspectFill"
        lazy-load
      />
      <view v-if="listing.available_count === 0" class="status-badge danger">已售罄</view>
      <view v-else-if="listing.status === 'removed'" class="status-badge">已下架</view>
    </view>
    <view class="body">
      <text class="title">{{ listing.title }}</text>
      <view class="meta">
        <text v-if="listing.campus" class="campus-badge">{{ listing.campus }}</text>
        <text class="muted">共 {{ listing.book_count }} 本</text>
      </view>
      <view class="bottom">
        <text class="price">{{ formatPrice(listing.default_price) }}<text class="per">/本起</text></text>
        <text class="time muted">{{ formatDate(listing.created_at) }}</text>
      </view>
      <text v-if="listing.seller" class="seller muted">
        @{{ listing.seller.nickname || listing.seller.username }}
      </text>
    </view>
  </view>
</template>

<style scoped lang="scss">
.card {
  overflow: hidden;
  display: flex;
  flex-direction: column;
  cursor: pointer;
}
.cover {
  position: relative;
  width: 100%;
  aspect-ratio: 4 / 3;
  background: linear-gradient(135deg, var(--vb-brand-50), var(--vb-bg-mute));
}
.cover-img {
  width: 100%;
  height: 100%;
  display: block;
}
.status-badge {
  position: absolute;
  top: 12rpx;
  left: 12rpx;
  padding: 4rpx 14rpx;
  border-radius: 6rpx;
  font-size: 22rpx;
  font-weight: 600;
  background: rgba(0, 0, 0, 0.6);
  color: #fff;
  backdrop-filter: blur(4px);
}
.status-badge.danger {
  background: rgba(220, 38, 38, 0.85);
}
.body {
  padding: 18rpx 20rpx 20rpx;
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8rpx;
}
.title {
  font-size: 28rpx;
  font-weight: 600;
  color: var(--vb-heading);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.meta {
  display: flex;
  align-items: center;
  gap: 10rpx;
  font-size: 22rpx;
}
.campus-badge {
  display: inline-block;
  padding: 2rpx 12rpx;
  border-radius: 999px;
  font-size: 20rpx;
  font-weight: 500;
  background: var(--vb-brand-50);
  color: var(--vb-brand-700);
}
.muted {
  color: var(--vb-ink-500);
}
.bottom {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  margin-top: auto;
  padding-top: 4rpx;
}
.price {
  font-size: 32rpx;
  font-weight: 700;
  color: var(--vb-danger);
}
.per {
  font-size: 20rpx;
  font-weight: 400;
  color: var(--vb-ink-400);
  margin-left: 2rpx;
}
.time {
  font-size: 20rpx;
}
.seller {
  font-size: 20rpx;
  margin-top: 2rpx;
}
</style>