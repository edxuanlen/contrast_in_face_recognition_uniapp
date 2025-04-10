<script>
	export default {
		onLaunch: function() {
			console.log('App Launch')
			// 检查登录状态
			const token = uni.getStorageSync('token')
			if (!token) {
				uni.redirectTo({
					url: '/pages/login/login'
				})
			}
		},
		onShow: function() {
			console.log('App Show')
		},
		onHide: function() {
			console.log('App Hide')
		},
		globalData:{
			host:'http://localhost:8080',
		}
	}
</script>

<style>
	/*每个页面公共css */
	page {
		font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
		color: #333;
		font-size: 14px;
		line-height: 1.5;
		background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
		min-height: 100vh;
	}

	.container {
		padding: 20px;
		background-color: rgba(255, 255, 255, 0.8);
		border-radius: 12px;
		box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
		margin: 15px;
		background: linear-gradient(to right, #4facfe 0%, #00f2fe 100%);
	}

	button {
		border: none;
		background: linear-gradient(to right, #4facfe 0%, #00f2fe 100%);
		color: white;
		border-radius: 8px;
		padding: 10px 15px;
		font-weight: 500;
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
		transition: all 0.3s ease;
	}

	button:active {
		transform: translateY(2px);
		box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1);
	}

	button::after {
		border: none;
	}

	.title {
		font-size: 20px;
		font-weight: bold;
		margin-bottom: 20px;
		color: #2c3e50;
		text-align: center;
		padding: 10px 0;
		border-bottom: 1px solid rgba(0, 0, 0, 0.1);
	}
</style>
