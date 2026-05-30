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

def fetch_news_baidu(query):
    """主引擎：百度新闻网页无痕抓取（时效性极佳，专克国内政务与合规通报）"""
    encoded_query = urllib.parse.quote(query)
    # rtt=1 表示按时间排序（风控最核心的诉求），bsst=1 开启高级检索
    url = f"https://www.baidu.com/s?tn=news&rtt=1&bsst=1&cl=2&wd={encoded_query}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Referer": "https://www.baidu.com/"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = 'utf-8'
        if response.status_code != 200:
            return []
            
        soup = BeautifulSoup(response.text, 'html.parser')
        # 抓取百度新闻的标准容器结构
        news_items = soup.select('div.result-op, div.c-container')
        
        articles = []
        for item in news_items:
            title_tag = item.find('h3') or item.find('a', class_=lambda x: x and 'title' in x.lower())
            if not title_tag:
                continue
            a_tag = title_tag.find('a') if title_tag.name != 'a' else title_tag
            if not a_tag:
                continue
                
            title = a_tag.get_text(strip=True)
            
            # 抓取摘要片段
            summary_tag = item.find('span', class_=lambda x: x and ('content' in x.lower() or 'summary' in x.lower())) or item.find('div', class_=lambda x: x and 'font-normal' in x.lower())
            summary = summary_tag.get_text(strip=True) if summary_tag else item.get_text(" ", strip=True).replace(title, "").strip()
            
            # 解析百度暴露的时间文本（如："生态环境部 2小时前" 或 "财联社 2026年05月12日"）
            item_text = item.get_text(" ")
            date_match = re.search(r'(\d{4}年\d{1,2}月\d{1,2}日|\d{4}-\d{2}-\d{2}|\d+小时前|\d+天前|\d+分钟前)', item_text)
            pub_date = date_match.group(1) if date_match else "近期发布"
            
            articles.append(f"【媒体发布时间】: {pub_date}\n标题: {title}\n摘要: {summary}\n---")
        return articles
    except Exception as e:
        print(f"     └─ [主引擎异常] 百度网页解析失败: {e}")
        return []

def fetch_news_google_rss(query, cutoff_date, bj_tz):
    """备用引擎：原有的 Google News RSS 机制（当百度受限时自动无缝兜底）"""
    encoded_query = urllib.parse.quote(query)
    url = f"https://news.google.com/rss/search?q={encoded_query}&hl=zh-CN&gl=CN&ceid=CN:zh-Hans"
    
    try:
        feed = feedparser.parse(url)
        articles = []
        seen_titles = set()
        
        for entry in feed.entries:
            title = entry.title.strip()
            if title in seen_titles:
                continue
            seen_titles.add(title)
            
            pub_date_str = "未知发布时间"
            parsed_time = entry.get('published_parsed')
            if parsed_time:
                dt_utc = datetime(parsed_time.tm_year, parsed_time.tm_mon, parsed_time.tm_mday,
                                  parsed_time.tm_hour, parsed_time.tm_min, parsed_time.tm_sec, tzinfo=timezone.utc)
                dt_bj = dt_utc.astimezone(bj_tz)
                if dt_bj < cutoff_date:
                    continue
                pub_date_str = dt_bj.strftime("%Y年%m月%d日 %H:%M")
            else:
                pub_date_str = entry.get('published', '未知发布时间')
                
            articles.append(f"【媒体发布时间】: {pub_date_str}\n标题: {entry.title}\n摘要: {entry.get('summary', '无')}\n---")
        return articles
    except Exception:
        return []

def fetch_news(company_short, group_short):
    """双引擎总控调度器"""
    c_search = company_short.strip()
    g_search = group_short.strip()
    
    if g_search and len(g_search) <= 2 and not g_search.endswith("集团"):
        g_search = f"{g_search}集团"
        
    if g_search and g_search != c_search:
        query = f"({c_search} OR {g_search})" 
    else:
        query = f"{c_search}"
        
    bj_tz = timezone(timedelta(hours=8))
    cutoff_date = datetime.now(bj_tz) - timedelta(days=30)
    
    print(f"   [数据检索中] 检索关键词: '{query}'")
    
    # 1. 尝试主引擎（百度新闻网页端）
    articles = fetch_news_baidu(query)
    if articles:
        print(f"     └─ [主引擎命中] 成功从百度新闻清洗出 {len(articles)} 条高时效样本")
        return "\n".join(articles[:15]) # 限制前15条精选，防Prompt过长
        
    # 2. 备用引擎兜底
    print(f"     └─ [引擎无缝切换] 百度未命中或受限，自动启用备用 Google RSS 引擎...")
    google_query = f"{query} when:30d"
    articles = fetch_news_google_rss(google_query, cutoff_date, bj_tz)
    if articles:
        print(f"     └─ [备用引擎命中] 成功从 Google RSS 补充 {len(articles)} 条样本")
        return "\n".join(articles[:20])
        
    print(f"     └─ [提示] 全网未发现该企业任何新闻动态")
    return ""

def analyze_with_llm(company_full, group_full, raw_text, api_key):
    """AI 风控清洗过滤层"""
    if not raw_text.strip():
        return "未发现风险信息"
        
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    prompt = (
        f"你是一个专业的企业风控合规数据清洗漏斗。请对以下关于【所属集团官方全称：{group_full} | 企业官方全称：{company_full}】的网络新闻进行智能化风控筛选。\n\n"
        f"【核心筛选法则】：\n"
        f"数据已确认属30天内最新。请【剔除正面、正常经营信息】，【仅提取】涉及负面风险、合规问题、监管变动（包括但不限于：生产经营异常、违法违规、点名通报、行政处罚、法律诉讼、被执行人、严重负面舆情等）。\n\n"
        f"【原始数据池】:\n{raw_text}\n\n"
        "【铁律指令 - 必须严格执行】:\n"
        "1. 必防幻觉铁律：你只能基于【原始数据池】内容提炼，绝不允许凭空捏造事件。\n"
        "2. 绝对中立铁律：完全真实、客观地还原新闻提及的事实本身，不进行主观定性。\n"
        "3. 拒绝过度总结：详尽还原原始事实细节（如包含具体的环保督察组点名详情、通报具体内容、公告编号、涉及金额等）。\n"
        "4. 【时效强制锚定规则】：\n"
        "   - 严禁输出“新闻未明确提及”或类似免责辞令！\n"
        "   - 提取逻辑：如果标题或摘要中写明了具体的日期、年份或月份（或者可以通过‘昨日’、‘上周’等结合【媒体发布时间】推导出来），请直接写出具体的转换日期。如果标题和摘要中【完全没有】出现任何更早的案发时间线索，请【直接将该条新闻的‘媒体发布时间’（精确到日期，如XXXX年XX月XX日）】作为风险发生时间！\n\n"
        "5. 如果发现任何符合要求的负面风险信息，请以清晰的列表形式说明。每一条必须严格且仅包含以下4个子字段：\n"
        f"   - 风险主体: [直接填写其对应的官方规范名称：{company_full} 或 {group_full}]\n"
        "   - 风险信息公布时间: [直接使用原始数据中提供的【媒体发布时间】]\n"
        "   - 风险信息发生时间: [严格执行上述“规则4”确定的具体日期。如找不到更早的线索，则必须直接照抄公布时间的年月日，绝对不准敷衍填写‘新闻未明确提及’！]\n"
        "   - 风险详细内容: [明确交代哪个主体在什么背景下发生了什么负面事件。详尽还原原始新闻中的违规细节、通报详情或涉诉事项]\n\n"
        "6. 如果发现新闻全部为正面宣传或没有任何风险信息，请【必须且仅】回复这7个字：未发现风险信息。绝对不能带有任何标点符号或多余文字。"
    )
    
    data = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": "你是一个严谨的风控合规专家。你深知风险系统严禁出现‘时间未知’的漏洞，懂得在摘要数据不全时将公布时间作为基准时间锚定，绝不偷懒敷衍。"},
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
            elif response.status_code == 429:
                time.sleep(15)
                continue
            else:
                time.sleep(5)
                continue
        except Exception:
            time.sleep(5)
            continue
            
    return "监控数据获取异常（请稍后重新运行触发）"

def send_email(html_content, total_count, risk_count):
    smtp_server = os.environ.get("SMTP_SERVER", "smtp.qq.com")
    smtp_port = 465
    sender_user = os.environ.get("SMTP_USER")
    sender_pass = os.environ.get("SMTP_PASS")
    receiver = os.environ.get("RECEIVER_EMAIL")
    
    if not all([sender_user, sender_pass, receiver]):
        print("错误：邮件环境变量未配置完整，无法发送。")
        return

    msg = MIMEMultipart()
    msg['From'] = sender_user
    msg['To'] = receiver
    msg['Subject'] = f"【每日风险监控】今日汇总表（监控:{total_count}家 | 发现风险:{risk_count}家）"
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
        print("错误：未配置 AI_KEY")
        return
        
    results = []
    risk_count = 0
    
    print(f"开始执行监控，共 {len(COMPANIES)} 家企业...")
    for item in COMPANIES:
        comp_short = item["name"]
        comp_full = item["full_name"]
        group_short = item["group"]
        group_full = item["group_full"]
        
        print(f"正在分析: {group_full} -> {comp_full}")
        
        raw_text = fetch_news(comp_short, group_short)
        analysis = analyze_with_llm(comp_full, group_full, raw_text, api_key)
        
        if "监控数据获取异常" in analysis or "分析失败" in analysis:
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
        
        time.sleep(4.5) # 安全间隔，模拟真人点击，彻底告别反爬验证码
            
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
            <p style="color:#666;"><b>数据源已升级：百度/Google全网联动</b> | 执行时间：北京时间 {execution_time}</p>
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
            status_str = "监控遇到网络波动（建议重试）"
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
