<template>
    <view class="page">

        <view class="article" v-for="(item, index) in articles" @mousedown="delLog(item.id)">
            <image class="thumbnail" :src="item.imgpath" mode="aspectFill"></image>
            <view class="content">
                <view class="title">
                    {{ aitype[item.aitype] }} | {{item.cls_name}}

                </view>
                <view class="summary">时间：{{ item.result_time }}</view>
            </view>
        </view>
    </view>

    <view class="bt">
        <button class="bb" @click="toggleRoute">切&nbsp;&nbsp;换</button>
    </view>
</template>

<script>
	let coco_classes_chinese = [
		"人", "自行车", "汽车", "摩托车", "飞机", "公交车", "火车", "卡车", "船",
		"红绿灯", "消防栓", "停止标志", "停车收费表", "长椅",
		"鸟", "猫", "狗", "马", "羊", "牛", "大象", "熊", "斑马", "长颈鹿",
		"背包", "雨伞", "手提包", "领带", "手提箱",
		"飞盘", "滑雪板", "单板滑雪", "运动球", "风筝", "棒球棒", "棒球手套", "滑板",
		"冲浪板", "网球拍", "瓶子", "酒杯", "杯子", "叉子", "刀", "勺子", "碗",
		"香蕉", "苹果", "三明治", "橙子", "西兰花", "胡萝卜", "热狗", "披萨", "甜甜圈", "蛋糕",
		"椅子", "沙发", "盆栽", "床", "餐桌", "马桶", "电视", "笔记本电脑", "鼠标", "遥控器",
		"键盘", "手机", "微波炉", "烤箱", "烤面包机", "水槽", "冰箱", "书", "时钟",
		"花瓶", "剪刀", "泰迪熊", "吹风机", "牙刷"
	]
	export default {
		data() {
			return {
				currentRouteIndex: 0,
				routes: [
					'http://localhost:8080/media/skindata/',
					'http://localhost:8080/media/tmourdata/'
				],
				// aitype: ['默认', '图像分类', '目标检测', '生成式GAN'],
				aitype: ['默认', '皮肤病分类', '肿瘤检测', '生成式GAN'],
				lablename: "飞机、汽车、鸟类、猫、鹿、狗、青蛙、马、船、卡车".split("、"),
				articles: [],
				cls: coco_classes_chinese,
				mode: 0
			};
		},
		onShow() {
			let _this = this // this提前缓存
			console.log('去服务器获取日志信息......')
			uni.request({
				url: 'http://localhost:8080/media/skindata/', //真实接口地址。
				success: (res) => {
					console.log(res.data);
					_this.articles = res.data.data
					this.articles = res.data.obj
				}
			});
		},
		methods: {
			toggleRoute() {
				let _this = this
				const url = this.routes[this.currentRouteIndex];
				uni.request({
					url: url,
					method: 'GET',
					success: (res) => {
						console.log(res.data);
						_this.articles = res.data.data
						this.articles = res.data.obj
					},
					fail: (err) => {
						console.error(err);
						uni.showToast({
							title: '请求失败',
							icon: 'none'
						});
					}
				});

				// 切换到下一个路由
				this.currentRouteIndex = (this.currentRouteIndex + 1) % this.routes.length;
			},
			delLog(id) {
				console.log(id)
				console.log('长按事件......', id)
				let _this = this
				uni.showModal({
					title: '危险操作',
					content: '是否确定删除？',
					success: function(res) {
						if (res.confirm) {
							console.log('用户点击确定');
							uni.request({
								url: 'http://localhost:8080/media/skindel/', //真实接口地址。
								data: {
									id: id
								},

								success: (res) => {
									console.log(res.data);
									// 直接在客户端完成数据更新
									_this.articles = _this.articles.filter(item => item.id !== id);
									uni.showToast({
										title: '删除成功',
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
		},

		handleBackClick() {
			//返回上一个页面
			uni.navigateBack({
				delta: 1 // 返回的页面数，1表示返回上一页

			});

		}
	};
</script>

<style>
	.thumbnail {
		width: 150rpx;
		height: 150rpx;
	}

	.article {
		width: 95%;
		display: flex;
		border-radius: 10rpx;
		margin-bottom: 10rpx;
		justify-items: center;
		align-items: center;
		margin-left: 10rpx;
		margin-left: 20rpx;
		margin-top: 1rpx;
		box-shadow: 2px 2px 4px 4px rgba(0, 0, 0, .1);
	}

	.content {
		margin-left: 20rpx;
	}

	.bt {
		background-color: #ffffff;
		height: 75rpx;
		display: flex;
		justify-content: center;
		align-items: center;
		position: fixed;
		bottom: 0;
		left: 0;
		right: 0;
		z-index: 999;
		border-top: 1px solid #eaeaea;
		/* 添加顶部边框 */
	}

	.bb {
		background-color: #aa55ff;
		color: #ffffff;
		border-radius: 15rpx;
		padding:5rpx;
		font-size: 30rpx;
		border: none;
	}

	.nav {
		/* position:fixed; */
		/* 		z-index: 1000;
		width: 100%;
		margin-top:0 ;
		padding-top: 0;
		border-radius: 0; */
	}
</style>
