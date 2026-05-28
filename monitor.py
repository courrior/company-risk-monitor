import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import urllib.parse
import feedparser
import requests
from datetime import datetime, timedelta, timezone

# ==================== 【企业名单配置区】 ====================
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
# ============================================================

API_URL = "https://models.inference.ai.azure.com/chat/completions"
MODEL_NAME = "gpt-4o-mini"  
def fetch_news(company_name, group_name):
    """利用 Google News RSS 联合抓取企业公开信息，并带上新闻发布时间"""
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
            # 🛡️ 【升级点】：提取新闻在互联网上的标准发布时间
            pub_date = entry.get('published', '未知发布时间')
            articles.append(f"【媒体发布时间】: {pub_date}\n标题: {entry.title}\n摘要: {entry.get('summary', '无')}\n---")
            
        return "\n".join(articles)
    except Exception as e:
        print(f"抓取 {group_name}-{company_name} 失败: {e}")
        return ""

def analyze_with_llm(company_name, group_name, raw_text, api_key):
    """调用大模型进行双时间维度的深度清洗与提炼"""
    if not raw_text.strip():
        return "未发现风险信息"
        
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # 🛡️ 【升级点】：在 Prompt 模版中死磕双时间格式
    prompt = (
        f"你是一个专业的企业风控合规专家。请对以下关于【所属集团：{group_name if group_name else '无'} | 企业名称：{company_name}】的网络搜索结果进行深度清洗与提炼。\n\n"
        f"【原始搜索数据】:\n{raw_text}\n\n"
        "【铁律指令 - 必须严格执行】:\n"
        "1. 必防幻觉铁律：你只能且必须完全基于上方提供的【原始搜索数据】内容进行提炼。绝对不允许编造任何不存在的细节！\n"
        "2. 必须去除所有广告、无关推广和陈旧重复信息。\n"
        "3. 仅保留真实的、近期的风险信息（包括但不限于：财务危机、高管变动、负面舆情、诉讼纠纷、被执行、行政处罚、退市警告等）。\n"
        "4. 如果发现相关风险，请以清晰的列表形式、逐个详细说明。每一条风险必须严格包含以下4个子字段，不得合并或缺失：\n"
        "   - **信息公布时间**: [从原始数据的【媒体发布时间】或正文中提取的新闻曝光时间]\n"
        "   - **风险实际发生时间**: [事件真正发生的年份/月份，或财务数据所属的报告期，如2025年度]\n"
        "   - **起因**: [导致该风险的具体行为、事件或财务数据细节]\n"
        "   - **结果**: [该事件引发的直接后果、法律责任或市场变动]\n"
        "5. 如果没有任何相关的风险或上述变动信息，请【必须且仅】回复这7个字：未发现风险信息。绝对不能带有任何标点符号、解释或多余的文字。"
    )
    
    data = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": "你是一个严格遵守字段格式和真实性指令的AI风控助手。"},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.1
    }
    
    try:
        response = requests.post(API_URL, json=data, headers=headers)
        if response.status_code == 200:
            res_json = response.json()
            if 'choices' in res_json and len(res_json['choices']) > 0:
                return res_json['choices'][0]['message']['content'].strip()
            else:
                return "分析失败（接口未返回有效回答）"
        else:
            return f"分析失败（API状态码:{response.status_code}）"
    except Exception as e:
        return f"分析失败（系统异常:{e}）"

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
        
        is_safe = ("未发现风险信息" in analysis)
        if not is_safe and "分析失败" not in analysis:
            risk_count += 1
            
        results.append({
            "name": comp_name,
            "group": group_name if group_name else "—",
            "analysis": analysis,
            "is_safe": is_safe
        })
            
    # 1. 在 html_body 上方注入时间计算代码
    bj_now = datetime.now(timezone(timedelta(hours=8)))
    execution_time = bj_now.strftime("%H:%M")

    # 2. 替换为动态时间模板
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
            .detail-block {{ background-color: #fff9f9; padding: 15px; border-left: 4px solid #d9534f; margin-bottom: 15px; border-radius: 0 4px 4px 0; }}
            h2 {{ color: #2c3e50; border-bottom: 2px solid #eee; padding-bottom: 10px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2>每日企业风险监控整体汇总表</h2>
            <p style="color:#666;">数据统计周期：过去24小时公开信息 | 执行时间：北京时间 {execution_time}</p>
            <table>
                <tr>
                    <th>序号</th>
                    <th>企业名称</th>
                    <th>所属集团</th>
                    <th>风险监控状态</th>
                </tr>
    """
    
    for idx, item in enumerate(results, 1):
        status_str = "未发现风险信息" if item["is_safe"] else "发现潜在风险/变动"
        status_class = "risk-no" if item["is_safe"] else "risk-yes"
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
        if not item["is_safe"] and "分析失败" not in item["analysis"]:
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
