<template>
    <view class="container">
      <view class="title">历史记录</view>

      <view v-if="!isAdmin" class="no-permission">
        <text>您没有权限查看历史记录</text>
      </view>

      <view v-else>
        <view class="filter-bar">
          <picker mode="date" :value="startDate" @change="onStartDateChange">
            <view class="picker-item">
              <text>Begin: {{startDate}}</text>
            </view>
          </picker>
          <picker mode="date" :value="endDate" @change="onEndDateChange">
            <view class="picker-item">
              <text>End: {{endDate}}</text>
            </view>
          </picker>
          <button class="filter-btn" @click="loadHistory">Find</button>
        </view>

        <view class="history-list">
          <view v-if="historyItems.length === 0" class="empty-state">
            <text>暂无历史记录</text>
          </view>

          <view v-else class="history-item" v-for="(item, index) in historyItems" :key="index">
            <view class="item-content" @click="viewDetail(item)">
              <image :src="item.image_url" mode="aspectFill" class="history-image"></image>
              <view class="history-info">
                <text class="history-date">{{formatDate(item.created_at)}}</text>
                <text class="history-count">检测到 {{item.face_count}} 个人脸</text>
              </view>
            </view>
            <view class="delete-btn" @click.stop="confirmDelete(item)">
              <text class="delete-icon">×</text>
            </view>
          </view>
        </view>
      </view>
    </view>
  </template>

  <script>
  export default {
    data() {
      return {
        isAdmin: false,
        historyItems: [],
        startDate: this.formatDateForPicker(new Date(Date.now() - 30 * 24 * 60 * 60 * 1000)),
        endDate: this.formatDateForPicker(new Date()),
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
        return;
      }

      this.isAdmin = this.userInfo.is_admin;

      if (this.isAdmin) {
        this.loadHistory();
      }
    },
    methods: {
      loadHistory() {
        uni.showLoading({
          title: '加载中...'
        });

        uni.request({
          url: this.host + '/api/detection_history/',
          method: 'GET',
          data: {
            start_date: this.startDate,
            end_date: this.endDate
          },
          header: {
            'Authorization': 'Token ' + uni.getStorageSync('token')
          },
          success: (res) => {
            uni.hideLoading();
            if (res.data.code === 200) {
              this.historyItems = res.data.data;
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

      viewDetail(item) {
        uni.navigateTo({
          url: `/pages/detail/detail?id=${item.id}`
        });
      },

      confirmDelete(item) {
        uni.showModal({
          title: '确认删除',
          content: '确定要删除这条历史记录吗？',
          success: (res) => {
            if (res.confirm) {
              this.deleteHistory(item.id);
            }
          }
        });
      },

      deleteHistory(id) {
        uni.showLoading({
          title: '删除中...'
        });

        uni.request({
          url: `${this.host}/api/detection_history/${id}/`,
          method: 'DELETE',
          header: {
            'Authorization': 'Token ' + uni.getStorageSync('token')
          },
          success: (res) => {
            uni.hideLoading();
            if (res.data.code === 200) {
              uni.showToast({
                title: '删除成功',
                icon: 'success'
              });
              // 从列表中移除已删除的项
              this.historyItems = this.historyItems.filter(item => item.id !== id);
            } else {
              uni.showToast({
                title: res.data.message || '删除失败',
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

      formatDate(dateString) {
        const date = new Date(dateString);
        return `${date.getFullYear()}-${(date.getMonth() + 1).toString().padStart(2, '0')}-${date.getDate().toString().padStart(2, '0')} ${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`;
      },

      formatDateForPicker(date) {
        return `${date.getFullYear()}-${(date.getMonth() + 1).toString().padStart(2, '0')}-${date.getDate().toString().padStart(2, '0')}`;
      },

      onStartDateChange(e) {
        this.startDate = e.detail.value;
      },

      onEndDateChange(e) {
        this.endDate = e.detail.value;
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

  .filter-bar {
    display: flex;
    justify-content: space-between;
    margin-bottom: 20px;
    background-color: #f0f0f0;
    padding: 10px;
    border-radius: 5px;
  }

  .picker-item {
    padding: 5px 10px;
    background-color: white;
    border-radius: 5px;
  }

  .filter-btn {
    background-color: #007aff;
    color: white;
    padding: 0 15px;
    border-radius: 5px;
    font-size: 14px;
  }

  .history-list {
    margin-top: 20px;
  }

  .empty-state {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 200px;
    background-color: #f8f8f8;
    border-radius: 10px;
  }

  .history-item {
    display: flex;
    margin-bottom: 15px;
    background-color: white;
    border-radius: 10px;
    overflow: hidden;
    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
  }

  .item-content {
    display: flex;
    flex: 1;
  }

  .history-image {
    width: 100px;
    height: 100px;
  }

  .history-info {
    flex: 1;
    padding: 15px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
  }

  .history-date {
    font-size: 14px;
    color: #666;
  }

  .history-count {
    font-size: 16px;
    font-weight: bold;
  }

  .delete-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 50px;
    background-color: #ff3b30;
    color: white;
  }

  .delete-icon {
    font-size: 24px;
    font-weight: bold;
  }
  </style>
