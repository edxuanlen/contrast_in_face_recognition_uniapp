<template>
    <view class="container">
      <view class="title">扫描目录添加人脸</view>

      <view v-if="!isAdmin" class="no-permission">
        <text>您没有权限使用此功能</text>
      </view>

      <view v-else class="scan-form">
        <view class="form-item">
          <text class="form-label">目录路径:</text>
          <input type="text" v-model="directoryPath" placeholder="请输入完整的目录路径" class="form-input" />
        </view>

        <view class="form-item">
          <text class="form-label">名称前缀:</text>
          <input type="text" v-model="namePrefix" placeholder="人脸名称前缀，默认为Person" class="form-input" />
        </view>

        <button @click="scanDirectory" class="scan-button" :disabled="isScanning">{{ isScanning ? '扫描中...' : '开始扫描' }}</button>

        <view v-if="scanResult" class="scan-result">
          <view class="result-summary">
            <text class="result-title">扫描结果:</text>
            <view class="stat-item">
              <text class="stat-label">总图片数:</text>
              <text class="stat-value">{{ scanResult.stats.total_images }}</text>
            </view>
            <view class="stat-item">
              <text class="stat-label">成功处理:</text>
              <text class="stat-value">{{ scanResult.stats.processed }}</text>
            </view>
            <view class="stat-item">
              <text class="stat-label">添加数量:</text>
              <text class="stat-value">{{ scanResult.stats.added }}</text>
            </view>
            <view class="stat-item">
              <text class="stat-label">无人脸跳过:</text>
              <text class="stat-value">{{ scanResult.stats.skipped_no_face }}</text>
            </view>
            <view class="stat-item">
              <text class="stat-label">多人脸跳过:</text>
              <text class="stat-value">{{ scanResult.stats.skipped_multiple_faces }}</text>
            </view>
            <view class="stat-item">
              <text class="stat-label">已存在跳过:</text>
              <text class="stat-value">{{ scanResult.stats.skipped_existing }}</text>
            </view>
            <view class="stat-item">
              <text class="stat-label">错误数量:</text>
              <text class="stat-value">{{ scanResult.stats.errors }}</text>
            </view>
          </view>

          <view class="details-title">详细记录:</view>
          <scroll-view scroll-y="true" class="detail-list">
            <view v-for="(item, index) in scanResult.results" :key="index"
                  :class="['detail-item', `status-${item.status}`]">
              <text class="detail-filename">{{ item.filename }}</text>
              <text class="detail-status">{{ getStatusText(item) }}</text>
            </view>
          </scroll-view>
        </view>
      </view>
    </view>
  </template>

  <script>
  export default {
    data() {
      return {
        isAdmin: false,
        userInfo: null,
        host: '',
        directoryPath: '',
        namePrefix: 'Person',
        isScanning: false,
        scanResult: null
      }
    },
    onLoad() {
      this.host = getApp().globalData.host;
      this.userInfo = uni.getStorageSync('userInfo');

      if (!this.userInfo) {
        uni.redirectTo({
          url: '/pages/login/login'
        });
        return;
      }

      this.isAdmin = this.userInfo.is_admin;
    },
    methods: {
      scanDirectory() {
        if (!this.directoryPath) {
          uni.showToast({
            title: '请输入目录路径',
            icon: 'none'
          });
          return;
        }

        this.isScanning = true;
        this.scanResult = null;

        uni.request({
          url: this.host + '/api/face_library/scan_directory/',
          method: 'POST',
          header: {
            'Authorization': 'Token ' + uni.getStorageSync('token'),
            'Content-Type': 'application/json'
          },
          data: {
            directory_path: this.directoryPath,
            name_prefix: this.namePrefix
          },
          success: (res) => {
            if (res.data.code === 200) {
              this.scanResult = res.data;
            } else {
              uni.showToast({
                title: res.data.message || '扫描失败',
                icon: 'none'
              });
            }
          },
          fail: (err) => {
            uni.showToast({
              title: '网络错误，请重试',
              icon: 'none'
            });
            console.error(err);
          },
          complete: () => {
            this.isScanning = false;
          }
        });
      },

      getStatusText(item) {
        switch(item.status) {
          case 'added':
            return `已添加: ${item.name}`;
          case 'skipped':
            return `已跳过: ${item.reason}`;
          case 'error':
            return `错误: ${item.reason}`;
          default:
            return item.status;
        }
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

  .no-permission {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 200px;
    background-color: #f8f8f8;
    border-radius: 10px;
  }

  .scan-form {
    background-color: #f8f8f8;
    padding: 20px;
    border-radius: 10px;
  }

  .form-item {
    margin-bottom: 15px;
    width: 90%;

  }

  .form-label {
    display: block;
    margin-bottom: 5px;
    font-weight: bold;
  }

  .form-input {
    width: 100%;
    padding: 10px;
    border: 1px solid #ddd;
    border-radius: 5px;
    background-color: white;
  }

  .scan-button {
    width: 100%;
    padding: 12px 0;
    background-color: #007aff;
    color: white;
    border-radius: 5px;
    text-align: center;
    margin: 20px 0;
  }

  .scan-button[disabled] {
    background-color: #cccccc;
  }

  .scan-result {
    margin-top: 20px;
  }

  .result-summary {
    background-color: white;
    border-radius: 10px;
    padding: 15px;
    margin-bottom: 20px;
  }

  .result-title {
    font-size: 18px;
    font-weight: bold;
    margin-bottom: 10px;
    display: block;
  }

  .stat-item {
    display: flex;
    justify-content: space-between;
    margin-bottom: 5px;
  }

  .details-title {
    font-size: 16px;
    font-weight: bold;
    margin: 15px 0 10px 0;
  }

  .detail-list {
    height: 300px;
    background-color: white;
    border-radius: 10px;
    padding: 10px;
  }

  .detail-item {
    padding: 10px;
    border-bottom: 1px solid #eee;
    display: flex;
    justify-content: space-between;
  }

  .detail-item:last-child {
    border-bottom: none;
  }

  .status-added {
    background-color: #e6f7e6;
  }

  .status-skipped {
    background-color: #f7f7e6;
  }

  .status-error {
    background-color: #f7e6e6;
  }

  .detail-filename {
    font-weight: bold;
  }

  .detail-status {
    color: #666;
  }
  </style>
