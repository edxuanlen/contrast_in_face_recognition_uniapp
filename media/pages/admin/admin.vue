<template>
  <view class="container">
    <view class="header">
      <text class="title">管理员控制台</text>
    </view>
    <button class="add-btn" @click="showCreateUserModal">添加用户</button>

    <view class="user-list">
      <view class="list-header">
        <text class="header-cell">用户名</text>
        <text class="header-cell">邮箱</text>
        <text class="header-cell">注册时间</text>
        <text class="header-cell">管理员</text>
        <text class="header-cell">操作</text>
      </view>

      <view class="list-item" v-for="user in users" :key="user.id">
        <text class="cell">{{ user.username }}</text>
        <text class="cell">{{ user.email }}</text>
        <text class="cell">{{ formatDate(user.date_joined) }}</text>
        <view class="cell">
          <switch
            :checked="user.is_admin"
            @change="toggleAdmin(user)"
            :disabled="user.id === currentUserId"
          />
        </view>
        <view class="cell actions">
          <view class="button-container">
            <button
              class="action-btn edit-btn"
              @click="showEditUserModal(user)"
              style="font-size: 12px;"
            >编辑</button>
            <button
              class="action-btn delete-btn"
              @click="deleteUser(user)"
              :disabled="user.id === currentUserId"
              style="font-size: 12px;"
            >删除</button>
          </view>
        </view>
      </view>
    </view>

    <!-- 替换 uni-popup 为原生弹窗 -->
    <view class="modal" v-if="showCreateModal">
      <view class="modal-mask" @click="hideCreateUserModal"></view>
      <view class="popup-content">
        <view class="popup-title">创建新用户</view>
        <view class="form-item">
          <input
            class="input"
            v-model="newUser.username"
            placeholder="用户名"
          />
        </view>
        <view class="form-item">
          <input
            class="input"
            v-model="newUser.password"
            type="password"
            placeholder="密码"
          />
        </view>
        <view class="form-item">
          <input
            class="input"
            v-model="newUser.email"
            type="email"
            placeholder="邮箱"
          />
        </view>
        <view class="form-item radio-group">
          <radio-group @change="handleAdminChange">
            <label class="radio">
              <radio value="true" :checked="newUser.is_admin" />设为管理员
            </label>
          </radio-group>
        </view>
        <view class="popup-buttons">
          <button
            class="cancel-btn"
            @click="hideCreateUserModal"
          >取消</button>
          <button
            class="confirm-btn"
            @click="createUser"
          >创建</button>
        </view>
      </view>
    </view>

    <view class="modal" v-if="showEditModal">
    <view class="modal-mask" @click="hideEditUserModal"></view>
    <view class="popup-content">
      <view class="popup-title">编辑用户</view>
      <view class="form-item">
        <input
          class="input"
          v-model="editingUser.username"
          placeholder="用户名"
        />
      </view>
      <view class="form-item">
        <input
          class="input"
          v-model="editingUser.email"
          type="email"
          placeholder="邮箱"
        />
      </view>
      <view class="form-item">
        <input
          class="input"
          v-model="editingUser.password"
          type="password"
          placeholder="新密码（留空则不修改）"
        />
      </view>
      <view class="popup-buttons">
        <button
          class="cancel-btn"
          @click="hideEditUserModal"
        >取消</button>
        <button
          class="confirm-btn"
          @click="updateUser"
        >保存</button>
      </view>
    </view>
  </view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      users: [],
      currentUserId: null,
      host: '',
      newUser: {
        username: '',
        password: '',
        email: '',
        is_admin: false
      },
      showCreateModal: false,
      showEditModal: false,
      editingUser: {
        id: null,
        username: '',
        email: '',
        password: ''
      }
    }
  },

  created() {
    this.host = getApp().globalData.host;
    // 从本地存储获取用户信息
    const userInfo = uni.getStorageSync('userInfo');
    if (userInfo) {
      this.currentUserId = userInfo.id;
      // 检查是否是管理员
      if (!userInfo.is_admin) {
        uni.showToast({
          title: '无权访问此页面',
          icon: 'none'
        });
        // 跳转回首页或其他页面
        uni.navigateBack();
        return;
      }
    }
    this.loadUsers();
  },

  methods: {


    showEditUserModal(user) {
      this.editingUser = {
        id: user.id,
        username: user.username,
        email: user.email,
        password: ''
      };
      this.showEditModal = true;
    },

    hideEditUserModal() {
      this.showEditModal = false;
      this.editingUser = {
        id: null,
        username: '',
        email: '',
        password: ''
      };
    },

    updateUser() {
      if (!this.editingUser.username || !this.editingUser.email) {
        uni.showToast({
          title: '用户名和邮箱不能为空',
          icon: 'none'
        });
        return;
      }

      const token = uni.getStorageSync('token');
      const userData = {
        username: this.editingUser.username,
        email: this.editingUser.email
      };

      // 只有当密码字段有值时才包含密码
      if (this.editingUser.password) {
        userData.password = this.editingUser.password;
      }

      uni.request({
        url: this.host + `/api/admin/users/${this.editingUser.id}/`,
        method: 'PUT',
        header: {
          'Authorization': 'Token ' + token,
          'Content-Type': 'application/json'
        },
        data: userData,
        success: (res) => {
          if (res.data.code === 200) {
            uni.showToast({
              title: '更新成功',
              icon: 'success'
            });
            this.hideEditUserModal();
            this.loadUsers();
          } else {
            uni.showToast({
              title: res.data.message || '更新失败',
              icon: 'none'
            });
          }
        },
        fail: () => {
          uni.showToast({
            title: '网络错误',
            icon: 'none'
          });
        }
      });
    },


    loadUsers() {
      const token = uni.getStorageSync('token');

      uni.request({
        url: this.host + '/api/admin/users/',
        method: 'GET',
        header: {
          'Authorization': 'Token ' + token
        },
        success: (res) => {
          if (res.data.code === 200) {
            this.users = res.data.data;
          } else {
            uni.showToast({
              title: '加载用户列表失败',
              icon: 'none'
            });
          }
        },
        fail: () => {
          uni.showToast({
            title: '网络错误',
            icon: 'none'
          });
        }
      });
    },

    toggleAdmin(user) {
      const token = uni.getStorageSync('token');

      uni.showModal({
        title: '确认操作',
        content: `确定要${user.is_admin ? '取消' : '授予'} ${user.username} 的管理员权限吗？`,
        success: (res) => {
          if (res.confirm) {
            uni.request({
              url: this.host + `/api/admin/users/${user.id}/toggle-admin/`,
              method: 'POST',
              header: {
                'Authorization': 'Token ' + token
              },
              success: (res) => {
                if (res.data.code === 200) {
                  uni.showToast({
                    title: '操作成功',
                    icon: 'success'
                  });
                  this.loadUsers();
                } else {
                  uni.showToast({
                    title: res.data.message || '操作失败',
                    icon: 'none'
                  });
                }
              }
            });
          }
        }
      });
    },

    deleteUser(user) {
      const token = uni.getStorageSync('token');

      uni.showModal({
        title: '确认删除',
        content: `确定要删除用户 ${user.username} 吗？此操作不可恢复！`,
        success: (res) => {
          if (res.confirm) {
            uni.request({
              url: this.host + `/api/admin/users/${user.id}/`,
              method: 'DELETE',
              header: {
                'Authorization': 'Token ' + token
              },
              success: (res) => {
                if (res.data.code === 200) {
                  uni.showToast({
                    title: '删除成功',
                    icon: 'success'
                  });
                  this.loadUsers();
                } else {
                  uni.showToast({
                    title: res.data.message || '删除失败',
                    icon: 'none'
                  });
                }
              }
            });
          }
        }
      });
    },

    formatDate(dateString) {
      const date = new Date(dateString);
      return date.toLocaleDateString();
    },

    showCreateUserModal() {
      this.newUser = {
        username: '',
        password: '',
        email: '',
        is_admin: false
      };
      this.showCreateModal = true;
    },

    hideCreateUserModal() {
      this.showCreateModal = false;
    },

    handleAdminChange(e) {
      console.log('Radio changed:', e);
      this.newUser.is_admin = e.detail.value === 'true';
      console.log('Is admin:', this.newUser.is_admin);
    },

    createUser() {
      if (!this.newUser.username || !this.newUser.password) {
        uni.showToast({
          title: '用户名和密码不能为空',
          icon: 'none'
        });
        return;
      }

      const token = uni.getStorageSync('token');

      // 确保发送正确的数据格式
      const userData = {
        username: this.newUser.username,
        password: this.newUser.password,
        email: this.newUser.email,
        is_admin: Boolean(this.newUser.is_admin) // 确保是布尔值
      };

      uni.request({
        url: this.host + '/api/admin/users/create/',
        method: 'POST',
        header: {
          'Authorization': 'Token ' + token,
          'Content-Type': 'application/json'
        },
        data: userData,
        success: (res) => {
          if (res.data.code === 200) {
            console.log('Created user:', res.data.data); // 查看返回的用户数据
            uni.showToast({
              title: '创建成功',
              icon: 'success'
            });
            this.hideCreateUserModal();
            this.loadUsers();
          } else {
            uni.showToast({
              title: res.data.message || '创建失败',
              icon: 'none'
            });
          }
        },
        fail: () => {
          uni.showToast({
            title: '网络错误',
            icon: 'none'
          });
        }
      });
    }
  }
}
</script>


// ... existing code ...

<style>
.container {
  padding: 10px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  flex-wrap: wrap;
}

.title {
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 10px;
  width: 100%;
}

.add-btn {
  width: 40%;
  height: 44px;
  background: #1890ff;
  color: white;
  border-radius: 4px;
  font-size: 12px;
  margin-bottom: 10px;
}

.user-list {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  width: 100%;
  overflow-x: auto;
}

.list-header {
  display: flex;
  padding: 12px 8px;
  background: #f5f5f5;
  border-top-left-radius: 8px;
  border-top-right-radius: 8px;
}

.list-item {
  display: flex;
  padding: 12px 8px;
  border-bottom: 1px solid #eee;
  font-size: 14px;
}

.header-cell,
.cell {
  flex: 1;
  padding: 0 4px;
  min-width: 80px;
  word-break: break-all;
  font-size: 14px;
}

.actions {
  display: flex;
  justify-content: center;
  gap: 4px;
  min-width: 100px;
}

.action-btn {
  flex: 1;
  padding: 2px 6px;
  border-radius: 3px;
  font-size: 12px;
  height: 16px;
  line-height: 16px;
  max-width: 45px;
}

.edit-btn {
  background: #1890ff;
  color: white;
}

.delete-btn {
  background: #ff4d4f;
  color: white;
}

.delete-btn[disabled] {
  background: #ccc;
}

/* 弹窗样式优化 */
.popup-content {
  position: relative;
  z-index: 1000;
  background: white;
  padding: 15px;
  border-radius: 8px;
  width: 90%;
  max-width: none;
}

.popup-title {
  font-size: 16px;
  margin-bottom: 15px;
}

.form-item {
  margin-bottom: 12px;
}

.input {
  width: 100%;
  height: 44px;
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 0 12px;
  font-size: 16px;
  box-sizing: border-box;
}

.radio-group {
  padding: 0;
  margin: 10px 0;
}

.radio {
  display: flex;
  align-items: center;
  height: 44px;
}

.popup-buttons {
  display: flex;
  justify-content: space-between;
  margin-top: 20px;
}

.cancel-btn,
.confirm-btn {
  flex: 1;
  margin: 0 5px;
  /* height: 44px; */
  line-height: 44px;
  border-radius: 4px;
  font-size: 16px;
}

/* 适配小屏幕 */
@media screen and (max-width: 375px) {
  .header-cell,
  .cell {
    font-size: 12px;
    padding: 0 2px;
    min-width: 60px;
  }

  .delete-btn {
    font-size: 12px;
    padding: 2px 6px;
  }

  .popup-content {
    padding: 12px;
  }

  .input {
    height: 40px;
    font-size: 14px;
  }
}

.button-container {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

</style>
