<template>
	<view>
		<uni-file-picker limit ="9" @select="uploadImage"></uni-file-picker>
		<!-- <uni-file-picker limit="1" @select="uploadImg"></uni-file-picker> -->
	</view>
	<uni-section title="安全检测" type="line">
		<view class="example-body">
			<uni-file-picker limit ="9" @select="uploadImage"></uni-file-picker>
		</view>
	</uni-section>
</template>

<script>
	export default {
		data() {
			return {

			}
		},
		methods: {
			uploadImage(image) {
				console.log(image.tempFilePaths)
				uni.uploadFile({
					url: "http://127.0.0.1:8000/ai/uploadImg/",
					filePath: image.tempFilePaths[0],
					name: 'img',// name用于后端接收处
					success: (res) => {
						console.log(res.data)
					}
				});
			}	
		}
	}
</script>
<style>
	.example-body {
		padding: 10px;
		padding-top: 0;
	}

	.custom-image-box {
		/* #ifndef APP-NVUE */
		display: flex;
		/* #endif */
		flex-direction: row;
		justify-content: space-between;
		align-items: center;
	}

	.text {
		font-size: 14px;
		color: #333;
	}
</style>