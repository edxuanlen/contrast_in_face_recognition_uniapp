<template>
  <view class="container">
    <view class="profile-header">
      <image class="avatar" src="/static/avatar/user.jpg"></image>
      <view class="user-info">
        <text class="username">{{userInfo.username}}</text>
        <text class="role">({{userInfo.is_admin ? '管理员' : '普通用户'}})</text>
      </view>
    </view>

    <view class="menu-list">
      <view class="menu-item" @click="goToHistory" v-if="userInfo.is_admin">
        <uni-icons type="calendar" size="24" color="#007aff"></uni-icons>
        <text class="menu-text">历史记录</text>
        <uni-icons type="right" size="16" color="#999"></uni-icons>
      </view>

      <!-- <view class="menu-item">
        <uni-icons type="person" size="24" color="#007aff"></uni-icons>
        <text class="menu-text">个人信息</text>
        <uni-icons type="right" size="16" color="#999"></uni-icons>
      </view>

      <view class="menu-item">
        <uni-icons type="locked" size="24" color="#007aff"></uni-icons>
        <text class="menu-text">修改密码</text>
        <uni-icons type="right" size="16" color="#999"></uni-icons>
      </view> -->

      <view class="menu-item" @click="logout">
        <uni-icons type="closeempty" size="24" color="#ff3b30"></uni-icons>
        <text class="menu-text logout-text">退出登录</text>
        <uni-icons type="right" size="16" color="#999"></uni-icons>
      </view>
    </view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      userInfo: null
    }
  },
  onLoad() {
    this.userInfo = uni.getStorageSync('userInfo');
    if (!this.userInfo) {
      uni.redirectTo({
        url: '/pages/login/login'
      });
    }
  },
  methods: {
    goToHistory() {
      uni.navigateTo({
        url: '/pages/history/history'
      });
    },

    logout() {
      uni.showModal({
        title: '提示',
        content: '确定要退出登录吗？',
        success: (res) => {
          if (res.confirm) {
            uni.removeStorageSync('userInfo');
            uni.removeStorageSync('token');
            uni.redirectTo({
              url: '/pages/login/login'
            });
          }
        }
      });
    }
  }
}
</script>

<style>
.container {
  padding: 20px;
}

.profile-header {
  display: flex;
  align-items: center;
  padding: 20px;
  background-color: #f8f8f8;
  border-radius: 10px;
  margin-bottom: 30px;
}

.avatar {
  width: 80px;
  height: 80px;
  border-radius: 40px;
  margin-right: 20px;
}

.user-info {
  flex: 1;
  padding-left: 10px;
}

.username {
  font-size: 20px;
  font-weight: bold;
  margin-bottom: 5px;
}

.role {
  font-size: 14px;
  color: #666;
  margin-left: 16px;
  margin-top: 5px;
}

.menu-list {
  background-color: #f8f8f8;
  border-radius: 10px;
  overflow: hidden;
}

.menu-item {
  display: flex;
  align-items: center;
  padding: 15px 20px;
  background-color: white;
  margin-bottom: 1px;
}

.menu-text {
  flex: 1;
  margin-left: 15px;
  font-size: 16px;
}

.logout-text {
  color: #ff3b30;
}
</style>
