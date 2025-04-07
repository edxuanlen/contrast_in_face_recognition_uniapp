<template>
	<view class="">
		<view class="container" v-if='mode == 0'>
			<scroll-view class="chat-message" scroll-y :scroll-top="scrollTop" ref="scrollView" @scroll="handleScroll">
				<!-- 第一条消息作为提示消息 -->
				<view class="message bot">
					<image class="avatar" src="../../static/avatar/rabot.png" mode=""></image>
					<view class="text">
						<view class="" style="display: flex;">
							<text>请使用下方按钮通过图片显示您的皮肤情况</text>
						</view>
					</view>
				</view>
				<!-- 循环展示图片和结果 -->
				<template v-for="(name, index) in name">
					<view class="message user">
						<view class="text">
							<image :src="imageurl[index]" mode="aspectFit"></image>
						</view>
						<image class="avatar" src="../../static/avatar/user.jpg" mode=""></image>
					</view>
					<view class="message bot">
						<image class="avatar" src="/static/avatar/rabot.png" mode=""></image>
						<view class="text">
							<view class="" style="display: flex;">
								<text>通过您的图片，我推测您的情况为:\n &nbsp;&nbsp;&nbsp;&nbsp;{{name}}
									\n对于这个结果，我们的建议是：\n &nbsp;&nbsp;&nbsp;&nbsp;{{note[index]}}</text>
							</view>
						</view>
					</view>
				</template>
			</scroll-view>
			<!-- 底部工具栏 -->
			<view class="bottom-bar">
				<view class="icon-container">
					<view class="" @tap="showDrawer('showLeft')">
						<image class="icon" src="../../static/ai/dir.png"></image>
					</view>
					<image class="icon" src="../../static/ai/pictures.png" @tap="chooseImage"></image>
					<image class="icon" src="../../static/ai/change.png" @click="refreshPage"></image>
					<!-- <image class="icon" src="../../static/ai/camera.png"  @click="handleSnap"></image> -->
					<!-- 功能选择 -->
					<uni-drawer ref="showLeft" mode="left" :width="150" @change="change($event,'showLeft')">
						<view class="close">
							<button @click="closeDrawer('showLeft')" class='button1'><text
									class="word-btn-white">皮肤科</text></button>
							<button @click="closeDrawer1('showLeft')" class='button1'><text
									class="word-btn-white">脑科</text></button>
						</view>
					</uni-drawer>
					<image class="icon" src="../../static/ai/goBack.png" @tap="goBack"></image>
				</view>
			</view>

		</view>

		<view class="" v-if='mode == 1'>
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

			<!-- 底部工具栏 -->
			<view class="bottom-bar">
				<view class="icon-container">
					<view class="" @tap="showDrawer('showLeft')">
						<image class="icon" src="../../static/ai/dir.png"></image>
					</view>
					<!-- 				<image class="icon" src="../../static/ai/pictures.png" @tap="chooseImage1"></image>
					<image class="icon" src="../../static/ai/camera.png" @tap="camera"></image> -->

					<image class="icon" src="../../static/ai/change.png" @tap="refreshPage"></image>
					<!-- 功能选择 -->
					<uni-drawer ref="showLeft" mode="left" :width="150" @change="change($event,'showLeft')">
						<view class="close">
							<button @click="closeDrawer('showLeft')" class='button1'><text
									class="word-btn-white">皮肤科</text></button>
							<button @click="closeDrawer1('showLeft')" class='button1'><text
									class="word-btn-white">脑科</text></button>
						</view>
					</uni-drawer>
					<image class="icon" src="../../static/ai/goBack.png" @tap="goBack"></image>
				</view>
			</view>
		</view>

	</view>
</template>

<script>
	export default {
		data() {
			return {
				imageurl: [], //图片地址
				name: [], //推测结果
				note: [], //建议

				imagedata: [], // 改为数组，用于存储多个图片URL
				names: [], // 改为数组，用于存储多个图片URL

				userdata: [],
				aidata: [],
				host: '', // 定义 host 变量
				scrollTop: 0, // 用于控制滚动的位置
				isScrollingToBottom: false, // 标记是否正在自动滚动到底部

				showRight: false,
				showLeft: false,
				// 进行模式选择，默认为：0
				mode: 0,
			}
		},
		onShow() {
			// 判断当前页面是否为首页，如果不是首页才隐藏 tabBar
			if (this.$route.path !== "/pages/index/index") {
				uni.hideTabBar();
			}
		},
		created() {
			this.host = getApp().globalData.host; // 在 created 生命周期中设置 host
		},
		mounted() {
		    // 确保代码仅在客户端执行
		        if (typeof window!== 'undefined') {
		          this.refreshPage = this.refreshPage.bind(this);
		        }
		  },
		methods: {
			goBack() {
				// 显示 tabBar
				uni.showTabBar();
				// 返回首页
				uni.switchTab({
					url: "/pages/index/index"
				});
			},
			chooseImage() {
				uni.chooseImage({
					count: 1,
					success: (res) => {
						let tempFilePaths = res.tempFilePaths;
						console.log(tempFilePaths);
						let url = 'http://localhost:8080/media/skin/';
						console.log(url);

						// 上传文件
						uni.uploadFile({
							url: url, // 使用上面定义的 url 变量
							filePath: tempFilePaths[0],
							name: 'file',
							success: (res) => {
								let data = JSON.parse(res.data);
								console.log(data)
								if (data.code === 200) {
									this.imageurl.push(data.imgurl);
									this.name.push(data.name);
									this.note.push(data.notes);

								}
							}
						});
					}
				});
			},
			refreshPage() {
				this.resetData();
			    // 方法一：使用 window.location.reload() 刷新页面
			    // window.location.reload();
			},
			resetData() {
				this.imageurl = [];
				this.name = [];
				this.note = [];
				this.imagedata = [];
				this.names = [];
			    },
			addItem() {
				const newItem = `Item ${this.aidata.length + 1}`;
				this.aidata.push(newItem);

				// 延迟执行以确保 DOM 更新完成
				this.$nextTick(() => {
					// 获取可滚动区域的高度
					const scrollView = this.$refs.scrollView;
					if (scrollView) {
						// 设置滚动到底部
						this.scrollToBottom();
					}
				});
			},

			scrollToBottom() {
				// 获取可滚动区域的高度
				const scrollView = this.$refs.scrollView;
				if (scrollView) {
					// 设置滚动到底部
					this.scrollTop = scrollView.$el.querySelector('.uni-scroll-view').scrollHeight;
					this.isScrollingToBottom = true;
				}
			},

			handleScroll(event) {
				// 如果用户手动滚动，则停止自动滚动
				if (!this.isScrollingToBottom) {
					this.scrollTop = event.detail.scrollTop;
				} else {
					// 滚动到底部后，重置标志
					this.isScrollingToBottom = false;
					// 更新note数组后调用scrollToBottom
					this.$nextTick(() => {
						this.scrollToBottom();
					});
				}
			},
			confirm() {},
			// 打开窗口
			showDrawer(e) {
				this.$refs[e].open()
			},
			// 关闭窗口
			closeDrawer(e) {

				this.mode = 0;
				console.log(this.mode);


				this.$refs[e].close()

			},
			closeDrawer1(e) {
				this.mode = 1;
				console.log(this.mode);
				this.$refs[e].close()
			},
			// 抽屉状态发生变化触发
			change(e, type) {

				console.log((type === 'showLeft' ? '左窗口' : '右窗口') + (e ? '打开' : '关闭'));
				this[type] = e;
			},
			onNavigationBarButtonTap(e) {
				if (this.showLeft) {
					this.$refs.showLeft.close()
				} else {
					this.$refs.showLeft.open()
				}
			},
			// app端拦截返回事件 ，仅app端生效
			onBackPress() {
				if (this.showRight || this.showLeft) {
					this.$refs.showLeft.close()
					this.$refs.showRight.close()
					return true
				}
			},
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
										this.imagedata.push(response.path); //更新图片地址数据
										this.names.push(response.name); //返回类型结果
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


		}
	}
</script>

<style>
	.container {
		display: flex;
		flex-direction: column;
		justify-content: flex-start;
		height: 100vh;
		padding: 20rpx;
		box-sizing: border-box;
		position: relative;
		background-color: #F5F5F5;
	}

	.chat-message {
		width: 100%;
		flex: 1;
		margin-bottom: 150rpx;
		/* 保证内容不会被input-section遮挡 */
		overflow-y: auto;
	}

	.message {
		display: flex;
		align-items: flex-start;
		margin: 20rpx 0;
	}

	.avatar {
		width: 85rpx;
		height: 85rpx;
		border-radius: 5rpx;
		/* margin-right: 20rpx; */
	}

	.avatar2 {
		width: 750rpx;
		border-radius: 5rpx;
		margin-right: 20rpx;
	}

	.user .avatar {
		margin-left: 20rpx;
	}

	.bot .avatar {
		margin-right: 20rpx;
	}

	.message.user .text {
		background-color: #a4ed92;
		padding: 10rpx;
		border-radius: 10rpx;
		color: #000;
		flex: 1;
		margin-left: 80rpx;
		/* 调整左边距 */
	}

	.message.bot .text {
		background-color: #ffffff;
		padding: 10rpx;
		border-radius: 10rpx;
		color: #000;
		flex: 1;
		word-wrap: break-word;
		/* 允许文本换行 */
		margin-right: 80rpx;
		/* 调整右边距 */
	}

	.text {
		display: inline-block;
	}

	.text image {
		width: 100%;
		height: 300rpx;
	}

	.input-section {
		width: 100%;
		max-width: 600px;
		display: flex;
		flex-direction: column;
		align-items: center;
		padding: 10rpx;
		background-color: #fff;
		border-top: 1px solid #e5e5e5;
		position: fixed;
		bottom: 0;
		left: 0;
		right: 0;
		box-sizing: border-box;
		height: 100rpx;
		/* 根据需要调整 */
	}

	.icon-container {
		width: 100%;
		display: flex;
		justify-content: space-around;
	}

	.icon {
		width: 60rpx;
		height: 60rpx;
	}

	/* 底部导航栏样式 */
	.bottom-bar {
		position: fixed;
		/* 固定在页面底部 */
		bottom: 0;
		left: 0;
		right: 0;
		background-color: #fff;
		/* 背景颜色可以根据需要调整 */
		box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.1);
		/* 添加阴影效果 */
		padding: 10px 0;
		/* 上下内边距 */
		display: flex;
		justify-content: center;
		/* 水平居中 */
		align-items: center;
		/* 垂直居中 */
		z-index: 1000;
		/* 确保在其他内容之上 */
	}

	.icon-container {
		display: flex;
		width: 100%;
		justify-content: space-around;
		/* 图标之间等间距分布 */
	}

	.icon {
		width: 40px;
		/* 图标宽度 */
		height: 40px;
		/* 图标高度 */
	}

	.button1 {
		width: 200rpx;
		padding: 0;
		margin-top: 10rpx;
		background-color: #a4ed92;
	}

	.padding1 {
		position: fixed;
		/* 固定在页面底部 */
		bottom: 0;
		left: 0;
		right: 0;
		height: 1000rpx;
	}
</style>
