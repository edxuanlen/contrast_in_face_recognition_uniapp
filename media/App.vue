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
		background-color: #f8f8f8;
	}

	.container {
		padding: 20px;
	}

	button {
		border: none;
	}

	button::after {
		border: none;
	}
</style>
