import csv
import time
import random
import os
import sys
import re
from DrissionPage import ChromiumPage, ChromiumOptions
from colorama import init, Fore, Style

# 初始化 colorama - 用于终端彩色输出
init(autoreset=True)

# 全局缓存: 存储从封包中拦截到的用户详细数据
# Key: 用户名 (不带 @), Value: 字典
全局用户数据缓存 = {}

def 初始化浏览器():
    """连接到已打开的浏览器"""
    print(f"{Fore.CYAN}正在连接到浏览器 (端口 9222)...")
    try:
        浏览器配置 = ChromiumOptions().set_local_port(9222)
        页面对象 = ChromiumPage(浏览器配置)
        print(f"{Fore.GREEN}成功连接到浏览器!")
        return 页面对象
    except Exception as 错误:
        print(f"{Fore.RED}连接失败: {错误}")
        print(f"{Fore.YELLOW}请确保浏览器已通过以下命令启动: chrome.exe --remote-debugging-port=9222")
        sys.exit(1)

def 获取用户输入():
    """获取用户输入参数"""
    print(f"\n{Fore.YELLOW}---设置运行参数---")
    
    # 默认链接
    默认链接 = "https://x.com/following"
    目标链接 = input(f"请输入主页/关注列表链接 (回车默认: 当前页面): ").strip()
    
    # 默认延迟
    try:
        延迟输入 = input(f"请输入滚动延迟(秒) (回车默认: 2.5): ").strip()
        滚动延迟 = float(延迟输入) if 延迟输入 else 2.5
    except ValueError:
        滚动延迟 = 2.5
        print(f"{Fore.RED}输入无效,使用默认延迟: {滚动延迟}")

    return 目标链接, 滚动延迟

def 滚动策略(页面对象, 滚动次数, 延迟):
    """
    执行 5次向下滚动, 1次向上滚动的策略
    """
    if 滚动次数 > 0 and 滚动次数 % 5 == 0:
        print(f"{Fore.BLUE}已向下滚动 5 次, 执行一次向上滚动以防卡顿...")
        页面对象.scroll.up(300) # 向上滚动一点
        time.sleep(1)
        # 再次向下滚动回原来的位置附近，保持流畅
        页面对象.scroll.down(100) 
    else:
        # 随机向下滚动 (根据用户要求步长改短 200)
        滚动距离 = random.randint(400, 700)
        页面对象.scroll.down(滚动距离)
    
    # 随机延迟，模拟真人
    # 解释: 这里在基础延迟上增加 ±0.5秒 的随机波动，是为了模拟真人操作的不规律性，防止被识别为机器人
    实际睡眠时间 = 延迟 + random.uniform(-0.5, 0.5)
    if 实际睡眠时间 < 0.5: 实际睡眠时间 = 0.5
    time.sleep(实际睡眠时间)

def update_cache_from_packet(数据包响应):
    """(混合模式) 从拦截的 JSON 数据包中更新全局缓存"""
    try:
        数据 = 数据包响应.response.body
        指令列表 = []
        
        # 尝试标准路径 (关注列表)
        if 'user' in 数据.get('data', {}):
            try:
                指令列表 = 数据['data']['user']['result']['timeline']['timeline']['instructions']
            except:
                pass
        
        # 尝试另一种路径
        if not 指令列表 and 'user' in 数据.get('data', {}):
             try:
                指令列表 = 数据['data']['user']['result']['timeline_v2']['timeline']['instructions']
             except:
                pass

        更新数量 = 0
        for 指令 in 指令列表:
            if 指令.get('type') == 'TimelineAddEntries':
                for 条目 in 指令.get('entries', []):
                    try:
                        内容 = 条目.get('content', {})
                        if 内容.get('entryType') == 'TimelineTimelineCursor':
                            continue
                            
                        用户结果 = 内容.get('itemContent', {}).get('user_results', {}).get('result', {})
                        if not 用户结果 or 'legacy' not in 用户结果:
                            continue
                            
                        核心信息 = 用户结果.get('core', {})
                        Legacy信息 = 用户结果.get('legacy', {})
                        
                        用户名 = 核心信息.get('screen_name') # 不带 @
                        if not 用户名: continue

                        # 提取我们需要的高级数据
                        缓存数据 = {
                            "粉丝数": Legacy信息.get('followers_count', 0),
                            "关注数": Legacy信息.get('friends_count', 0),
                            "是否蓝V": "是" if 用户结果.get('is_blue_verified') else "否",
                            "关注状态": "已关注" if 用户结果.get('relationship_perspectives', {}).get('following') else "未关注",
                            "是否关注我": "是" if 用户结果.get('relationship_perspectives', {}).get('followed_by') else "否",
                            "主页链接": f"https://x.com/{用户名}"
                        }
                        
                        全局用户数据缓存[用户名] = 缓存数据
                        更新数量 += 1
                        
                    except:
                        continue
        return 更新数量
    except:
        return 0

def 提取单个用户数据_混合(元素对象):
    """
    混合提取: 
    1. 从 DOM 获取: 用户名, XHunt评分 (仅 DOM 有)
    2. 从 缓存 获取: 粉丝数, 关注数 (仅 封包 有)
    """
    try:
        全部文本 = 元素对象.text
        文本行列表 = 全部文本.split('\n')
        
        用户名 = "未知"     # Handle (@xxx)
        显示名称 = "未知"   # Display Name
        Xhunt评分 = "-"    # 默认为 -
        
        # --- DOM: 提取 XHunt 评分 ---
        try:
            评分元素 = 元素对象.ele('.xhunt-avatar-rank-text', timeout=0.01) # 极短超时
            if 评分元素:
                原始评分 = 评分元素.text
                if "-" in 原始评分:
                    Xhunt评分 = "-"
                else:
                    Xhunt评分 = "".join(filter(str.isdigit, 原始评分))
        except:
            pass
            
        # --- DOM: 提取 用户名 ---
        for 索引, 行 in enumerate(文本行列表):
            if 行.startswith('@'):
                用户名 = 行
                if 索引 > 0: 显示名称 = 文本行列表[索引 - 1]
                break
        
        # 备用选择器提取用户名
        if 用户名 == "未知":
             try:
                链接元素 = 元素对象.ele('tag:a@@href^=/@@role=link', timeout=0.01)
                if 链接元素:
                    链接 = 链接元素.attr('href')
                    if 链接:
                        用户名 = f"@{链接.strip('/')}"
             except:
                 pass
        
        if 用户名 == "未知": return None

        纯用户名 = 用户名.replace('@', '')
        
        # --- 合并: 从缓存取数据 ---
        缓存 = 全局用户数据缓存.get(纯用户名, {})
        
        return {
            "用户名": 用户名,
            "显示名称": 显示名称,
            "XHunt评分": Xhunt评分, # 来自 DOM
            "粉丝数": 缓存.get("粉丝数", "等待刷新"), # 来自 封包
            "关注数": 缓存.get("关注数", "等待刷新"), # 来自 封包
            "是否蓝V": 缓存.get("是否蓝V", "否"),
            "关注状态": 缓存.get("关注状态", "未知"), 
            "是否关注我": 缓存.get("是否关注我", "未知"),
            "主页链接": f"https://x.com/{纯用户名}"
        }

    except Exception:
        return None

def 主程序():
    页面 = 初始化浏览器()
    
    目标链接, 延迟 = 获取用户输入()
    
    if 目标链接:
        print(f"{Fore.CYAN}即将导航到: {目标链接}")
        if not 目标链接.startswith('http'):
             if not "x.com" in 目标链接:
                 目标链接 = f"https://x.com/{目标链接.strip('@')}/following"
             else:
                 目标链接 = f"https://{目标链接}"
             
        页面.get(目标链接)
        print(f"{Fore.CYAN}等待页面加载 (3秒)...")
        time.sleep(3) 
    else:
        print(f"{Fore.CYAN}使用当前页面...")

    # 启动监听
    # 注: 调整位置，确保 attach 成功
    print(f"{Fore.CYAN}启动网络监听 (混合模式: 封包数据 + DOM渲染)...")
    try:
        页面.listen.start('Following')
        if 目标链接: 
            print(f"{Fore.CYAN}刷新页面以确保封包捕获...")
            页面.refresh()
            time.sleep(3)
    except Exception as e:
        print(f"{Fore.RED}监听启动失败: {e}")
        print(f"{Fore.YELLOW}将降级运行: 只能获取 XHunt 评分，无法获取粉丝数。")

    时间戳 = time.strftime("%Y%m%d_%H%M%S")
    文件名 = f"关注列表导出_{时间戳}.csv"
    文件已存在 = os.path.isfile(文件名)
    表头 = ["用户名", "显示名称", "粉丝数", "关注数", "XHunt评分", "是否蓝V", "关注状态", "是否关注我", "主页链接"]
    
    已提取用户集合 = set() # 记录已写入 CSV 的用户名
    
    # 恢复历史
    if 文件已存在:
        try:
            with open(文件名, 'r', encoding='utf-8-sig') as 文件:
                for 行 in csv.DictReader(文件):
                    if 行.get("用户名"): 已提取用户集合.add(行["用户名"])
            print(f"{Fore.GREEN}已读取 {len(已提取用户集合)} 条历史记录。")
        except: pass

    print(f"{Fore.YELLOW}>>> 开始混合提取 (封包+DOM)... 按 Ctrl+C 停止 <<<")
    print(f"{Fore.MAGENTA}>>> 提示: 程序会自动滚动。封包负责粉丝数，DOM负责XHunt数据 <<<")

    滚动计数 = 0
    本次提取总数 = 0

    try:
        with open(文件名, 'a', newline='', encoding='utf-8-sig') as 文件:
            写入器 = csv.DictWriter(文件, fieldnames=表头)
            if not 文件已存在: 写入器.writeheader()

            while True:
                # 1. 滚动触发加载
                滚动策略(页面, 滚动计数, 延迟)
                滚动计数 += 1
                
                # 2. 监听并更新缓存
                # 等待一会儿数据包，更新到全局字典
                包数量 = 0
                for 数据包 in 页面.listen.steps(timeout=2):
                    if 'Following' in 数据包.url:
                        包数量 += update_cache_from_packet(数据包)
                
                if 包数量 > 0:
                    print(f"\r{Fore.BLUE}[系统] 捕获数据包，更新了 {包数量} 个用户信息...", end="")

                # 3. 扫描 DOM 元素 (关联显示的数据)
                # 因为封包到了，页面应该也渲染了
                用户单元格列表 = 页面.eles('@@data-testid=UserCell')
                本轮新增 = 0
                
                for 单元格 in 用户单元格列表:
                    数据 = 提取单个用户数据_混合(单元格)
                    if 数据:
                        u = 数据['用户名']
                        
                        # [新增过滤] 严格模式: 如果没有获取到封包数据(粉丝数/关注数)，视为无效/非目标用户，直接跳过
                        # 这能有效过滤掉页面侧边栏 "Who to follow" 等不在关注列表里的用户
                        if 数据['粉丝数'] == "等待刷新" or 数据['关注数'] == "等待刷新":
                            continue

                        # 只有当数据完整(粉丝数不是等待刷新) 或者是确实提取了 且 未存在
                        if u not in 已提取用户集合:
                            写入器.writerow(数据)
                            文件.flush()
                            已提取用户集合.add(u)
                            本次提取总数 += 1
                            本轮新增 += 1
                            
                            粉丝显示 = 数据['粉丝数']
                            XH显示 = 数据['XHunt评分']
                            if XH显示 == "无": XH显示 = "-"
                            print(f"\n{Fore.GREEN}[+] 成功: {u:<15} | 粉丝: {粉丝显示:<6} | XHunt: {XH显示:<6}")

                print(f"\r{Fore.WHITE}>>> 状态: 滚动 {滚动计数} | 缓存池: {len(全局用户数据缓存)} | 已提取: {本次提取总数}", end="")

    except KeyboardInterrupt:
        print(f"\n{Fore.RED}>>> 停止 <<<")
        print(f"数据保存至: {文件名}")
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    主程序()
