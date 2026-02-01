import time
import re
import math
import random
from playwright.sync_api import sync_playwright

class 拟人鼠标操作:
    """
    模拟真实人类鼠标操作
    特性：
    1. 贝塞尔曲线轨迹
    2. 菲茨定律速度变化
    3. 随机抖动
    4. 目标内随机偏移
    """
    def __init__(self, 页面对象):
        self.页面 = 页面对象

    def _缓动函数(self, 时间百分比):
        """Ease-out 效果：接近目标时减速"""
        return 时间百分比 * (2 - 时间百分比)

    def _计算贝塞尔点(self, 时间, 起点, 控制点, 终点):
        """计算二次贝塞尔曲线上的坐标点"""
        横坐标 = (1 - 时间) ** 2 * 起点[0] + 2 * (1 - 时间) * 时间 * 控制点[0] + 时间 ** 2 * 终点[0]
        纵坐标 = (1 - 时间) ** 2 * 起点[1] + 2 * (1 - 时间) * 时间 * 控制点[1] + 时间 ** 2 * 终点[1]
        return (横坐标, 纵坐标)

    def 移动到(self, 目标横坐标, 目标纵坐标):
        """模拟人类轨迹移动鼠标到指定位置"""
        # 随机生成一个假想起点 (模拟手从别处移过来)
        起始横坐标 = 目标横坐标 + random.choice([-1, 1]) * random.randint(200, 500)
        起始纵坐标 = 目标纵坐标 + random.choice([-1, 1]) * random.randint(200, 500)
        
        # 限制在常见的屏幕范围内
        起始横坐标 = max(0, min(起始横坐标, 1920))
        起始纵坐标 = max(0, min(起始纵坐标, 1080))
        
        self.页面.mouse.move(起始横坐标, 起始纵坐标)
        
        # 生成中间控制点用于拉扯曲线
        控制横坐标 = (起始横坐标 + 目标横坐标) / 2 + random.randint(-100, 100)
        控制纵坐标 = (起始纵坐标 + 目标纵坐标) / 2 + random.randint(-100, 100)
        
        # 计算路径点
        步数 = random.randint(20, 40)
        路径 = []
        for 索引 in range(步数 + 1):
            时间比 = 索引 / 步数
            平滑时间 = self._缓动函数(时间比)
            现横, 现纵 = self._计算贝塞尔点(平滑时间, (起始横坐标, 起始纵坐标), (控制横坐标, 控制纵坐标), (目标横坐标, 目标纵坐标))
            
            # 越接近目标，抖动越小
            抖动量 = 2 * (1 - 时间比)
            现横 += random.uniform(-抖动量, 抖动量)
            现纵 += random.uniform(-抖动量, 抖动量)
            路径.append((现横, 现纵))
            
        # 执行移动指令
        for 点 in 路径:
            self.页面.mouse.move(点[0], 点[1])
            time.sleep(random.uniform(0.001, 0.003))

    def 点击元素(self, 元素定位器):
        """定位元素并执行拟人点击"""
        坐标盒子 = 元素定位器.bounding_box()
        if not 坐标盒子:
            print("[鼠标驱动] 警告：无法获取元素坐标，执行默认点击")
            元素定位器.click()
            return

        # 在元素范围内随机选一个点，避免点击正中心
        安全边距 = 0.1
        随机横 = 坐标盒子['x'] + random.uniform(坐标盒子['width'] * 安全边距, 坐标盒子['width'] * (1 - 安全边距))
        随机纵 = 坐标盒子['y'] + random.uniform(坐标盒子['height'] * 安全边距, 坐标盒子['height'] * (1 - 安全边距))
        
        self.移动到(随机横, 随机纵)
        
        # 模拟点击动作的微小延迟
        time.sleep(random.uniform(0.05, 0.12))
        self.页面.mouse.down()
        time.sleep(random.uniform(0.06, 0.15))
        self.页面.mouse.up()

    def 模拟漫游(self, 最短时常=10, 最长时常=20):
        """在页面上执行随机操作，模拟人类浏览"""
        print(f"[拟人行为] 开始随机漫游 ({最短时常}-{最长时常}秒)...")
        截止时间 = time.time() + random.uniform(最短时常, 最长时常)
        
        while time.time() < 截止时间:
            行为 = random.choice(['滑动', '滑轮', '发呆'])
            
            if 行为 == '滑动':
                视口 = self.页面.viewport_size or {'width': 1280, 'height': 800}
                随机横 = random.randint(0, 视口['width'])
                随机纵 = random.randint(0, 视口['height'])
                self.移动到(随机横, 随机纵)
                time.sleep(random.uniform(0.5, 1.2))
                
            elif 行为 == '滑轮':
                滚动量 = random.randint(200, 600)
                self.页面.mouse.wheel(0, 滚动量)
                time.sleep(random.uniform(0.8, 1.5))
                
            elif 行为 == '发呆':
                time.sleep(random.uniform(1.0, 2.5))

def 执行主逻辑():
    """程序入口函数"""
    print("==================================================")
    print("         X 批量斩杀/检测工具 (全中文版)           ")
    print("==================================================")
    
    # 获取用户设置的随机延迟范围
    输入最小 = input("[设置] 请输入随机等待的最小秒数 (默认 3 数量中等45 数量大建议300过风控): ")
    try:
        最小延迟 = float(输入最小) if 输入最小.strip() else 3.0
    except ValueError:
        print("[提示] 输入无效，使用默认值 3 秒")
        最小延迟 = 3.0

    输入最大 = input("[设置] 请输入随机等待的最大秒数 (默认 10 数量中等75 数量大建议600过风控): ")
    try:
        最大延迟 = float(输入最大) if 输入最大.strip() else 10.0
    except ValueError:
        print("[提示] 输入无效，使用默认值 10 秒")
        最大延迟 = 10.0
    
    if 最小延迟 > 最大延迟:
        print("[警告] 最小延迟大于最大延迟，已自动对调位置")
        最小延迟, 最大延迟 = 最大延迟, 最小延迟

    # 加载数据
    try:
        with open('users.txt', 'r', encoding='utf-8-sig') as 文件:
            # 去除 @ 符号并清理空白
            待处理用户 = [行.strip().lstrip('@') for 行 in 文件 if 行.strip()]
    except FileNotFoundError:
        print("[错误] 未找到 users.txt 文件，请在程序目录下创建。")
        return

    print(f"[信息] 成功加载 {len(待处理用户)} 个待处理账户。")

    # 启动 Playwright 并连接浏览器
    try:
        with sync_playwright() as 播放器:
            print("[网络] 正在尝试连接本地已开启的 Chrome 浏览器 (端口 9222)...")
            try:
                浏览器实例 = 播放器.chromium.connect_over_cdp("http://localhost:9222")
            except Exception as 错误:
                print(f"[失败] 无法连接浏览器: {错误}")
                print("[提示] 请确保 Chrome 使用该命令启动: chrome.exe --remote-debugging-port=9222")
                return

            浏览器上下文 = 浏览器实例.contexts[0]
            页面对象 = 浏览器上下文.new_page()
            拟人驱动 = 拟人鼠标操作(页面对象)
            
            print("[准备] 连接成功，开始执行流程...")

            for 账户名 in 待处理用户:
                print(f"--------------------------------------------------")
                print(f"[当前账户] @{账户名}")
                
                访问地址 = f"https://x.com/{账户名}"
                已成功访问 = False
                
                # 尝试访问逻辑
                for 尝试次数 in range(1, 4):
                    print(f"[网络] 正在进行第 {尝试次数} 次页面跳转...")
                    try:
                        页面对象.goto(访问地址)
                        页面对象.wait_for_load_state("domcontentloaded")
                        # 增加随机停顿，等待渲染
                        time.sleep(random.uniform(3, 5))
                        已成功访问 = True
                        break
                    except Exception as 访问错误:
                        print(f"[警告] 访问出错: {访问错误}，准备重试...")
                        time.sleep(2)

                if not 已成功访问:
                    print(f"[失败] 无法加载 @{账户名} 的页面，跳过。")
                    continue

                # --- 状态检测逻辑 ---
                
                # 1. 账号异常检测
                网页标题 = 页面对象.title()
                if any(关键词 in 网页标题 for 关键词 in ["Account suspended", "Page not found", "此账号已被冻结"]):
                    print(f"[异常] 账号状态无效 (标题显示已冻结或不存在)，跳过。")
                    continue

                # 2. 深度检测是否关注了我 (用户核心需求)
                print(f"[扫描] 正在检测对方是否已关注我...")
                关注我标志 = 页面对象.locator('[data-testid="userFollowIndicator"]')
                
                对方关注我吗 = False
                if 关注我标志.count() > 0:
                    文本内容 = 关注我标志.first.inner_text()
                    if "Follows you" in 文本内容:
                        print(f"【验证结果】对方 [已关注] 我 (检测到 'Follows you')")
                        对方关注我吗 = True
                    else:
                        print(f"【验证结果】对方 [未关注] 我 (标志位文本不匹配: {文本内容})")
                else:
                    print(f"【验证结果】对方 [未关注] 我 (未发现 'Follows you' 标志)")

                # 3. 页面关注按钮状态检测
                try:
                    已关注按钮 = 页面对象.locator('button', has_text=re.compile(r"^Following$"))
                    关注按钮 = 页面对象.locator('button', has_text=re.compile(r"^Follow$"))
                    
                    if 已关注按钮.count() > 0 and 已关注按钮.first.is_visible():
                        print(f"[状态] 我目前：已关注该用户")
                    elif 关注按钮.count() > 0 and 关注按钮.first.is_visible():
                        print(f"[状态] 我目前：未关注该用户")
                    else:
                        print(f"[疑问] 无法识别我的关注状态 (可能按钮尚未加载或结构变化)")
                except Exception as 状态错误:
                    print(f"[警告] 识别关注状态时发生错误: {状态错误}")

                # --- 屏蔽/后续操作逻辑 ---
                if 对方关注我吗:
                    print(f"[跳过] 对方已关注我，不执行斩杀操作。")
                else:
                    print(f"[操作] 对方未关注我，准备执行斩杀流程...")
                    try:
                        # 1. 点击“更多”按钮 (通常是三个点，data-testid="userActions")
                        更多按钮 = 页面对象.locator('[data-testid="userActions"]')
                        if 更多按钮.count() == 0:
                             更多按钮 = 页面对象.locator('div[aria-label="More"]')
                        
                        if 更多按钮.count() > 0 and 更多按钮.first.is_visible():
                            print(f"[步骤1] 正在点击“更多”菜单...")
                            拟人驱动.点击元素(更多按钮.first)
                            time.sleep(random.uniform(1, 2))
                            
                            # 2. 从菜单中选择“屏蔽”
                            屏蔽选项 = 页面对象.locator('[data-testid="block"]')
                            if 屏蔽选项.count() > 0 and 屏蔽选项.first.is_visible():
                                print(f"[步骤2] 正在点击“屏蔽”选项...")
                                拟人驱动.点击元素(屏蔽选项.first)
                                time.sleep(random.uniform(1, 2))
                                
                                # 3. 在弹窗中点击确认“屏蔽”
                                确认屏蔽按钮 = 页面对象.locator('[data-testid="confirmationSheetConfirm"]')
                                if 确认屏蔽按钮.count() > 0 and 确认屏蔽按钮.first.is_visible():
                                    print(f"[步骤3] 正在确认斩杀...")
                                    拟人驱动.点击元素(确认屏蔽按钮.first)
                                    print(f"【执行结果】成功斩杀用户 @{账户名}")
                                else:
                                    print(f"[错误] 无法定位“确认屏蔽”按钮")
                            else:
                                print(f"[错误] 无法定位“屏蔽”菜单项")
                        else:
                            print(f"[错误] 无法在主页上定位“更多”按钮")
                            
                    except Exception as 操作错误:
                        print(f"[失败] 斩杀操作流程中断: {操作错误}")
                
                # 用户要求：在处理完每个用户后进行随机时长的拟人行为
                print(f"[拟人执行] 准备进行随机延迟漫游...")
                拟人驱动.模拟漫游(最短时常=最小延迟, 最长时常=最大延迟)

            print("==================================================")
            print("[任务完成] 所有列表用户已处理完毕。")
            页面对象.close()

    except Exception as 致命错误:
        print(f"[致命] 程序执行中断: {致命错误}")

if __name__ == "__main__":
    执行主逻辑()
