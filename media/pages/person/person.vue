<template>
	<view class="container">
		<!-- 用户信息头部 -->
		<view class="user-info">
			<view class="avatar0" @click="navigateToLogin">
				<image :src="avatarUrl" class="avatar"></image>
				<text class="user-name" v-show="!isLoggedIn">未登录</text>
			</view>

			<view class="container2" v-if='mode==0'>
				<button class="real-name1" @tap='real_name'>去实名</button>
			</view>

			<view class="real-name2" v-if='mode==1'>
				<view class="info" style="margin-left: 30rpx;width: 35%;">
					<text class="user">姓名:</text>
					<text class="user1">{{ username }}</text>

				</view>
				<view class="info" style="margin-left: 10rpx;width: 25%;">
					<text class="user">性别:</text>
					<text class="user1">{{ usergender }}</text>

				</view>
				<view class="info" style="margin-left: 40rpx;width: 25%;">
					<text class="user">年龄:</text>
					<text class="user1">{{ userage }}</text>

				</view>
			</view>


		</view>

		<!-- 快捷功能区 -->
		<view class="quick-actions" @longpress="clear">
			<view url="/pages/case/case" class="action-item" @click="case1">
				<image src="/static/person/case.png" class="icon"></image>
				<view class="label"><text class="">查看记录</text></view>

			</view>
			<view url="/pages/appointments/index" class="action-item">
				<image src="/static/person/register.png" class="icon"></image>
				<text class="label">预约挂号</text>
			</view>

		</view>
		<view class="quick-actions">

			<view url="/pages/messages/index" class="action-item">
				<image src="/static/person/infomation.png" class="icon"></image>
				<text class="label">消息通知</text>
			</view>
			<view url="/pages/settings/index" class="action-item">
				<image src="/static/person/setting.png" class="icon"></image>
				<text class="label">设置</text>
			</view>
		</view>
	</view>
</template>

<script>
	export default {
		data() {
			return {
				isLoggedIn: false, //判断是否已登录
				avatarUrl: '../../static/person.png', // 用户头像地址
				username: '', // 用户名
				usergender: '',
				userage: '',
				mode: 0,
				user: {
					account: '',
					password: ''
				},
				host: '',

			}
		},
		created() {
			this.host = getApp().globalData.host; // 在 created 生命周期中设置 host
		},
		onShow() {
			if (getApp().globalData.userInfo != null) {

				this.userInfo = getApp().globalData.userInfo;
				// console.log(getApp().globalData.userInfo)
				console.log(this.userInfo);
				this.user.account = this.userInfo.account;
				this.user.password = this.userInfo.password;
				this.isLoggedIn = true


				// this.user.account = '255';
				// this.user.password = '123';
				let data = this.user;
				console.log(data);
				uni.request({
					url: this.host+'/media/getinfo/',
					data: data,
					method: "POST",
					header: {
						'Content-Type': 'application/json' // 确保 Content-Type 为 application/json
					},

					success: (res) => {
						// console.log(res.data);
						// console.log(res.data.data[0].name);
						if (res.data.data[0]) {
							console.log(res.data.data[0].name);
							this.username = res.data.data[0].name;
							this.usergender = res.data.data[0].gender;
							this.userage = res.data.data[0].age;
							this.avatarUrl = res.data.data[0].avatar;
						}
						if (this.username != '') {
							this.mode = 1;

						}
						// console.log("ok")
					},
				});
			}
		},
		methods: {
			navigateToLogin() {
				uni.navigateTo({
					url: '/pages/login/login' // 跳转到登录页面
				});
			},
			case1() {
				uni.navigateTo({
					url: '/pages/case/case' // 跳转到病例页面
				});
			},
			real_name() {
				uni.navigateTo({
					url: '/pages/realname/realname'
				});
			},
			clear() {
				uni.request({
					url: this.host+'/media/tmourdata/', //真实接口地址。
					success: (res) => {
						console.log(res.data);
						uni.showModal({
							title: '危险操作',
							content: '是否确定全部删除？',
							success: function(res) {
								if (res.confirm) {
									console.log('用户点击确定');
									uni.request({
										url: 'http://localhost:8080/media/del/', //真实接口地址。
										// data: {
										// 	id: id
										// },

										success: (res) => {
											console.log(res.data);
											// 直接在客户端完成数据更新
											// _this.articles = _this.articles.filter(item => item.id !== id);
											uni.showToast({
												title: '清除成功',
												icon: 'success',
												duration: 1500,
												mask: true,
											});

										}
									});

								} else if (res.cancel) {
									console.log('用户点击取消');
								}
							}
						});
					}
				});
			}
		}
	}
</script>

<style scoped>
	.container {
		/* display: flex; */
		flex-direction: column;
		align-items: center;
		/* padding: 20px; */
		/* background-color: #f5f5f5; */
		/* background-color: #daffd7;? */
	}

	.user-info {
		width: 90%;


		height: 30vh;
		align-items: center;
		padding: 20px;
		background-color: #ffffff;
		border-radius: 10px;
		box-shadow: 0 4px 8px rgba(0, 0, 0, .1);
		margin-bottom: 20px;
	}

	.avatar {
		width: 240rpx;
		height: 240rpx;
		border-radius: 50%;
		margin-left: 30rpx;
		margin-right: 15rpx;
	}

	.info {
		width: 33%;
		/* display: flex; */
		/* flex-direction: column; */
		/* 		margin-left: 10rpx;
		margin-right: 10rpx; */
		/* display: line-item; */
		/* background-color: aquamarine; */
		font-size: 36rpx;
		padding: 0;

	}

	.user {
		/* font-size: 40rpx; */
		font-weight: bold;
		color: #333;
	}

	.user1 {
		/* font-size: 30rpx; */
		font-weight: bold;
		color: #eb0fff;
		margin-left: 20rpx;
	}

	.role {
		font-size: 16px;
		color: #777;
	}

	.quick-actions {
		width: 100%;
		display: flex;
		justify-content: space-around;
		/* flex-wrap: wrap; */
		/* background-color: aquamarine; */
		/* background-color: #daffd7; */
	}

	.action-item {

		width: 40%;

		/* flex-direction: column; */

		padding: 20rpx;
		background-color: white;
		border-radius: 40rpx;
		box-shadow: 0 4px 8px rgba(0, 0, 0, .1);
		margin-bottom: 20px;

		align-items: right;
		justify-items: center;
		/* font-size: 0rpx; */
		display: flex;
		background-color: #dbffd3;

	}

	.icon {
		width: 120rpx;
		height: 120rpx;
		margin-bottom: 10rpx;
	}

	.label {
		font-size: 40rpx;
		color: #333;

		justify-content: center;
		margin-left: 1rpx;
		margin-bottom: 0;
		display: flex;
		flex-direction: column;
		justify-content: flex;
		align-items: flex-end;

	}

	.avatar0 {
		display: flex;
		flex-direction: column;
		/* 子元素垂直排列 */
		align-items: center;
		/* 子元素水平居中 */
	}

	.user-name {
		/* margin-left: 23rpx; */
		align-items: center;
		justify-items: center;
	}

	.real-name1 {
		width: 200rpx;
		border-radius: 25rpx;
		color: #3c3c3c;
		font-size: 35rpx;



		align-items: center;
		justify-items: center;
		background-color: #e2e2e2;
		box-shadow: 0 4px 8px rgba(0, 0, 0, .1);
	}

	.real-name2 {

		/* margin: 0;
		padding: 0; */
		width: 100%;
		height: 10vh;

		/* align-items: center; */
		/* padding: 20px; */
		/* background-color: yellow; */
		/* border-radius: 10px; */
		/* box-shadow: 0 4px 8px rgba(0, 0, 0, .1); */
		/* margin-bottom: 20px; */
		display: flex;
		align-items: center;
		justify-items: center;
		margin-top: 30rpx;
		;
	}

	.container2 {
		/* width: 500rpx; */
		/* background-color: #eb0fff; */
		/* display: flex; */
		/* 		align-items: center;
		justify-items: center; */
		margin-top: 30rpx;
	}
</style>
