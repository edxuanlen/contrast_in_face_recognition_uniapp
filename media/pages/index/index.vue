<template>
  <view class="container">
    <view class="title">人脸识别系统</view>

    <view class="camera-container" v-if="!imageUrl">
      <view class="camera-box">
        <uni-file-picker
          limit="1"
          @select="selectImage"
          title="选择图片"
          file-mediatype="image"
          mode="grid">
        </uni-file-picker>
      </view>
      <button class="primary-btn" @click="takePhoto">
        <img src="/static/ai/camera.png" alt="拍照识别" class="camera-icon" style="width: 20px; height: 20px;">
        拍照识别
      </button>
    </view>

    <view class="result-container" v-if="imageUrl">
      <view class="image-box">
        <image :src="imageUrl" mode="aspectFit" class="preview-image"></image>
        <canvas canvas-id="faceCanvas" class="face-canvas" id="faceCanvas"></canvas>
      </view>

      <view class="result-info" v-if="detectionResults.length > 0">
        <view class="result-item" v-for="(result, index) in detectionResults" :key="index">
          <text class="result-text">人脸 {{index+1}}: {{result.confidence.toFixed(2)}}% 置信度</text>
        </view>
      </view>

      <view class="btn-group">
        <button class="primary-btn" @click="resetDetection">重新检测</button>
        <!-- <button class="secondary-btn" @click="saveResult">保存结果</button> -->
      </view>
    </view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      imageUrl: '',
      tempFilePath: '',
      detectionResults: [],
      canvasContext: null,
      host: '',
      userInfo: null
    }
  },
  onLoad() {
    this.host = getApp().globalData.host;
    this.userInfo = uni.getStorageSync('userInfo');
    if (!this.userInfo) {
      uni.redirectTo({
        url: '/pages/login/login'
      });
    }
  },
  methods: {
    selectImage(e) {
      if (e.tempFiles.length > 0) {
        this.tempFilePath = e.tempFiles[0].path;
        this.imageUrl = this.tempFilePath;
        this.detectFaces();
      }
    },

    takePhoto() {
      uni.chooseImage({
        count: 1,
        sourceType: ['camera'],
        success: (res) => {
          this.tempFilePath = res.tempFilePaths[0];
          this.imageUrl = this.tempFilePath;
          this.detectFaces();
        }
      });
    },

    detectFaces() {
      uni.showLoading({
        title: '识别中...'
      });

      uni.uploadFile({
        url: this.host + '/api/detect_face/',
        filePath: this.tempFilePath,
        name: 'image',
        header: {
          'Authorization': 'Token ' + uni.getStorageSync('token')
        },
        success: (res) => {
          uni.hideLoading();
          const data = JSON.parse(res.data);
          if (data.code === 200) {
            this.detectionResults = data.results;
            this.$nextTick(() => {
              this.drawDetectionBoxes();
              this.saveResult();
            });
          } else {
            uni.showToast({
              title: data.message || '识别失败',
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
      query.select('#faceCanvas').boundingClientRect(data => {
        const canvas = uni.createCanvasContext('faceCanvas', this);

        uni.getImageInfo({
          src: this.imageUrl,
          success: (imgInfo) => {
            const canvasWidth = data.width;
            const canvasHeight = data.height;
            const imgWidth = imgInfo.width;
            const imgHeight = imgInfo.height;

            console.log(`Canvas Size: ${canvasWidth}x${canvasHeight}, Image Size: ${imgWidth}x${imgHeight}`);

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

            this.detectionResults.forEach((face, index) => {
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
              let labelText = `人脸 ${index+1}`;
              if (face.recognition && face.recognition.similarity > 0.5) {
                labelText += `: ${face.recognition.name}`;
              }
              canvas.fillText(labelText, boxX + 5, boxY - 10);
            });

            canvas.draw();
          }
        });
      }).exec();
    },

    resetDetection() {
      this.imageUrl = '';
      this.tempFilePath = '';
      this.detectionResults = [];
    },

    saveResult() {
      if (this.detectionResults.length === 0) {
        uni.showToast({
          title: '没有检测结果可保存',
          icon: 'none'
        });
        return;
      }

      uni.showLoading({
        title: '保存中...'
      });

      uni.uploadFile({
        url: this.host + '/api/save_detection/',
        filePath: this.tempFilePath,
        name: 'image',
        formData: {
          results: JSON.stringify(this.detectionResults)
        },
        header: {
          'Authorization': 'Token ' + uni.getStorageSync('token')
        },
        success: (res) => {
          uni.hideLoading();
          const data = JSON.parse(res.data);
          if (data.code === 200) {
            uni.showToast({
              title: '保存成功',
              icon: 'success'
            });
          } else {
            uni.showToast({
              title: data.message || '保存失败',
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
    }
  }
}
</script>

<style>
.container {
  padding: 20px;
  height: 100%;
}

.title {
  font-size: 24px;
  font-weight: bold;
  text-align: center;
  margin-bottom: 30px;
}

.camera-container {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.camera-box {
  width: 100%;
  margin-bottom: 20px;
}

.result-container {
  width: 100%;
}

.image-box {
  position: relative;
  width: 100%;
  height: 400px;
  margin-bottom: 20px;
}

.preview-image {
  width: 100%;
  height: 100%;
}

.face-canvas {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 10;
}

.result-info {
  margin-bottom: 20px;
}

.result-item {
  padding: 10px;
  background-color: #f0f0f0;
  margin-bottom: 5px;
  border-radius: 5px;
}

.result-text {
  font-size: 16px;
}

.btn-group {
  display: flex;
  justify-content: space-between;
}

.primary-btn {
  background-color: #007aff;
  color: white;
  /* padding: 10px 10px; */
  border-radius: 5px;
  margin: 10px 5px;
  flex: 1;
  height: 60px;
}

.secondary-btn {
  background-color: #5ac8fa;
  color: white;
  padding: 10px 20px;
  border-radius: 5px;
  margin: 10px 5px;
  flex: 1;
}
</style>
