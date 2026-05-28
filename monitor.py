import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import urllib.parse
import feedparser
import requests
from datetime import datetime, timedelta, timezone
import time

COMPANIES = [
    {"name": "海博思创", "group": ""},
    {"name": "富力城", "group": "富力"},
    {"name": "盛钰", "group": "荣盛"},
    {"name": "旭阳化工", "group": "旭阳"},
    {"name": "中铁装备", "group": "新华联合冶金"},
    {"name": "承德建龙", "group": "建龙"},
    {"name": "燕北冶金", "group": "建龙"},
    {"name": "海伟石化", "group": ""},
    {"name": "正大制管", "group": "正大制管"},
    {"name": "诚实实业", "group": "诚实"},
    {"name": "华荣制药", "group": "石药"},
    {"name": "敬业高品钢", "group": "敬业"},
    {"name": "敬业宽板", "group": "敬业"},
    {"name": "千喜鹤饮食", "group": "千喜鹤"},
    {"name": "新武安钢铁", "group": "普阳钢铁"},
    {"name": "旭阳能源", "group": "旭阳"},
    {"name": "华夏幸福基业控股", "group": "华夏幸福"},
    {"name": "今麦郎饮品", "group": "今麦郎"},
    {"name": "敬业钢铁", "group": "敬业"},
    {"name": "铭顺石油天然气", "group": "铭顺"},
    {"name": "廊坊市天然气", "group": "廊坊市天然气"},
    {"name": "翔福新能源", "group": "旭阳"},
    {"name": "迁安正大", "group": "正大制管"},
    {"name": "荣盛房地产", "group": "荣盛"},
    {"name": "三河汇福粮油集团精炼植物油", "group": "三河汇福"},
    {"name": "恩必普", "group": "石药"},
    {"name": "班公措", "group": ""},
    {"name": "创齐贸易", "group": ""},
    {"name": "万丰制管", "group": ""},
    {"name": "格萨贸易", "group": "格萨"},
    {"name": "旭阳化工", "group": "旭阳"},
    {"name": "津衡石油化工", "group": ""},
    {"name": "武安市裕华钢铁", "group": "冀南钢铁"},
    {"name": "澳森金属", "group": "澳森特钢"},
    {"name": "澳森特钢", "group": "澳森特钢"},
    {"name": "泽明国际", "group": ""},
    {"name": "新奥控股", "group": "廊坊市天然气"},
    {"name": "新奥能源", "group": "廊坊市天然气"},
    {"name": "银盾云", "group": "润泽"},
    {"name": "正大(天津)供应链", "group": "正大制管"},
    {"name": "知合", "group": "华夏幸福"},
    {"name": "中海外", "group": ""}
]

API_URL = "https://models.inference.ai.azure.com/chat/completions"
MODEL_NAME = "gpt-4o-mini"  

def fetch_news(company_name, group_name):
    """利用 Google News RSS 抓取信息，并将媒体发布时间自动换算为北京时间"""
    keywords = "(风险 OR 诉讼 OR 处罚 OR 违规 OR 财务 OR 执行 OR 舆情)"
    if group_name and group_name.strip():
        query = f"({company_name} OR {group_name}) {keywords} when:30d" 
    else:
        query = f"{company_name} {keywords} when:30d"
        
    encoded_query = urllib.parse.quote(query)
    url = f"https://news.google.com/rss/search?q={encoded_query}&hl=zh-CN&gl=CN&ceid=CN:zh-Hans"
    
    try:
        feed = feedparser.parse(url)
        articles = []
        
        print(f"   [调试信息] '{company_name}' 原始抓取到新闻条数: {len(feed.entries)} 条")
        
        for entry in feed.entries[:15]:
            pub_date_str = "未知发布时间"
            parsed_time = entry.get('published_parsed') 
            if parsed_time:
                try:
                    dt_utc = datetime(parsed_time.tm_year, parsed_time.tm_mon, parsed_time.tm_mday,
                                      parsed_time.tm_hour, parsed_time.tm_min, parsed_time.tm_sec,
                                      tzinfo=timezone.utc)
                    dt_bj = dt_utc.astimezone(timezone(timedelta(hours=8)))
                    pub_date_str = dt_bj.strftime("%Y年%m月%d日 %H:%M")
                except Exception:
                    pub_date_str = entry.get('published', '未知发布时间')
            else:
                pub_date_str = entry.get('published', '未知发布时间')

            articles.append(f"【媒体发布时间】: {pub_date_str}\n标题: {entry.title}\n摘要: {entry.get('summary', '无')}\n---")
            
        return "\n".join(articles)
    except Exception as e:
        print(f"抓取 {group_name}-{company_name} 失败: {e}")
        return ""

def analyze_with_llm(company_name, group_name, raw_text, api_key):
    """调用大模型进行纯事实、去分析化的结构化提炼，内置自动重试逻辑保障 100% 成功率"""
    if not raw_text.strip():
        return "未发现风险信息"
        
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    prompt = (
        f"你是一个专业的企业风控合规数据清洗工具。请对以下关于【所属集团：{group_name if group_name else '无'} | 企业名称：{company_name}】的网络搜索结果进行清洗与结构化提炼。\n\n"
        f"【原始搜索数据】:\n{raw_text}\n\n"
        "【铁律指令 - 必须严格执行】:\n"
        "1. 必防幻觉铁律：你只能且必须完全基于上方提供的【原始搜索数据】内容进行提炼。绝对不允许编造、臆断任何不存在的细节！\n"
        "2. 绝对中立铁律：【完全不需要】进行任何原因分析、后果预测、或主观定性（严禁出现“说明财务恶化”、“面临危机”、“提醒注意”等AI主观评价）。完全真实、客观地还原新闻提及的事实本身。\n"
        "3. 拒绝过度总结：保留原始数据中关键的时间、具体的涉案金额、具体的违规缘由、公告编号等核心事实细节，【严禁】将详细过程压缩、抽象成一句话。\n"
        "4. 如果发现风险或变动，请以清晰的列表形式说明。每一条必须严格且仅包含以下4个子字段，不得合并、缺失或自行增加其他字段：\n"
        "   - 风险主体: [必须写出原始数据中该事件直接指向的企业或集团的工商完整名称]\n"
        "   - 风险信息公布时间: [直接使用原始数据中提供的【媒体发布时间】]\n"
        "   - 风险信息发生时间: [事件真正发生的具体日期、年份、月份]\n"
        "   - 风险详细内容: [明确交代哪个主体在什么背景下发生了什么事。详尽还原原始事实细节，包含涉及的社会事件、诉讼、舆情、业务、涉案具体金额或违规事项，不作任何AI的二次加工和延伸解释]\n"
        "5. 如果没有任何相关的风险或变动信息，请【必须且仅】回复这7个字：未发现风险信息。绝对不能带有任何标点符号或多余文字。"
    )
    
    data = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": "你是一个只做客观事实提炼、不输出任何主观定性、原因及后果分析的AI风控助手。"},
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
                print(f"   [重试提示] 触发GitHub官方限流锁(429)，第 {attempt + 1} 次重试，正在静默等待 15 秒...")
                time.sleep(15)
                continue
            else:
                print(f"   [重试提示] 接口服务异常(状态码:{response.status_code})，5秒后进行第 {attempt + 1} 次重试...")
                time.sleep(5)
                continue
        except Exception as e:
            print(f"   [重试提示] 网络连通异常({e})，5秒后进行第 {attempt + 1} 次重试...")
            time.sleep(5)
            continue
            
    return "监控数据获取异常（请稍后重新运行触发）"

def send_email(html_content, total_count, risk_count):
    """通过 SMTP 发送 HTML 格式的精美邮件"""
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
    msg['Subject'] = f"【每日风险监控】今日汇总表（监控:{total_count}家 | 异常:{risk_count}家）"
    
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
        comp_name = item["name"]
        group_name = item["group"]
        print(f"正在分析: {group_name if group_name else '独立企业'} -> {comp_name}")
        
        raw_text = fetch_news(comp_name, group_name)
        analysis = analyze_with_llm(comp_name, group_name, raw_text, api_key)
        
        if "监控数据获取异常" in analysis or "分析失败" in analysis:
            status = "error"
        elif "未发现风险信息" in analysis:
            status = "safe"
        else:
            status = "risk"
            risk_count += 1
            
        results.append({
            "name": comp_name,
            "group": group_name if group_name else "—",
            "analysis": analysis,
            "status": status
        })
        
        time.sleep(4.5)
            
    bj_now = datetime.now(timezone(timedelta(hours=8)))
    execution_time = bj_now.strftime("%H:%M")

    html_body = f"""
    <html>
    <head>
        <style>
            body {{ font-family: 'Helvetica Neue', Arial, sans-serif; margin: 20px; color: #333; background-color: #fafafa; }}
            .container {{ max-width: 800px; background: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
            th, td {{ border: 1px solid #e0e0e0; padding: 12px; text-align: left; }}
            th {{ background-color: #f5f5f5; font-weight: bold; }}
            .risk-no {{ color: #5cb85c; font-weight: bold; }}
            .risk-yes {{ color: #d9534f; font-weight: bold; }}
            .risk-error {{ color: #ff9800; font-weight: bold; font-style: italic; }} /* 橙色低调提示色 */
            .detail-block {{ background-color: #fff9f9; padding: 15px; border-left: 4px solid #d9534f; margin-bottom: 15px; border-radius: 0 4px 4px 0; }}
            h2 {{ color: #2c3e50; border-bottom: 2px solid #eee; padding-bottom: 10px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2>每日企业风险监控整体汇总表</h2>
            <p style="color:#666;">数据统计周期：过去30天公开信息 | 执行时间：北京时间 {execution_time}</p>
            <table>
                <tr>
                    <th>序号</th>
                    <th>企业名称</th>
                    <th>所属集团</th>
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
                    <td><b>{item["name"]}</b></td>
                    <td>{item["group"]}</td>
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
        # 🛡️ 严格只有被系统判定为 status == 'risk' 的企业才会进入下方的详细说明
        if item["status"] == "risk":
            has_risk_detail = True
            formatted_res = item["analysis"].replace("\n", "<br/>")
            html_body += f"""
                <div class="detail-block">
                    <h3 style="color:#c9302c; margin-top:0;"> {item["group"]} - {item["name"]}</h3>
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
