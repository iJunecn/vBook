<script setup>
import { formatPrice, formatDate, mediaUrl } from '@/utils/format'

const props = defineProps({
  listing: { type: Object, required: true },
})

function open() {
  uni.navigateTo({ url: `/pages/listing/detail?id=${props.listing.id}` })
}
</script>

<template>
  <view class="card vb-card" @tap="open">
    <view class="cover">
      <image
        class="cover-img"
        :src="mediaUrl(listing.cover_image)"
        mode="aspectFill"
        lazy-load
      />
      <text v-if="listing.available_count === 0" class="vb-badge is-danger badge-abs">已售罄</text>
      <text v-else-if="listing.status === 'removed'" class="vb-badge badge-abs">已下架</text>
    </view>
    <view class="body">
      <text class="title">{{ listing.title }}</text>
      <view class="meta">
        <text v-if="listing.campus" class="vb-badge">{{ listing.campus }}</text>
        <text class="vb-muted">共 {{ listing.book_count }} 本</text>
      </view>
      <view class="bottom">
        <text class="vb-price">{{ formatPrice(listing.default_price) }}<text class="per">/本起</text></text>
        <text class="vb-muted time">{{ formatDate(listing.created_at) }}</text>
      </view>
      <text v-if="listing.seller" class="seller vb-muted">
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
}
.cover {
  position: relative;
  width: 100%;
  height: 220rpx;
  background: var(--vb-brand-50);
}
.cover-img {
  width: 100%;
  height: 100%;
}
.badge-abs {
  position: absolute;
  top: 12rpx;
  right: 12rpx;
}
.body {
  padding: 16rpx 18rpx 18rpx;
  flex: 1;
  display: flex;
  flex-direction: column;
}
.title {
  font-size: 28rpx;
  font-weight: 600;
  color: var(--vb-ink-900);
  margin-bottom: 10rpx;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.meta {
  display: flex;
  align-items: center;
  gap: 12rpx;
  font-size: 22rpx;
  margin-bottom: 12rpx;
}
.bottom {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  margin-top: auto;
}
.vb-price {
  font-size: 32rpx;
}
.per {
  font-size: 20rpx;
  font-weight: 400;
}
.time {
  font-size: 20rpx;
}
.seller {
  font-size: 20rpx;
  margin-top: 6rpx;
}
</style>
