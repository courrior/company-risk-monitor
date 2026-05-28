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
    {"name": "北京海博思创科技股份有限公司", "group": ""},
    {"name": "沧州富力城房地产开发有限公司", "group": "广州富力地产股份有限公司"},
    {"name": "沧州盛钰房地产开发有限公司", "group": "荣盛控股股份有限公司"},
    {"name": "沧州旭阳化工有限公司", "group": "旭阳集团有限公司"},
    {"name": "沧州中铁装备制造材料有限公司", "group": "河北新华联合冶金控股集团有限公司"},
    {"name": "承德建龙特殊钢有限公司", "group": "北京建龙重工集团有限公司"},
    {"name": "承德燕北冶金材料有限公司", "group": "北京建龙重工集团有限公司"},
    {"name": "海伟石化有限公司", "group": ""},
    {"name": "邯郸正大制管集团股份有限公司", "group": "邯郸正大制管集团股份有限公司"},
    {"name": "河北诚实实业集团有限公司", "group": "河北诚实实业集团有限公司"},
    {"name": "河北华荣制药有限公司", "group": "石药控股集团有限公司"},
    {"name": "河北敬业高品钢科技有限公司", "group": "敬业集团有限公司"},
    {"name": "河北敬业宽板科技有限公司", "group": "敬业集团有限公司"},
    {"name": "河北千喜鹤饮食股份有限公司", "group": "河北千喜鹤饮食股份有限公司"},
    {"name": "河北新武安钢铁集团烘熔钢铁有限公司", "group": "河北普阳钢铁有限公司"},
    {"name": "河北旭阳能源有限公司", "group": "旭阳集团有限公司"},
    {"name": "华夏幸福基业控股股份公司", "group": "华夏幸福基业股份有限公司"},
    {"name": "今麦郎饮品股份有限公司", "group": "今麦郎投资有限公司"},
    {"name": "敬业钢铁有限公司", "group": "敬业集团有限公司"},
    {"name": "廊坊市铭顺石油天然气销售有限公司", "group": "廊坊市铭顺石油天然气销售有限公司"},
    {"name": "廊坊市天然气有限公司", "group": "廊坊市天然气有限公司"},
    {"name": "内蒙古翔福新能源有限责任公司", "group": "旭阳集团有限公司"},
    {"name": "迁安正大通用钢管有限公司", "group": "邯郸正大制管集团股份有限公司"},
    {"name": "荣盛房地产发展股份有限公司", "group": "荣盛控股股份有限公司"},
    {"name": "三河汇福粮油集团精炼植物油有限公司", "group": "三河汇福粮油集团有限公司"},
    {"name": "石药集团恩必普药业有限公司", "group": "石药控股集团有限公司"},
    {"name": "唐山班公措新材料有限公司", "group": ""},
    {"name": "唐山创齐贸易有限公司", "group": ""},
    {"name": "唐山市丰南区万丰制管有限公司", "group": ""},
    {"name": "唐山市格萨贸易有限公司", "group": "唐山市格萨贸易有限公司"},
    {"name": "唐山旭阳化工有限公司", "group": "旭阳集团有限公司"},
    {"name": "天津津衡石油化工贸易有限责任公司", "group": ""},
    {"name": "武安市裕华钢铁有限公司", "group": "冀南钢铁集团有限公司"},
    {"name": "辛集市澳森金属制品有限公司", "group": "辛集市澳森特钢集团有限公司"},
    {"name": "辛集市澳森特钢集团有限公司", "group": "辛集市澳森特钢集团有限公司"},
    {"name": "辛集市泽明国际贸易有限公司", "group": ""},
    {"name": "新奥控股投资股份有限公司", "group": "廊坊市天然气有限公司"},
    {"name": "新奥能源供应链有限公司", "group": "廊坊市天然气有限公司"},
    {"name": "浙江银盾云科技有限公司", "group": "京津冀润泽（廊坊）数字信息有限公司"},
    {"name": "正大(天津)供应链有限公司", "group": "邯郸正大制管集团股份有限公司"},
    {"name": "知合控股有限公司", "group": "华夏幸福基业股份有限公司"},
    {"name": "中海外交通建设有限公司", "group": ""}
]
# ============================================================

API_URL = "https://models.inference.ai.azure.com/chat/completions"
MODEL_NAME = "gpt-4o-mini"  
def fetch_news(company_name, group_name):
    """利用 Google News RSS 联合抓取企业公开信息"""
    keywords = "(风险 OR 诉讼 OR 处罚 OR 违规 OR 财务 OR 执行 OR 舆情)"
    if group_name and group_name.strip():
        query = f"({company_name} OR {group_name}) {keywords} when:1d" 
    else:
        query = f"{company_name} {keywords} when:1d"
        
    encoded_query = urllib.parse.quote(query)
    url = f"https://news.google.com/rss/search?q={encoded_query}&hl=zh-CN&gl=CN&ceid=CN:zh-Hans"
    
    try:
        feed = feedparser.parse(url)
        articles = []
        for entry in feed.entries[:15]:
            articles.append(f"标题: {entry.title}\n摘要: {entry.get('summary', '无')}\n---")
        return "\n".join(articles)
    except Exception as e:
        print(f"抓取 {group_name}-{company_name} 失败: {e}")
        return ""

def analyze_with_llm(company_name, group_name, raw_text, api_key):
    """调用 GitHub 免费大模型进行提炼分析，严格执行防幻觉铁律"""
    if not raw_text.strip():
        return "未发现风险信息"
        
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    prompt = (
        f"你是一个专业的企业风控合规专家。请对以下关于【所属集团：{group_name if group_name else '无'} | 企业名称：{company_name}】在过去24小时内的网络搜索结果进行深度清洗与提炼。\n\n"
        f"【原始搜索数据】:\n{raw_text}\n\n"
        "【铁律指令 - 必须严格执行】:\n"
        "1. 必防幻觉铁律：你只能且必须完全基于上方提供的【原始搜索数据】内容进行提炼。绝对不允许编造、猜测、臆断任何不存在的日期、金额、罪名、受罚原因或事件细节！如果原文语焉不详，宁可不写，也绝不能凭空想象。\n"
        "2. 必须去除所有广告、无关推广、重复内容和陈旧历史信息（非过去24小时内的新闻）。\n"
        "3. 仅保留真实的、属于过去一个月内的风险信息（包括但不限于：财务危机、高管变动、负面舆情、诉讼纠纷、被执行、行政处罚、违规行为等）。\n"
        "4. 如果发现相关风险，请以清晰的列表形式、逐个详细说明事件的时间、起因和结果。\n"
        "5. 如果没有任何相关的风险或上述变动信息（或者搜索到的内容纯属无关推广），请【必须且仅】回复这7个字：未发现风险信息。绝对不能带有任何标点符号、解释或多余的文字。"
    )
    
    data = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": "你是一个严格遵守字数和真实性指令的AI助手。"},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.1
    }
    
    try:
        response = requests.post(API_URL, json=data, headers=headers)
        if response.status_code == 200:
            res_json = response.json()
            # 🛡️ 防御性排查：确保返回的数据里确实包含 choices 键，防止接口抽风导致脚本卡死
            if 'choices' in res_json and len(res_json['choices']) > 0:
                return res_json['choices'][0]['message']['content'].strip()
            else:
                print(f"警告：AI接口返回了异常格式: {res_json}")
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
