<template>
	<view class="container">
		<view class="login-form">
			<view class="title">人脸识别系统</view>
			<input type="text" v-model="loginData.username" placeholder="用户名" class="input-field" />
			<input type="password" v-model="loginData.password" placeholder="密码" class="input-field" />
			<button @click="handleLogin" class="login-button">登录</button>
			<view class="extra-links">
				<navigator url="#" class="link">忘记密码?</navigator>
				<navigator url="/pages/register/register" class="link">注册账号</navigator>
			</view>
		</view>
	</view>
</template>

<script>
	export default {
		data() {
			return {
				loginData: {
					username: '',
					password: ''
				},
				host: ''
			}
		},
		created() {
			this.host = getApp().globalData.host;
		},
		onHide() {
			if ((this.loginData.username != null) && (this.loginData.password != null)) {
				// getApp().globalData.userInfo = {
				// 	account: this.loginData.username,
				// 	password: this.loginData.password
				// }
			}

		},
		methods: {
			handleLogin() {
				if (!this.loginData.username || !this.loginData.password) {
					uni.showToast({
						title: '请输入用户名和密码',
						icon: 'none'
					});
					return;
				}

				uni.showLoading({
					title: '登录中...'
				});

				uni.request({
					url: this.host + '/api/login/',
					data: this.loginData,
					method: 'POST',
					success: (res) => {
						uni.hideLoading();
						if (res.data.code === 200) {
							// 保存用户信息和token
							uni.setStorageSync('userInfo', res.data.user);
							uni.setStorageSync('token', res.data.token);

							uni.showToast({
								title: '登录成功',
								icon: 'success'
							});

							// 跳转到首页
							uni.switchTab({
								url: '/pages/index/index'
							});
						} else {
							uni.showToast({
								title: res.data.message || '登录失败',
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

<style scoped>
	.container {
		display: flex;
		justify-content: center;
		align-items: center;
		height: 80vh;
		background-color: linear-gradient(to right, #4facfe 0%, #00f2fe 100%);
	}

	.login-form {
		width: 80%;
		padding: 30px;
		background-color: white;
		border-radius: 10px;
		box-shadow: 0 2px 10px rgba(0,0,0,0.1);
	}

	.title {
		font-size: 24px;
		font-weight: bold;
		text-align: center;
		margin-bottom: 30px;
	}

	.input-field {
		width: calc(100% - 15px); /* Adjusted width to account for padding */
		height: 45px;
		border: 1px solid #ddd;
		border-radius: 5px;
		margin-bottom: 15px;
		padding: 0 15px;
		font-size: 16px;
		box-sizing: border-box; /* Ensures padding is included in the total width */
	}

	.login-button {
		width: 100%;
		height: 45px;
		background-color: #007aff;
		color: white;
		border-radius: 5px;
		font-size: 16px;
		margin-top: 10px;
	}

	.extra-links {
		display: flex;
		justify-content: space-between;
		margin-top: 20px;
	}

	.link {
		color: #007aff;
		font-size: 14px;
	}
</style>
