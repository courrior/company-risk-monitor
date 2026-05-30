import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import urllib.parse
import feedparser
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime, timedelta, timezone
import time
import random

# ==================== 【企业名单配置区】 ====================
COMPANIES = [
    {"name": "海博思创", "full_name": "北京海博思创科技股份有限公司", "group": "", "group_full": "—"},
    {"name": "富力城", "full_name": "沧州富力城房地产开发有限公司", "group": "富力", "group_full": "广州富力地产股份有限公司"},
    {"name": "盛钰", "full_name": "沧州盛钰房地产开发有限公司", "group": "荣盛", "group_full": "荣盛控股股份有限公司"},
    {"name": "旭阳化工", "full_name": "沧州旭阳化工有限公司", "group": "旭阳", "group_full": "旭阳集团有限公司"},
    {"name": "中铁装备", "full_name": "沧州中铁装备制造材料有限公司", "group": "新华联合冶金", "group_full": "河北新华联合冶金控股集团有限公司"},
    {"name": "承德建龙", "full_name": "承德建龙特殊钢有限公司", "group": "建龙", "group_full": "北京建龙重工集团有限公司"},
    {"name": "燕北冶金", "full_name": "承德燕北冶金材料有限公司", "group": "建龙", "group_full": "北京建龙重工集团有限公司"},
    {"name": "海伟石化", "full_name": "海伟石化有限公司", "group": "", "group_full": "—"},
    {"name": "正大制管", "full_name": "邯郸正大制管集团股份有限公司", "group": "正大制管", "group_full": "正大制管集团"},
    {"name": "诚实实业", "full_name": "河北诚实实业集团有限公司", "group": "诚实", "group_full": "河北诚实实业集团有限公司"},
    {"name": "华荣制药", "full_name": "河北华荣制药有限公司", "group": "石药", "group_full": "石药控股集团有限公司"},
    {"name": "敬业高品钢", "full_name": "河北敬业高品钢科技有限公司", "group": "敬业", "group_full": "敬业集团有限公司"},
    {"name": "敬业宽板", "full_name": "河北敬业宽板科技有限公司", "group": "敬业", "group_full": "敬业集团有限公司"},
    {"name": "千喜鹤饮食", "full_name": "河北千喜鹤饮食股份有限公司", "group": "千喜鹤", "group_full": "河北千喜鹤饮食股份有限公司"},
    {"name": "新武安钢铁", "full_name": "河北新武安钢铁集团烘熔钢铁有限公司", "group": "普阳钢铁", "group_full": "河北普阳钢铁有限公司"},
    {"name": "旭阳能源", "full_name": "河北旭阳能源有限公司", "group": "旭阳", "group_full": "旭阳集团有限公司"},
    {"name": "华夏幸福基业控股", "full_name": "华夏幸福基业控股股份公司", "group": "华夏幸福", "group_full": "华夏幸福基业股份有限公司"},
    {"name": "今麦郎饮品", "full_name": "今麦郎饮品股份有限公司", "group": "今麦郎", "group_full": "今麦郎投资有限公司"},
    {"name": "敬业钢铁", "full_name": "敬业钢铁有限公司", "group": "敬业", "group_full": "敬业集团有限公司"},
    {"name": "铭顺石油天然气", "full_name": "廊坊市铭顺石油天然气销售有限公司", "group": "铭顺", "group_full": "廊坊市铭顺石油天然气销售有限公司"},
    {"name": "廊坊市天然气", "full_name": "廊坊市天然气有限公司", "group": "廊坊市天然气", "group_full": "廊坊市天然气有限公司"},
    {"name": "翔福新能源", "full_name": "内蒙古翔福新能源有限责任公司", "group": "旭阳", "group_full": "旭阳集团有限公司"},
    {"name": "迁安正大", "full_name": "迁安正大通用钢管有限公司", "group": "正大制管", "group_full": "邯郸正大制管集团股份有限公司"},
    {"name": "荣盛房地产", "full_name": "荣盛房地产发展股份有限公司", "group": "荣盛", "group_full": "荣盛控股股份有限公司"},
    {"name": "三河汇福粮油集团精炼植物油", "full_name": "三河汇福粮油集团精炼植物油有限公司", "group": "三河汇福", "group_full": "三河汇福粮油集团有限公司"},
    {"name": "恩必普", "full_name": "石药集团恩必普药业有限公司", "group": "石药", "group_full": "石药控股集团有限公司"},
    {"name": "班公措", "full_name": "唐山班公措新材料有限公司", "group": "", "group_full": "—"},
    {"name": "创齐贸易", "full_name": "唐山创齐贸易有限公司", "group": "", "group_full": "—"},
    {"name": "万丰制管", "full_name": "唐山市丰南区万丰制管有限公司", "group": "", "group_full": "—"},
    {"name": "格萨贸易", "full_name": "唐山市格萨贸易有限公司", "group": "格萨", "group_full": "唐山市格萨贸易有限公司"},
    {"name": "唐山旭阳", "full_name": "唐山旭阳化工有限公司", "group": "旭阳", "group_full": "旭阳集团有限公司"},
    {"name": "津衡石油化工", "full_name": "天津津衡石油化工贸易有限责任公司", "group": "", "group_full": "—"},
    {"name": "武安市裕华钢铁", "full_name": "武安市裕华钢铁有限公司", "group": "冀南钢铁", "group_full": "冀南钢铁集团有限公司"},
    {"name": "澳森金属", "full_name": "辛集市澳森金属制品有限公司", "group": "澳森特钢", "group_full": "辛集市澳森特钢集团有限公司"},
    {"name": "澳森特钢", "full_name": "辛集市澳森特钢集团有限公司", "group": "澳森特钢", "group_full": "辛集市澳森特钢集团有限公司"},
    {"name": "泽明国际", "full_name": "辛集市泽明国际贸易有限公司", "group": "", "group_full": "—"},
    {"name": "新奥控股", "full_name": "新奥控股投资股份有限公司", "group": "廊坊市天然气", "group_full": "廊坊市天然气有限公司"},
    {"name": "新奥能源", "full_name": "新奥能源供应链有限公司", "group": "廊坊市天然气", "group_full": "廊坊市天然气有限公司"},
    {"name": "银盾云", "full_name": "浙江银盾云科技有限公司", "group": "京津冀润泽", "group_full": "京津冀润泽（廊坊）数字信息有限公司"},
    {"name": "正大(天津)供应链", "full_name": "正大(天津)供应链有限公司", "group": "正大制管", "group_full": "邯郸正大制管集团股份有限公司"},
    {"name": "知合", "full_name": "知合控股有限公司", "group": "华夏幸福", "group_full": "华夏幸福基业股份有限公司"},
    {"name": "中海外", "full_name": "中海外交通建设有限公司", "group": "", "group_full": "—"}
]
# ==================================================================================

API_URL = "https://models.inference.ai.azure.com/chat/completions"
MODEL_NAME = "gpt-4o-mini"  

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0"
]

def parse_date_universal(date_str, bj_now):
    """通用国内媒体时间智能转换引擎"""
    date_str = date_str.strip()
    try:
        if '分钟前' in date_str:
            m = re.search(r'(\d+)', date_str)
            return bj_now - timedelta(minutes=int(m.group(1))) if m else bj_now
        elif '小时前' in date_str:
            h = re.search(r'(\d+)', date_str)
            return bj_now - timedelta(hours=int(h.group(1))) if h else bj_now
        elif '天前' in date_str:
            d = re.search(r'(\d+)', date_str)
            return bj_now - timedelta(days=int(d.group(1))) if d else bj_now
        else:
            match_cn = re.search(r'(\d{4})年(\d{1,2})月(\d{1,2})日', date_str)
            if match_cn:
                return datetime(int(match_cn.group(1)), int(match_cn.group(2)), int(match_cn.group(3)), tzinfo=timezone(timedelta(hours=8)))
            match_iso = re.search(r'(\d{4})[-──](\d{1,2})[-──](\d{1,2})', date_str)
            if match_iso:
                return datetime(int(match_iso.group(1)), int(match_iso.group(2)), int(match_iso.group(3)), tzinfo=timezone(timedelta(hours=8)))
    except Exception:
        pass
    return None

def fetch_news_baidu_session(session, query, cutoff_date, bj_now, max_pages=2):
    """【强攻绕过版】带会话保持与风控检测的百度新闻爬取"""
    encoded_query = urllib.parse.quote(query)
    articles = []
    
    for page in range(max_pages):
        pn = page * 10
        url = f"https://www.baidu.com/s?tn=news&rtt=1&bsst=1&cl=2&wd={encoded_query}&pn={pn}"
        
        try:
            # 继承Session的合法Cookie，假装是真人在点击
            response = session.get(url, timeout=10)
            response.encoding = 'utf-8'
            
            if response.status_code != 200:
                print(f"     ├─ ❌ [百度阻断] 状态码异常 {response.status_code}")
                break
                
            if "安全验证" in response.text or "verify" in response.text:
                print(f"     ├─ 🚨 [强攻受阻] 百度第 {page+1} 页弹出图形验证码！主动启动强攻绕过备用机制。")
                break
                
            soup = BeautifulSoup(response.text, 'html.parser')
            news_items = soup.select('div.result-op, div.c-container')
            
            if not news_items:
                break
                
            page_filtered = 0
            for item in news_items:
                title_tag = item.find('h3') or item.find('a', class_=lambda x: x and 'title' in x.lower())
                if not title_tag: continue
                a_tag = title_tag.find('a') if title_tag.name != 'a' else title_tag
                if not a_tag: continue
                    
                title = a_tag.get_text(strip=True)
                summary_tag = item.find('span', class_=lambda x: x and ('content' in x.lower() or 'summary' in x.lower())) or item.find('div', class_=lambda x: x and 'font-normal' in x.lower())
                summary = summary_tag.get_text(strip=True) if summary_tag else ""
                
                item_text = item.get_text(" ")
                date_match = re.search(r'(\d{4}年\d{1,2}月\d{1,2}日|\d{4}-\d{2}-\d{2}|\d+小时前|\d+天前|\d+分钟前)', item_text)
                raw_date_str = date_match.group(1) if date_match else "近期发布"
                
                parsed_dt = parse_date_universal(raw_date_str, bj_now)
                if parsed_dt and parsed_dt < cutoff_date:
                    page_filtered += 1
                    continue
                    
                formatted_pub_date = parsed_dt.strftime("%Y年%m月%d日") if parsed_dt else raw_date_str
                articles.append(f"【数据源: 百度新闻】媒体发布时间: {formatted_pub_date}\n标题: {title}\n摘要: {summary}\n---")
                
            print(f"     ├─ [百度第 {page+1} 页] 捞出 {len(news_items)} 条，时效过滤掉 {page_filtered} 条")
            
            if page < max_pages - 1:
                time.sleep(random.uniform(2.0, 4.0))
                
        except Exception as e:
            print(f"     └─ [百度网络波动]: {e}")
            break
            
    return articles

def fetch_news_360_backup(query, cutoff_date, bj_now):
    """【国内保底雷达】360时效绿色新闻引擎（抗封锁、高覆盖）"""
    encoded_query = urllib.parse.quote(query)
    # rank=p 代表按时间最新排序
    url = f"https://news.so.com/ns?q={encoded_query}&rank=p"
    articles = []
    
    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Referer": "https://news.so.com/"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = 'utf-8'
        
        soup = BeautifulSoup(response.text, 'html.parser')
        # 360新闻标准的条目容器类名为 res-list
        news_items = soup.select('li.res-list, div.res-list')
        
        filtered_count = 0
        for item in news_items:
            title_tag = item.find('h3')
            if not title_tag: continue
            a_tag = title_tag.find('a')
            if not a_tag: continue
            
            title = a_tag.get_text(strip=True)
            summary_tag = item.find('p') or item.find('span', class_='content')
            summary = summary_tag.get_text(strip=True) if summary_tag else ""
            
            # 提取360新闻的发布时间
            sitename_tag = item.find('span', class_='sitename') or item.find('span', class_='showtime')
            raw_date_str = "近期发布"
            if sitename_tag:
                date_match = re.search(r'(\d{4}年\d{1,2}月\d{1,2}日|\d{4}-\d{2}-\d{2}|\d+小时前|\d+天前|\d+分钟前)', sitename_tag.get_text())
                if date_match:
                    raw_date_str = date_match.group(1)
            
            parsed_dt = parse_date_universal(raw_date_str, bj_now)
            if parsed_dt and parsed_dt < cutoff_date:
                filtered_count += 1
                continue
                
            formatted_pub_date = parsed_dt.strftime("%Y年%m月%d日") if parsed_dt else raw_date_str
            articles.append(f"【数据源: 360新闻】媒体发布时间: {formatted_pub_date}\n标题: {title}\n摘要: {summary}\n---")
            
        print(f"     ├─ [国内保底雷达(360新闻)] 成功捞出 {len(news_items)} 条，过滤掉过期 {filtered_count} 条")
        return articles
    except Exception as e:
        print(f"     ├─ ⚠️ [国内保底雷达波动] 无法获取360新闻数据: {e}")
        return []

def fetch_news(session, company_short, group_short):
    """【双引擎协同】百度绕过 + 360国内干货保底机制"""
    c_search = company_short.strip()
    g_search = group_short.strip()
    if g_search and len(g_search) <= 2 and not g_search.endswith("集团"):
        g_search = f"{g_search}集团"
    query = f"({c_search} OR {g_search})" if g_search and g_search != c_search else f"{c_search}"
        
    bj_tz = timezone(timedelta(hours=8))
    bj_now = datetime.now(bj_tz)
    cutoff_date = bj_now - timedelta(days=30)
    
    print(f"   [国内全网联合穿透] 检索主词: '{query}'")
    
    # ⚔️ 第一战线：带会话伪装的百度深度抓取
    articles_baidu = fetch_news_baidu_session(session, query, cutoff_date, bj_now, max_pages=2)
    
    # 🛡️ 第二战线：抗封锁国内保底雷达（哪怕百度全被拦截返回0条，这里也会兜底抓到国内干货）
    articles_360 = fetch_news_360_backup(query, cutoff_date, bj_now)
    
    # 🤝 双源大合流
    combined = articles_baidu + articles_360
    
    # 语义去重（防止两边抓到重复新闻）
    seen_titles = set()
    unique_articles = []
    for art in combined:
        title_line = [line for line in art.split('\n') if line.startswith('标题: ')]
        if title_line:
            title_text = title_line[0].replace('标题: ', '').strip()
            norm_title = re.sub(r'[^\w]', '', title_text)[:15] 
            if norm_title in seen_titles: continue
            seen_titles.add(norm_title)
        unique_articles.append(art)
        
    final_pool = unique_articles[:100]
    print(f"     └─ 🎯 [最终池生成] 本次穿透成功为 AI 锁定国内有效线索共: {len(final_pool)} 条")
    return "\n".join(final_pool)

def analyze_with_llm(company_full, group_full, raw_text, api_key):
    if not raw_text.strip():
        return "未发现风险信息"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    prompt = (
        f"你是一个专业的企业风控合规数据清洗漏斗。请对以下关于【所属集团官方全称：{group_full} | 企业官方全称：{company_full}】的网络新闻进行智能化风控筛选。\n\n"
        f"【核心筛选法则】：\n"
        f"输入的数据已经过Python底层语义时间戳初筛，发布时间均在30天内最新。请【剔除正面、正常经营信息】，【仅提取】涉及负面风险、合规问题、监管变动（包括但不限于：生产经营异常、违法违规、点名通报、现场检查、行政处罚、法律诉讼、被执行人、严重负面舆情等）。\n\n"
        f"【原始数据池】:\n{raw_text}\n\n"
        "【铁律指令 - 必须严格执行】:\n"
        "1. 必防幻觉铁律：你只能基于【原始数据池】内容提炼，绝不允许凭空捏造事件。\n"
        "2. 绝对中立铁律：完全真实、客观地还原新闻提及的事实本身，不进行主观定性。\n"
        "3. 拒绝过度总结：详尽还原原始事实细节（如包含具体的环保督察组点名详情、现场检查通报具体内容、公告编号、涉及金额等）。\n"
        "4. 【时效强制锚定规则】：\n"
        "   - 严禁输出“新闻未明确提及”或类似免责辞令！\n"
        "   - 提取逻辑：如果标题或摘要中写明了具体的日期、年份或月份（或者可以通过‘昨日’、‘上周’等结合【媒体发布时间】推导出来），请直接写出具体的转换日期。如果标题和摘要中【完全没有】出现任何更早的案发时间线索，请【直接将该条新闻的‘媒体发布时间’（精确到日期，如XXXX年XX月XX日）】作为风险发生时间！\n\n"
        "5. 如果发现任何符合要求的负面风险信息，请以清晰的列表形式说明。每一条必须严格且仅包含以下4个子字段：\n"
        f"   - 风险主体: [直接填写其对应的官方规范名称：{company_full} 或 {group_full}]\n"
        "   - 风险信息公布时间: [直接使用原始数据中提供的【媒体发布时间】]\n"
        "   - 风险信息发生时间: [严格执行上述“规则4”确定的具体日期。如找不到更早的线索，则必须直接照抄公布时间的年月日，绝对不准敷衍填写‘新闻未明确提及’！]\n"
        "   - 风险详细内容: [明确交代哪个主体在什么背景下发生了什么负面事件。详尽还原原始新闻中的现场检查细节、违规详情或涉诉事项]\n\n"
        "6. 如果发现新闻全部为正面宣传或没有任何风险信息，请【必须且仅】回复这7个字：未发现风险信息。绝对不能带有任何标点符号或多余文字。"
    )
    data = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": "你是一个严谨的风控合规专家。您深知风险系统严禁出现‘时间未知’的漏洞，懂得在摘要数据不全时将公布时间作为基准时间锚定，绝不偷懒敷衍。"},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.0
    }
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = requests.post(API_URL, json=data, headers=headers)
            if response.status_code == 200:
                res_json = response.json()
                if 'choices' in res_json and len(res_json['choices']) > 0:
                    return res_json['choices'][0]['message']['content'].strip()
            time.sleep(5)
        except Exception:
            time.sleep(5)
    return "监控数据获取异常（请稍后重新运行触发）"

def send_email(html_content, total_count, risk_count):
    smtp_server = os.environ.get("SMTP_SERVER", "smtp.qq.com")
    smtp_port = 465
    sender_user = os.environ.get("SMTP_USER")
    sender_pass = os.environ.get("SMTP_PASS")
    receiver = os.environ.get("RECEIVER_EMAIL")
    
    if not all([sender_user, sender_pass, receiver]):
        print("邮件配置不全，跳过发送。")
        return

    msg = MIMEMultipart()
    msg['From'] = sender_user
    msg['To'] = receiver
    msg['Subject'] = f"【每日风险监控】抗封锁联合版（总监控:{total_count}家 | 拦截兜底成功风险:{risk_count}家）"
    msg.attach(MIMEText(html_content, 'html', 'utf-8'))
    
    try:
        server = smtplib.SMTP_SSL(smtp_server, smtp_port)
        server.login(sender_user, sender_pass)
        server.sendmail(sender_user, [receiver], msg.as_string())
        server.quit()
        print("邮件汇总发送成功！")
    except Exception as e:
        print(f"邮件发送失败: {e}")

def main():
    api_key = os.environ.get("AI_KEY")
    if not api_key:
        print("错误：未配置 AI_KEY")
        return
        
    # ─── 核心破局点：初始化抗风控Session并提前注册Baidu通行证 ───
    session = requests.Session()
    ua = random.choice(USER_AGENTS)
    session.headers.update({
        "User-Agent": ua,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9",
    })
    try:
        print("[系统初始化] 正在伪装浏览器并向百度大厅申请合法访问通行证(Cookie)...")
        session.get("https://www.baidu.com/", timeout=5)
        print("[初始化成功] 成功拿到百度合法访客凭证，抗封锁引擎启动。")
    except Exception:
        print("[初始化警告] 百度大厅连接超时，系统将强力依赖国内保底兜底引擎。")

    results = []
    risk_count = 0
    
    print(f"\n开始执行抗封锁全网深度监控，共 {len(COMPANIES)} 家企业...")
    for item in COMPANIES:
        comp_short = item["name"]
        comp_full = item["full_name"]
        group_short = item["group"]
        group_full = item["group_full"]
        
        print(f"\n[监控任务展开] 正在深度穿透: {group_full} -> {comp_full}")
        
        raw_text = fetch_news(session, comp_short, group_short)
        analysis = analyze_with_llm(comp_full, group_full, raw_text, api_key)
        
        if "监控数据获取异常" in analysis:
            status = "error"
        elif "未发现风险信息" in analysis:
            status = "safe"
        else:
            status = "risk"
            risk_count += 1
            
        results.append({
            "full_name": comp_full,
            "group_full": group_full,
            "analysis": analysis,
            "status": status
        })
        
        # 仿生学非等时静默隔离，打乱机器访问死规律
        sleep_time = random.uniform(5.0, 9.0)
        print(f"   [仿生防封隔离] 随机静默发呆 {sleep_time:.2f} 秒，切换下一家企业...")
        time.sleep(sleep_time)
            
    bj_now = datetime.now(timezone(timedelta(hours=8)))
    execution_time = bj_now.strftime("%Y-%m-%d %H:%M")

    html_body = f"""
    <html>
    <head>
        <style>
            body {{ font-family: 'Helvetica Neue', Arial, sans-serif; margin: 20px; color: #333; background-color: #fafafa; }}
            .container {{ max-width: 900px; background: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            table {{ width: 100%; border-collapse: collapse; margin: 20px 0; table-layout: fixed; }}
            th, td {{ border: 1px solid #e0e0e0; padding: 12px; text-align: left; word-break: break-all; }}
            th {{ background-color: #f5f5f5; font-weight: bold; }}
            .risk-no {{ color: #5cb85c; font-weight: bold; }}
            .risk-yes {{ color: #d9534f; font-weight: bold; }}
            .risk-error {{ color: #ff9800; font-weight: bold; font-style: italic; }}
            .detail-block {{ background-color: #fff9f9; padding: 15px; border-left: 4px solid #d9534f; margin-bottom: 15px; border-radius: 0 4px 4px 0; }}
            h2 {{ color: #2c3e50; border-bottom: 2px solid #eee; padding-bottom: 10px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2>每日企业风险监控整体汇总表</h2>
            <p style="color:#666;"><b>防御模式：百度Session伪装 + 360新闻国内全方位兜底</b> | 执行时间：北京时间 {execution_time}</p>
            <table>
                <colgroup>
                    <col style="width: 8%;">
                    <col style="width: 42%;">
                    <col style="width: 28%;">
                    <col style="width: 22%;">
                </colgroup>
                <tr>
                    <th>序号</th>
                    <th>企业全称</th>
                    <th>所属集团全称</th>
                    <th>风险监控状态</th>
                </tr>
    """
    
    for idx, item in enumerate(results, 1):
        if item["status"] == "safe":
            status_str = "未发现风险信息"
            status_class = "risk-no"
        elif item["status"] == "risk":
            status_str = "发现潜在风险/变动"
            status_class = "risk-yes"
        else:
            status_str = "大模型调用波动"
            status_class = "risk-error"
            
        html_body += f"""
                <tr>
                    <td>{idx}</td>
                    <td><b>{item["full_name"]}</b></td>
                    <td>{item["group_full"]}</td>
                    <td class="{status_class}">{status_str}</td>
                </tr>
        """
        
    html_body += """
            </table>
            <br/>
            <h2>企业风险详细说明列表</h2>
    """
    
    has_risk_detail = False
    for item in results:
        if item["status"] == "risk":
            has_risk_detail = True
            formatted_res = item["analysis"].replace("\n", "<br/>")
            html_body += f"""
                <div class="detail-block">
                    <h3 style="color:#c9302c; margin-top:0;">{item["group_full"]} - {item["full_name"]}</h3>
                    <p style="line-height:1.6; color:#444;">{formatted_res}</p>
                </div>
            """
            
    if not has_risk_detail:
        html_body += "<p style='color: #5cb85c; font-size: 15px;'><b>今日所有监控企业均【未发现风险信息】。</b></p>"
        
    html_body += """
        </div>
    </body>
    </html>
    """
    send_email(html_body, len(COMPANIES), risk_count)

if __name__ == "__main__":
    main()
