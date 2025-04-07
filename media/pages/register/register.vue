<template>
	<view class="container">
		<view class="register-form">
			<view class="title">注册账号</view>

			<input type="text" v-model="registerData.username" placeholder="用户名" class="input-field" />
			<input type="password" v-model="registerData.password" placeholder="密码" class="input-field" />
			<input type="password" v-model="confirmPassword" placeholder="确认密码" class="input-field" />
			<input type="text" v-model="registerData.email" placeholder="邮箱" class="input-field" />

			<view class="captcha-container">
				<input type="text" v-model="inputCaptcha" placeholder="验证码" class="captcha-input" />
				<view class="captcha-box" @click="refreshCaptcha">
					<text class="captcha-text">{{captcha}}</text>
				</view>
			</view>

			<button @click="handleRegister" class="register-button">注册</button>
			<view class="login-link">
				已有账号? <navigator url="/pages/login/login" class="link">登录</navigator>
			</view>
		</view>
	</view>
</template>

<script>
	export default {
		data() {
			return {
				registerData: {
					username: '',
					password: '',
					email: ''
				},
				confirmPassword: '',
				captcha: '',
				inputCaptcha: '',
				host: ''
			}
		},
		created() {
			this.host = getApp().globalData.host;
			this.refreshCaptcha();
		},
		methods: {
			generateCaptcha(length) {
				const characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
				let result = '';
				for (let i = 0; i < length; i++) {
					result += characters.charAt(Math.floor(Math.random() * characters.length));
				}
				return result;
			},

			refreshCaptcha() {
				this.captcha = this.generateCaptcha(4);
				this.inputCaptcha = '';
			},

			handleRegister() {
				// 验证表单
				if (!this.registerData.username || !this.registerData.password || !this.confirmPassword || !this.registerData.email) {
					uni.showToast({
						title: '请填写所有字段',
						icon: 'none'
					});
					return;
				}

				if (this.registerData.password !== this.confirmPassword) {
					uni.showToast({
						title: '两次密码输入不一致',
						icon: 'none'
					});
					return;
				}

				// 验证邮箱格式
				const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
				if (!emailRegex.test(this.registerData.email)) {
					uni.showToast({
						title: '请输入有效的邮箱地址',
						icon: 'none'
					});
					return;
				}

				// 验证验证码
				if (this.inputCaptcha.toLowerCase() !== this.captcha.toLowerCase()) {
					uni.showToast({
						title: '验证码错误',
						icon: 'none'
					});
					this.refreshCaptcha();
					return;
				}

				// 提交注册
				uni.showLoading({
					title: '注册中...'
				});

				uni.request({
					url: this.host + '/api/register/',
					data: this.registerData,
					method: 'POST',
					success: (res) => {
						uni.hideLoading();
						if (res.data.code === 200) {
							uni.showToast({
								title: '注册成功',
								icon: 'success'
							});

							setTimeout(() => {
								uni.navigateTo({
									url: '/pages/login/login'
								});
							}, 1500);
						} else {
							uni.showToast({
								title: res.data.message || '注册失败',
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
		display: flex;
		justify-content: center;
		align-items: center;
		min-height: 100vh;
		background-color: #f8f8f8;
		padding: 20px 0;
	}

	.register-form {
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
		width: 100%;
		height: 45px;
		border: 1px solid #ddd;
		border-radius: 5px;
		margin-bottom: 15px;
		padding: 0 15px;
		font-size: 16px;
	}

	.captcha-container {
		display: flex;
		margin-bottom: 15px;
	}

	.captcha-input {
		flex: 1;
		height: 45px;
		border: 1px solid #ddd;
		border-radius: 5px;
		padding: 0 15px;
		font-size: 16px;
		margin-right: 10px;
	}

	.captcha-box {
		width: 100px;
		height: 45px;
		background-color: #f0f0f0;
		border-radius: 5px;
		display: flex;
		justify-content: center;
		align-items: center;
	}

	.captcha-text {
		font-family: 'Courier New', monospace;
		font-size: 18px;
		font-weight: bold;
		letter-spacing: 2px;
	}

	.register-button {
		width: 100%;
		height: 45px;
		background-color: #007aff;
		color: white;
		border-radius: 5px;
		font-size: 16px;
		margin-top: 10px;
	}

	.login-link {
		text-align: center;
		margin-top: 20px;
		font-size: 14px;
	}

	.link {
		color: #007aff;
		display: inline;
	}
</style>
