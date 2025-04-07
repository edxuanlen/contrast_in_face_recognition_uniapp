<template>
	<view class="container">
		<form @submit="handleSubmit">
			<!-- 头像上传 -->
			<view class="form-group">
				<text class="label">头像:</text>
				<image :src="avatar" class="avatar" @click="chooseImage"></image>
			</view>

			<!-- 姓名输入 -->
			<view class="form-group">
				<text class="label">姓名:</text>
				<input type="text" v-model="name" placeholder="请输入姓名" />
			</view>

			<!-- 性别选择 -->
			<view class="form-group" style="display: flex;">
				<text class="label">性别:</text>
				<radio-group @change="radioChange">
					<label style="margin-left: 150rpx;">
						<radio value="男" :checked="gender==='男'" />男
					</label>
					<label style="margin-left: 50rpx;">
						<radio value="女" :checked="gender==='女'" />女
					</label>
				</radio-group>
			</view>

			<!-- 年龄输入 -->
			<view class="form-group">
				<text class="label">年龄:</text>
				<input type="number" v-model="age" placeholder="请输入年龄" />
			</view>


			<!-- 			<view class="form-group">
				<text class="label">病种</text>
				<picker mode="selector" :range="diseases" @change="bindDiseaseChange">
					<view>{{ disease || '请选择病种' }}</view>
				</picker>
			</view>

			
			<view class="form-group">
				<text class="label">主治医生</text>
				<picker mode="selector" :range="doctors" @change="bindDoctorChange">
					<view>{{ doctor || '请选择主治医生' }}</view>
				</picker>
			</view> -->

			<!-- 
			<view class="form-group">
				<text class="label">时间</text>
				<picker mode="date" @change="bindDateChange">
					<view>{{ date || '请选择日期' }}</view>
				</picker>
			</view> -->

			<button form-type="submit" @click="login1" >提交</button>
		</form>
	</view>
</template>

<script>
	export default {
		data() {
			return {
				account: '',
				password: '',
				avatar: '',
				name: '',
				gender: '',
				age: '',
				img_name:'',
				host: '',

				// disease: '',
				// diseases: ['皮肤病', '脑肿瘤', '心脏病'],
				// doctor: '',
				// doctors: ['李医生', '王医生', '张医生'],
				// date: ''

			}
		},
		created() {
			this.host = getApp().globalData.host; // 在 created 生命周期中设置 host
		},
		onShow() {
			if(getApp().globalData.userInfo==null){
				uni.showModal({
					title: '提示',
					content: '请先登录',
					showCancel: false
				});
			}
			else{
				this.userInfo = getApp().globalData.userInfo;
				// console.log(getApp().globalData.userInfo)
				// console.log(this.userInfo);
				this.account = this.userInfo.account;
				this.password = this.userInfo.password;
			}
			
			


		},
	
		methods: {
			// 发送图片
			chooseImage() {
				uni.chooseImage({
					count: 1,
					success: (res) => {
						let tempFilePaths = res.tempFilePaths;
						// console.log(tempFilePaths);
						let url = this.host+'/media/imgurl/';
						
						this.avatar=tempFilePaths[0]
			
						// 上传文件
						uni.uploadFile({
							url: url, // 使用上面定义的 url 变量
							filePath: tempFilePaths[0],
							name: 'file',
							success: (res) => {
								let data = JSON.parse(res.data);
								
								if (data.code === 200) {
									
									console.log(data);
									this.img_name=data.msg;
									// console.log(data.msg);
								}
							}
						});
					}
				});
			},
			radioChange(e) {
				this.gender = e.detail.value;
			},
			// bindDiseaseChange(e) {
			// 	this.disease = this.diseases[e.detail.value];
			// },
			// bindDoctorChange(e) {
			// 	this.doctor = this.doctors[e.detail.value];
			// },
			// bindDateChange(e) {
			// 	this.date = e.detail.value;
			// },
			
			// 发送文字
			handleSubmit(e) {
				console.log('Form Submitted:', this.$data);
				console.log(this.avatar)
				// // 在这里处理表单提交逻辑
				
				uni.request({
					url:this.host+'/media/realname/',
					method: 'POST',
					header: {
						'Content-Type': 'application/json' // 确保 Content-Type 为 application/json
					},
					data: JSON.stringify(this.$data),
					imgurl:this.img_name,
					// data: this.$data,
					// data = JSON.parse(this.$data),
					success: (res) => {
						console.log(res.data);
						}
				});
			},
				
			login1(){
				uni.navigateBack({
					delta:1
				})
			}
		}
	}
</script>

<style>
	.container {
		padding: 20px;
	}

	.form-group {
		margin-bottom: 20px;
		/* display: flex; */
	}

	.label {
		display: block;
		font-weight: bold;
		margin-bottom: 5px;

	}

	input,
	picker {
		width: 90%;
		padding: 10px;
		border: 1px solid #ccc;
		border-radius: 4px;
	}

	.avatar {


		height: 300rpx;
		width: 300rpx;
		border-radius: 50%;
		border: 1px solid #000000;
		justify-content: center;
		align-items: center;
		margin-left: 200rpx;
	}
</style>