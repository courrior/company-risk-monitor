import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import urllib.parse
import feedparser
import requests
from datetime import datetime, timedelta, timezone
import time  # 🛡️ 严格控制请求频率，消灭接口限流

# ==================== 【企业名单配置区】 ====================
# name/group 用于后台模糊搜索（高召回防漏）；full_name/group_full 用于邮件规范显示（正式严谨）
COMPANIES = [
    {"name": "海博思创", "full_name": "北京海博思创科技股份有限公司", "group": "", "group_full": "—"},
    {"name": "富力城", "full_name": "富力城房地产开发有限公司", "group": "富力", "group_full": "富力集团"},
    {"name": "盛钰", "full_name": "荣盛集团旗下盛钰相关主体", "group": "荣盛", "group_full": "荣盛控股股份有限公司"},
    {"name": "旭阳化工", "full_name": "旭阳化工有限公司", "group": "旭阳", "group_full": "中国旭阳集团"},
    {"name": "中铁装备", "full_name": "中铁工程装备集团有限公司", "group": "新华联合冶金", "group_full": "新华联合冶金控股集团"},
    {"name": "承德建龙", "full_name": "承德建龙特殊钢有限公司", "group": "建龙", "group_full": "建龙重工集团"},
    {"name": "燕北冶金", "full_name": "承德燕北冶金材料有限公司", "group": "建龙", "group_full": "建龙重工集团"},
    {"name": "海伟石化", "full_name": "海伟交通设施集团石化有限公司", "group": "", "group_full": "—"},
    {"name": "正大制管", "full_name": "邯郸正大制管集团股份有限公司", "group": "正大制管", "group_full": "正大制管集团"},
    {"name": "诚实实业", "full_name": "诚实实业集团有限公司", "group": "诚实", "group_full": "诚实集团"},
    {"name": "华荣制药", "full_name": "石药集团华荣制药有限公司", "group": "石药", "group_full": "石药控股集团有限公司"},
    {"name": "敬业高品钢", "full_name": "河北敬业高品钢科技有限公司", "group": "敬业", "group_full": "敬业集团有限公司"},
    {"name": "敬业宽板", "full_name": "乌兰浩特钢铁有限责任公司宽厚板厂", "group": "敬业", "group_full": "敬业集团有限公司"},
    {"name": "千喜鹤饮食", "full_name": "千喜鹤饮食股份有限公司", "group": "千喜鹤", "group_full": "千喜鹤集团"},
    {"name": "新武安钢铁", "full_name": "武安市新武安钢铁集团有限公司", "group": "普阳钢铁", "group_full": "河北普阳钢铁集团"},
    {"name": "旭阳能源", "full_name": "定州旭阳能源有限公司", "group": "旭阳", "group_full": "中国旭阳集团"},
    {"name": "华夏幸福基业控股", "full_name": "华夏幸福基业控股股份公司", "group": "华夏幸福", "group_full": "华夏幸福"},
    {"name": "今麦郎饮品", "full_name": "今麦郎饮品股份有限公司", "group": "今麦郎", "group_full": "今麦郎食品股份有限公司"},
    {"name": "敬业钢铁", "full_name": "敬业钢铁有限公司", "group": "敬业", "group_full": "敬业集团有限公司"},
    {"name": "铭顺石油天然气", "full_name": "铭顺石油天然气销售有限公司", "group": "铭顺", "group_full": "铭顺集团"},
    {"name": "廊坊市天然气", "full_name": "廊坊市天然气有限公司", "group": "廊坊市天然气", "group_full": "廊坊市天然气集团"},
    {"name": "翔福新能源", "full_name": "河北翔福新能源有限责任公司", "group": "旭阳", "group_full": "中国旭阳集团"},
    {"name": "迁安正大", "full_name": "迁安正大通用钢管有限公司", "group": "正大制管", "group_full": "正大制管集团"},
    {"name": "荣盛房地产", "full_name": "荣盛房地产发展股份有限公司", "group": "荣盛", "group_full": "荣盛控股股份有限公司"},
    {"name": "三河汇福粮油集团精炼植物油", "full_name": "三河汇福粮油集团精炼植物油有限公司", "group": "三河汇福", "group_full": "三河汇福粮油集团"},
    {"name": "恩必普", "full_name": "石药集团恩必普药业有限公司", "group": "石药", "group_full": "石药控股集团有限公司"},
    {"name": "班公措", "full_name": "班公措相关贸易主体", "group": "", "group_full": "—"},
    {"name": "创齐贸易", "full_name": "创齐贸易有限公司", "group": "", "group_full": "—"},
    {"name": "万丰制管", "full_name": "万丰制管有限公司", "group": "", "group_full": "—"},
    {"name": "格萨贸易", "full_name": "格萨贸易有限公司", "group": "格萨", "group_full": "格萨集团"},
    {"name": "旭阳化工", "full_name": "沧州旭阳化工有限公司", "group": "旭阳", "group_full": "中国旭阳集团"},
    {"name": "津衡石油化工", "full_name": "津衡石油化工有限公司", "group": "", "group_full": "—"},
    {"name": "武安市裕华钢铁", "full_name": "武安市裕华钢铁有限公司", "group": "冀南钢铁", "group_full": "冀南钢铁集团"},
    {"name": "澳森金属", "full_name": "辛集市澳森金属制品有限公司", "group": "澳森特钢", "group_full": "河北澳森特钢集团"},
    {"name": "澳森特钢", "full_name": "河北澳森特钢集团有限公司", "group": "澳森特钢", "group_full": "河北澳森特钢集团"},
    {"name": "泽明国际", "full_name": "泽明国际贸易有限公司", "group": "", "group_full": "—"},
    {"name": "新奥控股", "full_name": "新奥控股投资股份有限公司", "group": "廊坊市天然气", "group_full": "新奥集团"},
    {"name": "新奥能源", "full_name": "新奥能源控股有限公司", "group": "廊坊市天然气", "group_full": "新奥集团"},
    {"name": "银盾云", "full_name": "银盾云数据中心有限公司", "group": "润泽", "group_full": "润泽科技"},
    {"name": "正大(天津)供应链", "full_name": "正大(天津)供应链管理有限公司", "group": "正大制管", "group_full": "正大制管集团"},
    {"name": "知合", "full_name": "知合控股有限公司", "group": "华夏幸福", "group_full": "华夏幸福"},
    {"name": "中海外", "full_name": "中国海外工程有限责任公司", "group": "", "group_full": "—"}
]
# ==================================================================================

API_URL = "https://models.inference.ai.azure.com/chat/completions"
MODEL_NAME = "gpt-4o-mini"  

def fetch_news(company_short, group_short):
    """进行清洗加固后的搜索，防御词义污染，确保轻量表达式100%被引擎解析"""
    
    # 🛡️【重大升级 1】：自动对短简称加固。防止“爱岗敬业”、“做人诚实”等社会高频词造成严重的噪音海啸
    c_search = company_short
    g_search = group_short
    
    if g_search and len(g_search) <= 2 and not g_search.endswith("集团"):
        g_search = f"{g_search}集团"
        
    # 🛡️【重大升级 2】：精炼核心风控词（降低表达式长度），确保 Google News RSS 引擎不产生解析 Bug
    keywords_str = "(风险 OR 处罚 OR 通报 OR 违规 OR 诉讼 OR 执行)"
    
    if g_search and g_search.strip():
        query = f"({c_search} OR {g_search}) {keywords_str} when:30d" 
    else:
        query = f"{c_search} {keywords_str} when:30d"
        
    encoded_query = urllib.parse.quote(query)
    url = f"https://news.google.com/rss/search?q={encoded_query}&hl=zh-CN&gl=CN&ceid=CN:zh-Hans"
    
    try:
        feed = feedparser.parse(url)
        articles = []
        seen_titles = set()  
        
        print(f"   [安全检索] 正在使用清洁词检索: '{query}' | 原始抓取: {len(feed.entries)} 条")
        
        for entry in feed.entries:
            title = entry.title.strip()
            if title in seen_titles:
                continue
            seen_titles.add(title)
            
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
            
            if len(articles) >= 40:
                break
            
        return "\n".join(articles)
    except Exception as e:
        print(f"抓取 {company_short} 失败: {e}")
        return ""

def analyze_with_llm(company_full, group_full, raw_text, api_key):
    """大模型结合官方全称进行精准事实过滤与清洗"""
    if not raw_text.strip():
        return "未发现风险信息"
        
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    prompt = (
        f"你是一个专业的企业风控合规数据清洗工具。请对以下关于【所属集团官方全称：{group_full} | 企业官方全称：{company_full}】的网络搜索结果进行清洗与结构化提炼。\n\n"
        f"【原始搜索数据】:\n{raw_text}\n\n"
        "【铁律指令 - 必须严格执行】:\n"
        "1. 必防幻觉铁律：你只能且必须完全基于上方提供的【原始搜索数据】内容进行提炼。绝对不允许编造、臆断任何不存在的细节！\n"
        "2. 绝对中立铁律：【完全不需要】进行任何原因分析、后果预测、或主观定性（严禁出现“说明财务恶化”、“面临危机”、“提醒注意”等AI主观评价）。完全真实、客观地还原新闻提及的事实本身。\n"
        "3. 拒绝过度总结：保留原始数据中关键的时间、具体的涉案金额、具体的违规缘由、公告编号等核心事实细节，【严禁】将详细过程压缩、抽象成一句话。\n"
        "4. 如果发现风险或变动，请以清晰的列表形式说明。每一条必须严格且仅包含以下4个子字段，不得合并、缺失或自行增加其他字段（严禁出现“起因”、“结果”等）：\n"
        "   - 风险主体: [必须写出原始数据中该事件直接指向的企业或集团的工商完整名称]\n"
        "   - 风险信息公布时间: [直接使用原始数据中提供的【媒体发布时间】]\n"
        "   - 风险信息发生时间: [事件真正发生的具体日期、年份、月份]\n"
        "   - 风险详细内容: [明确交代哪个主体在什么背景下发生了什么事。详尽还原原始事实细节，包含涉及的涉诉、舆情信息、业务、涉案具体金额或违规事项，不作任何AI的二次加工和延伸解释]\n"
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
                print(f"   [重试提示] 触发官方频率限制(429)，正在静默等待15秒...")
                time.sleep(15)
                continue
            else:
                time.sleep(5)
                continue
        except Exception as e:
            time.sleep(5)
            continue
            
    return "监控数据获取异常（请稍后重新运行触发）"

def send_email(html_content, total_count, risk_count):
    """通过 SMTP 发送 HTML 格式的邮件"""
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
        
        # 🛡️ 每次请求后制动 4.5 秒，稳定绕过 GitHub 15 RPM 限制
        time.sleep(4.5)
            
    bj_now = datetime.now(timezone(timedelta(hours=8)))
    execution_time = bj_now.strftime("%H:%M")

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
            <p style="color:#666;">数据统计周期：过去30天公开信息 | 执行时间：北京时间 {execution_time}</p>
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
