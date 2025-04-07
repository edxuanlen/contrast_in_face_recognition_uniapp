<template>
  <view class="container">
    <view class="title">检测详情</view>

    <view class="detail-container" v-if="detailData">
      <view class="image-box">
        <image :src="detailData.image_url" mode="aspectFit" class="detail-image"></image>
        <canvas canvas-id="detailCanvas" class="detail-canvas" id="detailCanvas"></canvas>
      </view>

      <view class="info-section">
        <view class="info-item">
          <text class="info-label">检测时间:</text>
          <text class="info-value">{{formatDate(detailData.created_at)}}</text>
        </view>

        <view class="info-item">
          <text class="info-label">检测人脸数:</text>
          <text class="info-value">{{detailData.face_count}}</text>
        </view>

        <view class="info-item">
          <text class="info-label">用户:</text>
          <text class="info-value">{{detailData.user_name}}</text>
        </view>
      </view>

      <view class="faces-section">
        <view class="section-title">检测结果</view>

        <view class="face-item" v-for="(face, index) in detailData.faces" :key="index">
          <view class="face-header">
            <text class="face-title">人脸 {{index+1}}</text>
            <text class="face-confidence">置信度: {{(face.confidence * 100).toFixed(2)}}%</text>
          </view>

          <view class="face-coords">
            <text>坐标: [{{face.bbox.join(', ')}}]</text>
          </view>
        </view>
      </view>
    </view>

    <view v-else class="loading">
      <text>加载中...</text>
    </view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      detailId: null,
      detailData: null,
      host: '',
      userInfo: null
    }
  },
  onLoad(options) {
    this.host = getApp().globalData.host;
    this.userInfo = uni.getStorageSync('userInfo');

    if (!this.userInfo) {
      uni.redirectTo({
        url: '/pages/login/login'
      });
      return;
    }

    if (!this.userInfo.is_admin) {
      uni.showToast({
        title: '您没有权限查看此页面',
        icon: 'none'
      });
      setTimeout(() => {
        uni.navigateBack();
      }, 1500);
      return;
    }

    this.detailId = options.id;
    this.loadDetail();
  },
  methods: {
    loadDetail() {
      uni.showLoading({
        title: '加载中...'
      });

      uni.request({
        url: this.host + `/api/detection_detail/${this.detailId}/`,
        method: 'GET',
        header: {
          'Authorization': 'Token ' + uni.getStorageSync('token')
        },
        success: (res) => {
          uni.hideLoading();
          if (res.data.code === 200) {
            this.detailData = res.data.data;
            this.$nextTick(() => {
              this.drawDetectionBoxes();
            });
          } else {
            uni.showToast({
              title: res.data.message || '加载失败',
              icon: 'none'
            });
          }
        },
        fail: (err) => {
          uni.hideLoading();
          uni.showToast({
            title: '网络错误，请重试',
            icon: 'none'
          });
          console.error(err);
        }
      });
    },

    drawDetectionBoxes() {
      const query = uni.createSelectorQuery().in(this);
      query.select('#detailCanvas').boundingClientRect(data => {
        const canvas = uni.createCanvasContext('detailCanvas', this);

        uni.getImageInfo({
          src: this.detailData.image_url,
          success: (imgInfo) => {
            const canvasWidth = data.width;
            const canvasHeight = data.height;
            const imgWidth = imgInfo.width;
            const imgHeight = imgInfo.height;


            // 计算图片在Canvas中的实际显示尺寸和位置
            let displayWidth, displayHeight, offsetX, offsetY;

            // 计算图片的宽高比
            const imgRatio = imgWidth / imgHeight;
            const canvasRatio = canvasWidth / canvasHeight;

            if (imgRatio > canvasRatio) {
              // 图片比Canvas更宽，以宽度为基准
              displayWidth = canvasWidth;
              displayHeight = canvasWidth / imgRatio;
              offsetX = 0;
              offsetY = (canvasHeight - displayHeight) / 2;
            } else {
              // 图片比Canvas更高，以高度为基准
              displayHeight = canvasHeight;
              displayWidth = canvasHeight * imgRatio;
              offsetX = (canvasWidth - displayWidth) / 2;
              offsetY = 0;
            }

            // 计算缩放比例
            const scaleX = displayWidth / imgWidth;
            const scaleY = displayHeight / imgHeight;

            console.log(`Display Size: ${displayWidth}x${displayHeight}, Offset: (${offsetX}, ${offsetY})`);

            canvas.clearRect(0, 0, canvasWidth, canvasHeight);

            this.detailData.faces.forEach((face, index) => {
              const [x1, y1, x2, y2] = face.bbox;

              // 使用缩放比例和偏移量计算框的位置
              const boxX = x1 * scaleX + offsetX;
              const boxY = y1 * scaleY + offsetY;
              const boxWidth = (x2 - x1) * scaleX;
              const boxHeight = (y2 - y1) * scaleY;

              console.log(`Face ${index + 1} - Original: [${x1}, ${y1}, ${x2}, ${y2}], Canvas: [${boxX}, ${boxY}, ${boxWidth}, ${boxHeight}]`);

              // 绘制边框
              canvas.setStrokeStyle('#00ff00');
              canvas.setLineWidth(3);
              canvas.strokeRect(boxX, boxY, boxWidth, boxHeight);

              // 绘制标签
              canvas.setFillStyle('rgba(0, 255, 0, 0.7)');
              canvas.fillRect(boxX, boxY - 30, 120, 30);
              canvas.setFillStyle('#ffffff');
              canvas.setFontSize(14);
              canvas.fillText(`人脸 ${index+1}: ${(face.confidence * 100).toFixed(0)}%`, boxX + 5, boxY - 10);
            });

            canvas.draw();
          }
        });
      }).exec();
    },
    formatDate(dateString) {
      const date = new Date(dateString);
      return `${date.getFullYear()}-${(date.getMonth() + 1).toString().padStart(2, '0')}-${date.getDate().toString().padStart(2, '0')} ${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`;
    }
  }
}
</script>

<style>
.container {
  padding: 20px;
}

.title {
  font-size: 24px;
  font-weight: bold;
  text-align: center;
  margin-bottom: 30px;
}

.detail-container {
  width: 100%;
}

.image-box {
  position: relative;
  width: 100%;
  height: 400px;
  margin-bottom: 20px;
}

.detail-image {
  width: 100%;
  height: 100%;
}

.detail-canvas {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 10;
}

.info-section {
  background-color: #f8f8f8;
  padding: 15px;
  border-radius: 10px;
  margin-bottom: 20px;
}

.info-item {
  display: flex;
  margin-bottom: 10px;
}

.info-label {
  font-weight: bold;
  width: 100px;
}

.info-value {
  flex: 1;
}

.faces-section {
  background-color: #f8f8f8;
  padding: 15px;
  border-radius: 10px;
}

.section-title {
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 15px;
}

.face-item {
  background-color: white;
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 10px;
}

.face-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
}

.face-title {
  font-weight: bold;
}

.face-confidence {
  color: #007aff;
}

.face-coords {
  color: #666;
}

.loading {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 200px;
}
</style>
