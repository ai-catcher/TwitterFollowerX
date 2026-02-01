记录我蓝v互关的笔记 会记录一些采集的适合互关的列表

目标一万蓝v互关

来互关 [@ThanksuTrump](https://x.com/ThanksuTrump)

新增关注检测脚本 scraper_v6.py 检测哪些账号未回关 以及分析关注数据
新增批量屏蔽脚本 batch_block_v3.py 批量屏蔽未回关的账号



scraper_v6.py使用方法  
1.(可选)无法直接访问x的电脑 开启tun模式vpn  
2.(可选)安装Python 3.13.2 已安装可以跳过 太新或太旧的版本运行可能故障  
3.(可选)安装运行库已安装的可以跳过 打开cmd 运行 pip install DrissionPage colorama  
4.打开cmd 运行 "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:\yourfolder\"  
把C:\Program Files\Google\Chrome\Application\chrome.exe换成你chrome浏览器位置把C:\yourfolder\换成你新建的一个空文件夹  
5.在打开的浏览器里登录x账号 如果要提高加载速度和节省流量还可以禁止浏览器加载图片
6.(可选)如果要统计xhunt数据的话安装xhunt 建议安装xhunt统计下数据  
7.打开cmd运行脚本python scraper_v6.py  
8.不要直接回车用默认页面 在cmd里输入你的关注页面链接 https://x.com/ThanksuTrump/following 把ThanksuTrump换成你的账号  
9.完毕后手动按ctrl+c停止 如果过程中网页卡住自己动动让他继续滚动 脚本会生成一个csv文件  
10.使用excel进行筛选 将xhunt评分一栏升序排列 是否关注我一栏 过滤选择否  
11.排除掉前面xhunt评分高的kol你就知道哪些人你关注了但他没回关你 接下来选择要一个个联系让回关还是直接取关  
12.有两千人没回我关 看到的请回关 长期不回的一一取关!  

batch_block_v3.py使用方法  
1.(可选)无法直接访问x的电脑 开启tun模式vpn  
2.(可选)安装Python 3.13.2 已安装可以跳过  
太新或太旧的版本运行可能故障  
3.(可选)安装运行库已安装的可以跳过 打开cmd 运行 pip install playwright  
4.打开cmd 运行 "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222  --user-data-dir="C:\yourfolder\" 把C:\Program Files\Google\Chrome\Application\chrome.exe换成你chrome浏览器位置把C:\yourfolder\换成你新建的一个空文件夹  
5.在打开的浏览器里登录x账号  
6.在目录下users.txt里粘贴你要屏蔽的用户列表 一行一个例如  
@user1  
@user2  
7.打开cmd运行脚本python batch_block_v3.py  



