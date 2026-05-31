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

RISK_KEYWORDS = [
    "诉讼", "处罚", "点名", "通报", "违规", "破产", "执行", "违法"
]

API_URL = "https://models.inference.ai.azure.com/chat/completions"
MODEL_NAME = "gpt-4o-mini"  

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0"
]

def check_publish_date_valid(raw_date_label, bj_now):
    if not raw_date_label or raw_date_label == "近期发布":
        return True 
    raw_date_label = raw_date_label.strip()
    if any(keyword in raw_date_label for keyword in ["小时", "分钟", "刚", "当前", "昨天"]):
        return True
    match_days_ago = re.search(r'(\d+)\s*天前', raw_date_label)
    if match_days_ago:
        return int(match_days_ago.group(1)) <= 30
    numbers = [int(n) for n in re.findall(r'\d+', raw_date_label)]
    try:
        if len(numbers) >= 3 and numbers[0] >= 1000:
            year, month, day = numbers[0], numbers[1], numbers[2]
            target_dt = datetime(year, month, day, tzinfo=timezone(timedelta(hours=8)))
            return (bj_now - target_dt).days <= 30
        elif len(numbers) == 2:
            month, day = numbers[0], numbers[1]
            current_year = bj_now.year
            target_dt = datetime(current_year, month, day, tzinfo=timezone(timedelta(hours=8)))
            if target_dt > bj_now:
                target_dt = datetime(current_year - 1, month, day, tzinfo=timezone(timedelta(hours=8)))
            return (bj_now - target_dt).days <= 30
    except Exception:
        pass
    return True 

def fetch_news_google_rss(query, bj_tz, cutoff_date):
    encoded_query = urllib.parse.quote(query)
    url = f"https://news.google.com/rss/search?q={encoded_query}+when:30d&hl=zh-CN&gl=CN&ceid=CN:zh-Hans"
    articles = []
    try:
        feed = feedparser.parse(url)
        for entry in feed.entries:
            parsed_time = entry.get('published_parsed')
            if parsed_time:
                dt_utc = datetime(parsed_time.tm_year, parsed_time.tm_mon, parsed_time.tm_mday,
                                  parsed_time.tm_hour, parsed_time.tm_min, parsed_time.tm_sec, tzinfo=timezone.utc)
                dt_bj = dt_utc.astimezone(bj_tz)
                if dt_bj < cutoff_date: continue
                pub_str = dt_bj.strftime("%Y年%m月%d日")
            else:
                pub_str = "近期发布"
            articles.append(f"【源:谷歌】时间: {pub_str} | 标题: {entry.title} | 摘要: {entry.get('summary', '')}")
        return articles
    except Exception:
        return []

def fetch_news_baidu(session, query, bj_now):
    encoded_query = urllib.parse.quote(query)
    url = f"https://www.baidu.com/s?tn=news&rtt=1&bsst=1&cl=2&wd={encoded_query}"
    articles = []
    try:
        response = session.get(url, timeout=8)
        response.encoding = 'utf-8'
        if response.status_code != 200 or "安全验证" in response.text:
            return []
        soup = BeautifulSoup(response.text, 'html.parser')
        blocks = soup.find_all(['div', 'li'], class_=lambda x: x and ('result' in x or 'container' in x))
        for b in blocks:
            a_tag = b.find('a')
            if not a_tag: continue
            title = a_tag.get_text(strip=True)
            if not title: continue
            b_text = b.get_text(" ")
            date_match = re.search(r'(\d{4}年\d{1,2}月\d{1,2}日|\d{4}-\d{2}-\d{2}|\d+月\d+日|\d{2}-\d{2}|\d+小时前|\d+天前|\d+分钟前)', b_text)
            raw_date_label = date_match.group(1) if date_match else "近期发布"
            if not check_publish_date_valid(raw_date_label, bj_now):
                continue
            articles.append(f"【源:百度】时间: {raw_date_label} | 标题: {title} | 摘要: {b_text[:150]}")
        return articles
    except Exception:
        return []

def fetch_news_360(query, bj_now):
    encoded_query = urllib.parse.quote(query)
    url = f"https://news.so.com/ns?q={encoded_query}&rank=p"
    articles = []
    headers = {"User-Agent": random.choice(USER_AGENTS), "Referer": "https://news.so.com/"}
    try:
        response = requests.get(url, headers=headers, timeout=8)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        items = soup.find_all(['li', 'div'], class_=lambda x: x and 'res-list' in x)
        for item in items:
            a_tag = item.find('h3').find('a') if item.find('h3') else item.find('a')
            if not a_tag: continue
            title = a_tag.get_text(strip=True)
            item_text = item.get_text(" ")
            date_match = re.search(r'(\d{4}年\d{1,2}月\d{1,2}日|\d{4}-\d{2}-\d{2}|\d+月\d+日|\d{2}-\d{2}|\d+小时前|\d+天前)', item_text)
            raw_date_label = date_match.group(1) if date_match else "近期发布"
            if not check_publish_date_valid(raw_date_label, bj_now):
                continue
            articles.append(f"【源:360】时间: {raw_date_label} | 标题: {title} | 摘要: {item_text[:150]}")
        return articles
    except Exception:
        return []

def get_combined_raw_pool(session, comp_short, group_short):
    bj_tz = timezone(timedelta(hours=8))
    bj_now = datetime.now(bj_tz)
    cutoff_date = bj_now - timedelta(days=30)
    
    search_queries = [comp_short]
    
    sample_size = min(2, len(RISK_KEYWORDS))
    selected_risks = random.sample(RISK_KEYWORDS, sample_size)
    for risk_word in selected_risks:
        search_queries.append(f"{comp_short} {risk_word}")

    if group_short and group_short != "—" and len(group_short) > 1:
        anchors = ["企业", "项目", "基地"]
        risks = ["违规", "处罚", "通报", "破产", "执行"]
        
        combined_group_queries = []
        for anchor in anchors:
            for risk in risks:
                combined_group_queries.append(f"{group_short} {anchor} {risk}")
        
        sample_group_size = min(6, len(combined_group_queries))
        search_queries.extend(random.sample(combined_group_queries, sample_group_size))
        
    search_queries = list(set(search_queries))

    all_articles = []
    for q in search_queries:
        print(f"     ├─ 🚀 触发【矩阵交叉搜索】: 【{q}】")
        g_res = fetch_news_google_rss(q, bj_tz, cutoff_date)
        b_res = fetch_news_baidu(session, q, bj_now)
        s_res = fetch_news_360(q, bj_now)
        all_articles.extend(g_res + b_res + s_res)
        time.sleep(random.uniform(1.8, 3.2))
        
    seen_keys = set()
    unique_pool = []
    for art in all_articles:
        match_title = re.search(r'标题:\s*(.*?)(\||\s|$)', art)
        if match_title:
            t_key = re.sub(r'[^\w]', '', match_title.group(1))[:12]
            if t_key in seen_keys: continue
            seen_keys.add(t_key)
        unique_pool.append(art)
        
    final_pool = unique_pool[:40]
    print(f"     └─ 🎯 [清洗完毕] 成功捕获 {len(final_pool)} 条交叉高密数据送入 AI 审查")
    return "\n".join(final_pool)

# ==================== 【4. 重构：AI模糊穿透审查模块】 ====================
def analyze_with_llm(company_full, group_full, raw_text, api_key):
    if not raw_text.strip():
        return "未发现风险信息"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    risk_words_str = "、".join(RISK_KEYWORDS)
        
    prompt = (
        f"你是一个拥有鹰眼般审视能力的企业风控专家。请对以下新闻样本进行深度合规剥离。\n"
        f"当前审查的核心目标企业是：【{company_full}】，其所属母集团为：【{group_full}】。\n\n"
        f"【核心风控铁律：集团级模糊穿透原则】\n"
        f"由于媒体和官方通报习惯不同，新闻中可能不会写出母集团全称‘{group_full}’。在判定关联风险时，请遵循‘核心词穿透’逻辑：\n"
        f"只要输入的数据中，涉案主体名称包含了母集团的核心特征词‘{group_core}’（例如新闻中出现了‘营口市敬业中板公司’、‘敬业中板’、‘乌兰浩特钢铁（敬业基地）’等包含‘{group_core}’二字的企业），"
        f"你必须视同该集团旗下子公司爆雷，属于本次审查的连带重大声誉与合规风险，立刻抓取还原！绝不允许因为具体子公司名称与目标企业不完全一致而将其过滤！\n\n"
        f"【重点监控情形】：{risk_words_str} 以及 违规、通报、破产、执行。\n\n"
        f"【输入样本数据】:\n{raw_text}\n\n"
        "【输出格式要求】:\n"
        "1. 只能基于搜索到的原文内容进行提炼，绝对不允许编造任何不存在的日期、金额或罪名。\n"
        "2. 只要触发上述任何关联公司或子公司的风险，必须以下列格式输出：\n"
        "   - 风险主体: 原文中出现的精确公司名称（如：营口市敬业中板公司）\n"
        "   - 风险信息公布时间: 照抄文本中的发布时间\n"
        "   - 风险信息发生时间: 原文提及的涉案起因时间（如：2022年至今累计违规生产）\n"
        "   - 风险详细内容: 详细还原违规新增产能、被生态环境部作为典型案例通报批评的来龙去脉\n\n"
        "3. 若无任何上述关联风险或全是正面宣传，仅回复这7个字：未发现风险信息。"
    )
    data = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": "你是一个专业的合规审查专家，深知母子公司连带声誉风险的穿透审查是合规的核心。"},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.0
    }
    
    max_retries = 5
    for attempt in range(max_retries):
        try:
            response = requests.post(API_URL, json=data, headers=headers, timeout=90)
            if response.status_code == 200:
                return response.json()['choices'][0]['message']['content'].strip()
            
            elif response.status_code == 429:
                sleep_time = 25 * (attempt + 1)
                print(f"     └─ ⚠️ [AI接口限流 429] 触发免费测试通道限制，第 {attempt + 1} 次休眠 {sleep_time} 秒后重试...")
                time.sleep(sleep_time)
            else:
                print(f"     └─ ❌ [AI接口异常] HTTP状态码: {response.status_code} | 原因: {response.text[:200]}")
                time.sleep(10)
        except requests.exceptions.Timeout:
            print(f"     └─ ⏳ [AI接口超时] 第 {attempt + 1} 次请求响应超过90秒，正在强行重试...")
            time.sleep(5)
        except Exception as e:
            print(f"     └─ ❌ [AI网络断开] 底层连接异常: {str(e)}")
            time.sleep(5)
            
    return "AI接口异常/超时"

def send_email(html_content, total_count, risk_count):
    smtp_server = os.environ.get("SMTP_SERVER", "smtp.qq.com")
    smtp_port = 465
    sender_user = os.environ.get("SMTP_USER")
    sender_pass = os.environ.get("SMTP_PASS")
    receiver = os.environ.get("RECEIVER_EMAIL")
    if not all([sender_user, sender_pass, receiver]): return

    msg = MIMEMultipart()
    msg['From'] = sender_user
    msg['To'] = receiver
    msg['Subject'] = f"【每日风险监控】（公司总数:{total_count}家 | 涉及风险企业数量:{risk_count}家）"
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
        print("错误：未检测到环境变量 AI_KEY，请先配置！")
        return
        
    session = requests.Session()
    session.headers.update({"User-Agent": random.choice(USER_AGENTS)})

    results = []
    risk_count = 0
    
    print(f"\n开始执行全网监控，共 {len(COMPANIES)} 家企业...")
    for item in COMPANIES:
        comp_short = item["name"]
        comp_full = item["full_name"]
        group_short = item["group"]
        group_full = item["group_full"]
        
        print(f"\n[任务启动] 正在扫描: {comp_full}")
        
        raw_text = get_combined_raw_pool(session, comp_short, group_short)
        analysis = analyze_with_llm(comp_full, group_full, raw_text, api_key)
        
        if "未发现风险信息" in analysis: status = "safe"
        elif "AI接口异常/超时" in analysis: status = "error"
        else:
            status = "risk"
            risk_count += 1
            
        results.append({"full_name": comp_full, "group_full": group_full, "analysis": analysis, "status": status})
        time.sleep(random.uniform(3.5, 6.0)) 
            
    bj_now = datetime.now(timezone(timedelta(hours=8)))
    execution_time = bj_now.strftime("%Y-%m-%d %H:%M")

    html_body = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #fafafa; }}
            .container {{ max-width: 900px; background: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
            th, td {{ border: 1px solid #e0e0e0; padding: 12px; text-align: left; }}
            th {{ background-color: #f5f5f5; }}
            .risk-no {{ color: #5cb85c; font-weight: bold; }}
            .risk-yes {{ color: #d9534f; font-weight: bold; }}
            .risk-err {{ color: #f0ad4e; font-weight: bold; }}
            .detail-block {{ background-color: #fff9f9; padding: 15px; border-left: 4px solid #d9534f; margin-bottom: 15px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2>每日企业风险监控</h2>
            <p>时间：{execution_time} | 矩阵爆破+大模型模糊穿透内核：已开启</p>
            <table>
                <tr><th>序号</th><th>企业名称</th><th>所属集团</th><th>状态</th></tr>
    """
    for idx, item in enumerate(results, 1):
        if item["status"] == "safe":
            s_str, s_cls = "未发现风险信息", "risk-no"
        elif item["status"] == "risk":
            s_str, s_cls = "发现潜在风险", "risk-yes"
        else:
            s_str, s_cls = "AI接口异常/超时", "risk-err"
            
        html_body += f"<tr><td>{idx}</td><td><b>{item['full_name']}</b></td><td>{item['group_full']}</td><td class='{s_cls}'>{s_str}</td></tr>"
    html_body += "</table><br/><h2>风险信息明细</h2>"
    
    has_r = False
    for item in results:
        if item["status"] == "risk":
            has_r = True
            analysis_html = item['analysis'].replace('\n', '<br/>')
            html_body += f"<div class='detail-block'><h3>{item['full_name']}</h3><p>{analysis_html}</p></div>"
    if not has_r: html_body += "<p style='color:#5cb85c;'>今日无触网风险。</p>"
    html_body += "</div></body></html>"
    send_email(html_body, len(COMPANIES), risk_count)

if __name__ == "__main__":
    main()
