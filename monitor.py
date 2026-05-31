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
    {"name": "海博思创", "full_name": "北京海博思创科技股份有限公司", "group": "", "group_full": "—", "affiliate_keywords": []},
    {"name": "富力城", "full_name": "沧州富力城房地产开发有限公司", "group": "富力", "group_full": "广州富力地产股份有限公司", "affiliate_keywords": []},
    {"name": "盛钰", "full_name": "沧州盛钰房地产开发有限公司", "group": "荣盛", "group_full": "荣盛控股股份有限公司", "affiliate_keywords": []},
    {"name": "旭阳化工", "full_name": "沧州旭阳化工有限公司", "group": "旭阳", "group_full": "旭阳集团有限公司", "affiliate_keywords": []},
    {"name": "中铁装备", "full_name": "沧州中铁装备制造材料有限公司", "group": "新华联合冶金", "group_full": "河北新华联合冶金控股集团有限公司", "affiliate_keywords": []},
    {"name": "承德建龙", "full_name": "承德建龙特殊钢有限公司", "group": "建龙", "group_full": "北京建龙重工集团有限公司", "affiliate_keywords": []},
    {"name": "燕北冶金", "full_name": "承德燕北冶金材料有限公司", "group": "建龙", "group_full": "北京建龙重工集团有限公司", "affiliate_keywords": []},
    {"name": "海伟石化", "full_name": "海伟石化有限公司", "group": "", "group_full": "—", "affiliate_keywords": []},
    {"name": "正大制管", "full_name": "邯郸正大制管集团股份有限公司", "group": "正大制管", "group_full": "正大制管集团", "affiliate_keywords": []},
    {"name": "诚实实业", "full_name": "河北诚实实业集团有限公司", "group": "诚实", "group_full": "河北诚实实业集团有限公司", "affiliate_keywords": []},
    {"name": "华荣制药", "full_name": "河北华荣制药有限公司", "group": "石药", "group_full": "石药控股集团有限公司", "affiliate_keywords": []},
    {"name": "千喜鹤饮食", "full_name": "河北千喜鹤饮食股份有限公司", "group": "千喜鹤", "group_full": "河北千喜鹤饮食股份有限公司", "affiliate_keywords": []},
    {"name": "新武安钢铁", "full_name": "河北新武安钢铁集团烘熔钢铁有限公司", "group": "普阳钢铁", "group_full": "河北普阳钢铁有限公司", "affiliate_keywords": []},
    {"name": "旭阳能源", "full_name": "河北旭阳能源有限公司", "group": "旭阳", "group_full": "旭阳集团有限公司", "affiliate_keywords": []},
    {"name": "华夏幸福基业控股", "full_name": "华夏幸福基业控股股份公司", "group": "华夏幸福", "group_full": "华夏幸福基业股份有限公司", "affiliate_keywords": []},
    {"name": "今麦郎饮品", "full_name": "今麦郎饮品股份有限公司", "group": "今麦郎", "group_full": "今麦郎投资有限公司", "affiliate_keywords": []},
    {"name": "铭顺石油天然气", "full_name": "廊坊市铭顺石油天然气销售有限公司", "group": "铭顺", "group_full": "廊坊市铭顺石油天然气销售有限公司", "affiliate_keywords": []},
    {"name": "廊坊市天然气", "full_name": "廊坊市天然气有限公司", "group": "廊坊市天然气", "group_full": "廊坊市天然气有限公司", "affiliate_keywords": []},
    {"name": "翔福新能源", "full_name": "内蒙古翔福新能源有限责任公司", "group": "旭阳", "group_full": "旭阳集团有限公司", "affiliate_keywords": []},
    {"name": "迁安正大", "full_name": "迁安正大通用钢管有限公司", "group": "正大制管", "group_full": "邯郸正大制管集团股份有限公司", "affiliate_keywords": []},
    {"name": "荣盛房地产", "full_name": "荣盛房地产发展股份有限公司", "group": "荣盛", "group_full": "荣盛控股股份有限公司", "affiliate_keywords": []},
    {"name": "三河汇福粮油集团精炼植物油", "full_name": "三河汇福粮油集团精炼植物油有限公司", "group": "三河汇福", "group_full": "三河汇福粮油集团有限公司", "affiliate_keywords": []},
    {"name": "恩必普", "full_name": "石药集团恩必普药业有限公司", "group": "石药", "group_full": "石药控股集团有限公司", "affiliate_keywords": []},
    {"name": "班公措", "full_name": "唐山班公措新材料有限公司", "group": "", "group_full": "—", "affiliate_keywords": []},
    {"name": "创齐贸易", "full_name": "唐山创齐贸易有限公司", "group": "", "group_full": "—", "affiliate_keywords": []},
    {"name": "万丰制管", "full_name": "唐山市丰南区万丰制管有限公司", "group": "", "group_full": "—", "affiliate_keywords": []},
    {"name": "格萨贸易", "full_name": "唐山市格萨贸易有限公司", "group": "格萨", "group_full": "唐山市格萨贸易有限公司", "affiliate_keywords": []},
    {"name": "唐山旭阳", "full_name": "唐山旭阳化工有限公司", "group": "旭阳", "group_full": "旭阳集团有限公司", "affiliate_keywords": []},
    {"name": "津衡石油化工", "full_name": "天津津衡石油化工贸易有限责任公司", "group": "", "group_full": "—", "affiliate_keywords": []},
    {"name": "武安市裕华钢铁", "full_name": "武安市裕华钢铁有限公司", "group": "冀南钢铁", "group_full": "冀南钢铁集团有限公司", "affiliate_keywords": []},
    {"name": "澳森金属", "full_name": "辛集市澳森金属制品有限公司", "group": "澳森特钢", "group_full": "辛集市澳森特钢集团有限公司", "affiliate_keywords": []},
    {"name": "澳森特钢", "full_name": "辛集市澳森特钢集团有限公司", "group": "澳森特钢", "group_full": "辛集市澳森特钢集团有限公司", "affiliate_keywords": []},
    {"name": "澤明国际", "full_name": "辛集市泽明国际贸易有限公司", "group": "", "group_full": "—", "affiliate_keywords": []},
    {"name": "新奥控股", "full_name": "新奥控股投资股份有限公司", "group": "廊坊市天然气", "group_full": "廊坊市天然气有限公司", "affiliate_keywords": []},
    {"name": "新奥能源", "full_name": "新奥能源供应链有限公司", "group": "廊坊市天然气", "group_full": "廊坊市天然气有限公司", "affiliate_keywords": []},
    {"name": "银盾云", "full_name": "浙江银盾云科技有限公司", "group": "京津冀润泽", "group_full": "京津冀润泽（廊坊）数字信息有限公司", "affiliate_keywords": []},
    {"name": "正大(天津)供应链", "full_name": "正大(天津)供应链有限公司", "group": "正大制管", "group_full": "邯郸正大制管集团股份有限公司", "affiliate_keywords": []},
    {"name": "知合", "full_name": "知合控股有限公司", "group": "华夏幸福", "group_full": "华夏幸福基业股份有限公司", "affiliate_keywords": []},
    {"name": "中海外", "full_name": "中海外交通建设有限公司", "group": "", "group_full": "—", "affiliate_keywords": []}
]

RISK_KEYWORDS = ["诉讼", "处罚", "减持", "通报", "违规", "破产", "执行", "违法"]

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

def deep_scrape_page_content(session, url):
    """
    点进重磅链接（如news.cn、gov.cn），完整抓取正文前2000字，从根本上解决摘要被截断的盲区
    """
    if not url or not url.startswith("http"): return ""
    if any(ext in url.lower() for ext in [".pdf", ".docx", ".xlsx", ".zip"]): return ""
    try:
        res = session.get(url, timeout=6, headers={"User-Agent": random.choice(USER_AGENTS)})
        res.encoding = res.apparent_encoding or 'utf-8'
        if res.status_code != 200: return ""
        soup = BeautifulSoup(res.text, 'html.parser')
        for element in soup(["script", "style", "nav", "footer", "header"]):
            element.extract()
        full_text = soup.get_text(" ")
        clean_text = re.sub(r'\s+', ' ', full_text).strip()
        return clean_text[:2000] 
    except Exception:
        return ""

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
            articles.append({"source": "谷歌/权威网源", "time": pub_str, "title": entry.title, "link": entry.link, "summary": entry.get('summary', '')})
        return articles
    except Exception:
        return []

def fetch_web_baidu(session, query, bj_now):
    """
    并入全网网页搜索通道，打破“新闻”类目限制，无条件捕获政务、通报等全量网页
    """
    encoded_query = urllib.parse.quote(query)
    url = f"https://www.baidu.com/s?wd={encoded_query}&gpc=stf%3D{int(time.time()-2592000)}%2C{int(time.time())}%7Cstftype%3D2"
    articles = []
    try:
        response = session.get(url, timeout=8)
        response.encoding = 'utf-8'
        if response.status_code != 200 or "安全验证" in response.text:
            return []
        soup = BeautifulSoup(response.text, 'html.parser')
        blocks = soup.find_all('div', class_=lambda x: x and 'result' in x and 'c-container' in x)
        for b in blocks:
            a_tag = b.find('a')
            if not a_tag: continue
            title = a_tag.get_text(strip=True)
            link = a_tag.get('href', '')
            if not title: continue
            b_text = b.get_text(" ")
            date_match = re.search(r'(\d{4}年\d{1,2}月\d{1,2}日|\d{4}-\d{2}-\d{2}|\d+月\d+日|\d{2}-\d{2}|\d+小时前|\d+天前|\d+分钟前)', b_text)
            raw_date_label = date_match.group(1) if date_match else "近期发布"
            if not check_publish_date_valid(raw_date_label, bj_now):
                continue
            articles.append({"source": "百度全网", "time": raw_date_label, "title": title, "link": link, "summary": b_text[:200]})
        return articles
    except Exception:
        return []

def get_combined_raw_pool(session, comp_full, group_full, affiliate_keywords):
    bj_tz = timezone(timedelta(hours=8))
    bj_now = datetime.now(bj_tz)
    cutoff_date = bj_now - timedelta(days=30)
    
    search_queries = [f'"{comp_full}"']
    
    if group_full and group_full != "—":
        search_queries.append(f'"{group_full}"')
        group_core = group_full.replace("有限公司", "").replace("集团", "").strip()
        if len(group_core) > 1:
            search_queries.append(f'"{group_core}集团"')

    for aff in affiliate_keywords:
        search_queries.append(f'"{aff}"')

    search_queries = list(set(search_queries))
    raw_articles = []

    for q in search_queries:
        print(f"     ├─ 🚀 启动【全量饱和检索】: 【{q}】")
        g_res = fetch_news_google_rss(q, bj_tz, cutoff_date)
        b_res = fetch_web_baidu(session, q, bj_now)
        raw_articles.extend(g_res + b_res)
        time.sleep(random.uniform(1.5, 2.5))
        
    seen_links = set()
    unique_articles = []
    for art in raw_articles:
        link = art["link"]
        if link in seen_links: continue
        seen_links.add(link)
        unique_articles.append(art)

    final_text_blocks = []
    穿透计数 = 0
    
    for art in unique_articles[:25]: 
        url = art["link"]
        is_authoritative = any(domain in url for domain in ["news.cn", "gov.cn", "cctv", "people.com", "xinhuanet"])
        has_risk_clue = any(kw in art["title"] for kw in RISK_KEYWORDS)
        
        if (is_authoritative or has_risk_clue) and 穿透计数 < 8:
            print(f"     │  ⚡ 触发【二级网页深度穿透】：{art['title'][:15]}... -> 正在抓取正文")
            full_context = deep_scrape_page_content(session, url)
            if full_context:
                art["summary"] = f"[网页穿透全文提取]: {full_context}"
                穿透计数 += 1
            time.sleep(random.uniform(0.8, 1.5))
            
        block = f"【源:{art['source']}】| 时间: {art['time']} | 标题: {art['title']} | 链接: {url} | 文本内容: {art['summary']}"
        final_text_blocks.append(block)
        
    print(f"     └─ 🎯 成功捕获 {len(final_text_blocks)} 条富文本数据送入 AI 审理")
    return "\n".join(final_text_blocks)

def analyze_with_llm(company_full, group_full, affiliate_keywords, raw_text, api_key):
    if not raw_text.strip():
        return "未发现风险信息"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    risk_words_str = "、".join(RISK_KEYWORDS)
    group_core = group_full.replace("有限公司", "").replace("集团", "").strip() if (group_full and group_full != "—") else ""
    
    prompt = (
        f"你是一个拥有顶级鹰眼合规审视能力的企业风控与反洗钱专家。请对以下全网捕获的穿透富文本进行严密审计。\n"
        f"【核心审计目标】：\n"
        f"1. 目标企业：【{company_full}】\n"
        f"2. 母集团：【{group_full}】（核心特征词：{group_core}）\n"
        f"3. 核心关联或派生企业特征词：{affiliate_keywords}\n\n"
        f"【重大风控穿透准则（零容忍）】:\n"
        f"官方政务通报、环保督察报告、司法公告等往往篇幅极长且属于合并通报。新闻标题可能完全不提及目标公司。\n"
        f"你必须逐字通读以下输入样本。只要文本任何一个角落（包括长文内嵌名单、附录、提及的历史涉案行为）中，"
        f"出现了上述【任何一个】目标企业、母集团全称/简称、或关联企业特征词，并且涉及【{risk_words_str}】等合规、声誉风险，"
        f"你必须视同触发实质性爆雷，立刻精准抓取还原！绝对不放过任何隐藏在长文底部的株连/连带风险。\n\n"
        f"【输入样本富文本数据】:\n{raw_text}\n\n"
        "【输出格式要求】:\n"
        "1. 只能基于搜索到的原文内容进行提炼，绝对不允许编造任何不存在的日期、金额或罪名。\n"
        "2. 只要触发风险，必须按以下格式输出：\n"
        "   - 风险主体: 原文中出现的精确公司/集团名称\n"
        "   - 风险信息公布时间: 照抄文本中的发布时间或通报时间\n"
        "   - 风险信息发生时间: 原文提及的涉案起因/被查时间\n"
        "   - 风险详细内容: 详细还原违规风险、被通报批评或处罚的来龙去脉、案由与文号\n"
        "3. 若仔细通读后无任何关联风险（例如仅为新品推介、日常无关联政治新闻），则必须仅回复这7个字：未发现风险信息。"
    )
    
    data = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": "你是一个严厉且毫无漏洞的合规风控专家，深知长文嵌套通报是企业防范连带声誉风险的死角。"},
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
                time.sleep(sleep_time)
            else:
                time.sleep(10)
        except Exception:
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
    msg['Subject'] = f"【每日风险信息监测】（企业总数:{total_count}家 | 发现风险信息:{risk_count}家）"
    msg.attach(MIMEText(html_content, 'html', 'utf-8'))
    try:
        server = smtplib.SMTP_SSL(smtp_server, smtp_port)
        server.login(sender_user, sender_pass)
        server.sendmail(sender_user, [receiver], msg.as_string())
        server.quit()
        print("邮件发送成功！")
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
    
    print(f"\n开始执行合规深度扫描，共 {len(COMPANIES)} 家企业...")
    for item in COMPANIES:
        comp_full = item["full_name"]
        group_full = item["group_full"]
        affiliate_keywords = item.get("affiliate_keywords", [])
        
        print(f"\n[任务启动] 正在扫描: {comp_full}")
        raw_text = get_combined_raw_pool(session, comp_full, group_full, affiliate_keywords)
        analysis = analyze_with_llm(comp_full, group_full, affiliate_keywords, raw_text, api_key)
        
        if "未发现风险信息" in analysis: status = "safe"
        elif "AI接口异常/超时" in analysis: status = "error"
        else:
            status = "risk"
            risk_count += 1
            
        results.append({"full_name": comp_full, "group_full": group_full, "analysis": analysis, "status": status})
        time.sleep(random.uniform(3.5, 5.5))
            
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
            <h2>每日企业合规风险监控结果报告</h2>
            <p>时间：{execution_time} | 全量饱和检索 + 网页深度二级穿透已全面启动</p>
            <table>
                <tr><th>序号</th><th>企业名称</th><th>所属集团</th><th>风险信息</th></tr>
    """
    for idx, item in enumerate(results, 1):
        if item["status"] == "safe":
            s_str, s_cls = "未发现风险信息", "risk-no"
        elif item["status"] == "risk":
            s_str, s_cls = "发现潜在合规风险（见下方明细）", "risk-yes"
        else:
            s_str, s_cls = "AI接口异常/超时", "risk-err"
            
        html_body += f"<tr><td>{idx}</td><td><b>{item['full_name']}</b></td><td>{item['group_full']}</td><td class='{s_cls}'>{s_str}</td></tr>"
    html_body += "</table><br/><h2>风险穿透审计明细</h2>"
    
    has_r = False
    for item in results:
        if item["status"] == "risk":
            has_r = True
            analysis_html = item['analysis'].replace('\n', '<br/>')
            html_body += f"<div class='detail-block'><h3>{item['full_name']}</h3><p>{analysis_html}</p></div>"
    if not has_r: html_body += "<p style='color:#5cb85c;'>今日名单内所有企业均未发现触发合规风控红线。</p>"
    html_body += "</div></body></html>"
    send_email(html_body, len(COMPANIES), risk_count)

if __name__ == "__main__":
    main()
