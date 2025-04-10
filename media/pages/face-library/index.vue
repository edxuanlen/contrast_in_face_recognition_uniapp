<template>
  <view class="container">
    <view class="title">人脸库管理</view>

    <view class="action-buttons">
      <button class="action-btn" @click="navigateToScan">批量扫描添加</button>
      <button class="action-btn" @click="showAddFaceModal">单个添加人脸</button>
    </view>

    <view class="library-list">
      <view v-if="loading" class="loading">
        <text>加载中...</text>
      </view>

      <view v-else-if="faces.length === 0" class="empty-state">
        <text>人脸库为空</text>
      </view>

      <view v-else class="face-list">
        <view v-for="(face, index) in faces" :key="face.id" class="face-item">
          <image :src="face.image_url" mode="aspectFill" class="face-image"></image>
          <view class="face-info">
            <text v-if="!face.isEditing" class="face-name">{{face.name}}</text>
            <input v-else type="text" v-model="face.editingName" class="face-name-input" @blur="updateFaceName(face)" />
            <text class="face-date">添加时间: {{formatDate(face.created_at)}}</text>
          </view>
          <view class="face-actions">
            <text class="action-text edit" @click="editFaceName(face)">{{face.isEditing ? '保存' : '编辑'}}</text>
            <text class="action-text delete" @click="deleteFace(face)">删除</text>
          </view>
        </view>
      </view>
    </view>

    <!-- 添加人脸的模态框 -->
    <view v-if="showModal" class="modal-mask">
      <view class="modal-content">
        <view class="modal-header">
          <text class="modal-title">添加人脸</text>
          <text class="modal-close" @click="showModal = false">×</text>
        </view>

        <view class="modal-body">
          <view class="form-item">
            <text class="form-label">人脸名称:</text>
            <input type="text" v-model="newFaceName" placeholder="请输入人脸名称" class="form-input" />
          </view>

          <view class="form-item">
            <text class="form-label">人脸图片:</text>
            <view class="image-upload" @click="chooseImage">
              <image v-if="imageUrl" :src="imageUrl" mode="aspectFill" class="preview-image"></image>
              <view v-else class="upload-placeholder">
                <text>点击选择图片</text>
              </view>
            </view>
          </view>
        </view>

        <view class="modal-footer">
          <button class="cancel-btn" @click="showModal = false">取消</button>
          <button class="confirm-btn" @click="addFace" :disabled="!canSubmit">添加</button>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      host: '',
      userInfo: null,
      loading: true,
      faces: [],
      showModal: false,
      newFaceName: '',
      imageFile: null,
      imageUrl: '',
    }
  },
  computed: {
    canSubmit() {
      return this.newFaceName.trim() !== '' && this.imageFile !== null;
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

    this.loadFaceLibrary();
  },
  methods: {
    loadFaceLibrary() {
      this.loading = true;

      uni.request({
        url: this.host + '/api/face_library/list/',
        method: 'GET',
        header: {
          'Authorization': 'Token ' + uni.getStorageSync('token')
        },
        success: (res) => {
          if (res.data.code === 200) {
            this.faces = res.data.data.map(face => ({ ...face, isEditing: false, editingName: face.name }));
          } else {
            uni.showToast({
              title: res.data.message || '加载失败',
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
          this.loading = false;
        }
      });
    },

    navigateToScan() {
      uni.navigateTo({
        url: '/pages/face-library/scan'
      });
    },

    showAddFaceModal() {
      this.showModal = true;
      this.newFaceName = '';
      this.imageFile = null;
      this.imageUrl = '';
    },

    chooseImage() {
      uni.chooseImage({
        count: 1,
        sizeType: ['original', 'compressed'],
        sourceType: ['album', 'camera'],
        success: (res) => {
          this.imageFile = res.tempFiles[0];
          this.imageUrl = res.tempFilePaths[0];
        }
      });
    },

    addFace() {
      if (!this.canSubmit) return;

      uni.showLoading({
        title: '添加中...'
      });

      const formData = new FormData();
      formData.append('name', this.newFaceName);
      formData.append('image', this.imageFile);

      uni.uploadFile({
        url: this.host + '/api/face_library/add/',
        filePath: this.imageUrl,
        name: 'image',
        formData: {
          name: this.newFaceName
        },
        header: {
          'Authorization': 'Token ' + uni.getStorageSync('token')
        },
        success: (res) => {
          const data = JSON.parse(res.data);
          if (data.code === 200) {
            uni.showToast({
              title: '添加成功',
              icon: 'success'
            });
            this.showModal = false;
            this.loadFaceLibrary();
          } else {
            uni.showToast({
              title: data.message || '添加失败',
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
          uni.hideLoading();
        }
      });
    },

    deleteFace(face) {
      uni.showModal({
        title: '确认删除',
        content: `确定要删除"${face.name}"吗？`,
        success: (res) => {
          if (res.confirm) {
            uni.showLoading({
              title: '删除中...'
            });

            uni.request({
              url: this.host + `/api/face_library/delete/${face.id}/`,
              method: 'DELETE',
              header: {
                'Authorization': 'Token ' + uni.getStorageSync('token')
              },
              success: (res) => {
                if (res.data.code === 200) {
                  uni.showToast({
                    title: '删除成功',
                    icon: 'success'
                  });
                  this.loadFaceLibrary();
                } else {
                  uni.showToast({
                    title: res.data.message || '删除失败',
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
                uni.hideLoading();
              }
            });
          }
        }
      });
    },

    editFaceName(face) {
      if (face.isEditing) {
        this.updateFaceName(face);
      } else {
        face.isEditing = true;
        face.editingName = face.name;
      }
    },

    updateFaceName(face) {
      if (!face.editingName.trim() || face.editingName === face.name) {
        face.editingName = face.name;
        face.isEditing = false;
        return;
      }

      uni.showLoading({
        title: '更新中...'
      });

      uni.request({
        url: this.host + `/api/face_library/update/${face.id}/`,
        method: 'PUT',
        data: {
          name: face.editingName
        },
        header: {
          'Authorization': 'Token ' + uni.getStorageSync('token')
        },
        success: (res) => {
          if (res.data.code === 200) {
            face.name = face.editingName;
            uni.showToast({
              title: '更新成功',
              icon: 'success'
            });
          } else {
            face.editingName = face.name;
            uni.showToast({
              title: res.data.message || '更新失败',
              icon: 'none'
            });
          }
        },
        fail: (err) => {
          face.editingName = face.name;
          uni.showToast({
            title: '网络错误，请重试',
            icon: 'none'
          });
          console.error(err);
        },
        complete: () => {
          face.isEditing = false;
          uni.hideLoading();
        }
      });
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

.action-buttons {
  display: flex;
  justify-content: space-between;
  margin-bottom: 20px;
}

.action-btn {
  width: 48%;
  padding: 10px 0;
  background-color: #007aff;
  color: white;
  border-radius: 5px;
  text-align: center;
}

.library-list {
  margin-top: 20px;
}

.loading, .empty-state {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 200px;
  background-color: #f8f8f8;
  border-radius: 10px;
}

.face-list {
  margin-top: 10px;
}

.face-item {
  display: flex;
  background-color: white;
  padding: 15px;
  border-radius: 10px;
  margin-bottom: 15px;
  box-shadow: 0 2px 5px rgba(0,0,0,0.1);
}

.face-image {
  width: 80px;
  height: 80px;
  border-radius: 5px;
}

.face-info {
  flex: 1;
  margin-left: 15px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.face-name {
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 5px;
}

.face-date {
  font-size: 14px;
  color: #666;
}

.face-actions {
  display: flex;
  align-items: center;
}

.action-text {
  padding: 5px 5px;
  border-radius: 5px;
}

.delete {
  color: #ff3b30;
}

/* 模态框样式 */
.modal-mask {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0,0,0,0.6);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  width: 80%;
  background-color: white;
  border-radius: 10px;
  overflow: hidden;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  border-bottom: 1px solid #eee;
}

.modal-title {
  font-size: 18px;
  font-weight: bold;
}

.modal-close {
  font-size: 24px;
  color: #666;
}

.modal-body {
  padding: 15px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  padding: 15px;
  border-top: 1px solid #eee;
}

.cancel-btn, .confirm-btn {
  padding: 8px 20px;
  border-radius: 5px;
  margin-left: 10px;
}

.cancel-btn {
  background-color: #f2f2f2;
  color: #666;
}

.confirm-btn {
  background-color: #007aff;
  color: white;
}

.confirm-btn[disabled] {
  background-color: #cccccc;
}

.image-upload {
  width: 100%;
  height: 200px;
  border: 2px dashed #ddd;
  border-radius: 5px;
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: 10px;
}

.preview-image {
  width: 100%;
  height: 100%;
  border-radius: 5px;
}

.upload-placeholder {
  color: #999;
}
</style>
