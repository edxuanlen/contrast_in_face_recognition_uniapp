<template>
	<view class="container">
		<uni-section title="可以选择最多9张图片" type="line">
			<view class="example-body">
				<uni-file-picker limit="9" @select="handleUpload"></uni-file-picker>
			</view>
		</uni-section>
		<view class="image-container" v-if="imagedata.length">
			<view class="preview-image-wrapper" v-for="(image, index) in imagedata" :key="index">
				<view class="">
					{{names[index]}}
				</view>
				<image :src="image" mode="aspectFit" class="preview-image"></image>
			</view>
		</view>
	</view>
</template>

<script>
	export default {
		data() {
			return {
				imagedata: [], // 改为数组，用于存储多个图片URL
				names: [], // 改为数组，用于存储多个图片URL
			}
		},
		methods: {
			handleUpload(e) {
				const files = e.tempFiles;
				const uploads = [];

				uni.showLoading({
					title: "正在处理",
				});

				files.forEach((file, index) => {
					uploads.push(
						uni.uploadFile({
							url: 'http://localhost:8080/media/tmour/', // 替换为真实的接口地址
							filePath: file.path,
							name: 'file',
							success: (uploadRes) => {
								try {
									const response = JSON.parse(uploadRes.data); // JSON解析
									if (response.path) {
										this.imagedata.push(response.path);   //更新图片地址数据
										this.names.push(response.name);  //返回类型结果
										console.log('Image URL:', response.path);
									} else {
										console.error('No image URL found in the server response.');
									}
								} catch (error) {
									console.error('Failed to parse server response:', error);
								}
							},
							fail: (err) => {
								console.error('Upload failed:', err);
							},
							complete: () => {
								if (index === files.length - 1) {
									uni.hideLoading();
								}
							}
						})
					);
				});
			},
			removeImage(index) {
				this.imagedata.splice(index, 1);
			},
			addImage() {
				// 模拟添加图片的逻辑
				uni.showToast({
					title: '点击添加按钮',
					icon: 'none'
				});
			}
		},
	}
</script>

<style scoped>
	.container {
		padding: 20px;
	}

	.example-body {
		padding: 10px;
		padding-top: 0;
	}

	.image-container {
		margin-top: 20px;
		display: flex;
		flex-direction: column; /* 垂直排列 */
		gap: 10px; /* 图片之间的间距 */
		max-height: calc(100vh - 200px); /* 设置最大高度 */
		overflow-y: auto; /* 添加垂直滚动条 */
	}

	.preview-image-wrapper {
		position: relative;
		border-radius: 8px;
		box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
	}

	.preview-image {
		width: 100%; /* 确保图像宽度填满父元素 */
		max-width: 300px; /* 限制每个图像的最大宽度 */
		max-height: 300px; /* 限制每个图像的最大高度 */
		border-radius: 8px; /* 圆角边框 */
		object-fit: cover; /* 确保图片保持宽高比并覆盖整个容器 */
	}

	.close-button {
		position: absolute;
		top: 5px;
		right: 5px;
		background-color: rgba(0, 0, 0, 0.5);
		color: white;
		border-radius: 50%;
		padding: 5px;
		cursor: pointer;
	}

	.add-button {
		margin-top: 20px;
		text-align: center;
		border: 1px solid #ccc;
		border-radius: 8px;
		padding: 20px;
		cursor: pointer;
	}

	.add-button .iconfont {
		font-size: 50px;
		color: #ccc;
	}
</style>
