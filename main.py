import os
import requests
import hashlib
import time
import smtplib
import json5
from email.mime.text import MIMEText
from bs4 import BeautifulSoup

# 定义需要监测的使用Get请求的网站列表和对应的哈希值
get_websites = {
    # 'https://pccz.court.gov.cn/pcajxxw/gkaj/gkajxq?id=019BB709472B4921E36A549D1762AFED&lx=999': '',
    # 'https://pccz.court.gov.cn/pcajxxw/gkaj/gkajxq?id=9DEC24DE35F9FE35713AFDF51D687EDB&lx=999': '',
    # 'https://pccz.court.gov.cn/pcajxxw/gkaj/gkajxq?id=222ABB16C416C8B0C4F6A067C78FAB86&lx=999': '',
    # 'https://pccz.court.gov.cn/pcajxxw/gkaj/gkajxq?id=7C99CEFDCDCE8BE5302046D3EA45EDC1&lx=999': '',
    # 'https://pccz.court.gov.cn/pcajxxw/gkaj/gkajxq?id=C1BD4759CD07840CF9098A4D9E36D41C&lx=999': ''
}
# 定义需要监测的使用Post请求的网站列表和对应的哈希值
post_websites = [
    {"url":"https://pccz.court.gov.cn/pcajxxw/gkaj/gkajindex",
     "data":{"lx": 0, "id": "019BB709472B4921E36A549D1762AFED"},
     "hash":""
    },
    {"url":"https://pccz.court.gov.cn/pcajxxw/gkaj/gkajindex","data":{"lx": 0, "id": "9DEC24DE35F9FE35713AFDF51D687EDB"},"hash":""},
    {"url":"https://pccz.court.gov.cn/pcajxxw/gkaj/gkajindex","data":{"lx": 0, "id": "222ABB16C416C8B0C4F6A067C78FAB86"},"hash":""},
    {"url":"https://pccz.court.gov.cn/pcajxxw/gkaj/gkajindex","data":{"lx": 0, "id": "7C99CEFDCDCE8BE5302046D3EA45EDC1"},"hash":""},
    {"url":"https://pccz.court.gov.cn/pcajxxw/gkaj/gkajindex","data":{"lx": 0, "id": "C1BD4759CD07840CF9098A4D9E36D41C"},"hash":""}
]

# 定义需要忽略的时间戳相关字段
ignore_tags = ['script', 'style', 'time']

# 定义发送邮件的参数
smtp_server = 'smtp.263.net'
smtp_port = 25
smtp_username = 'jerry.tan@cilslaw.com'
smtp_password = 'Tht961002'
from_email = 'jerry.tan@cilslaw.com'
to_email = 'haotian.tan@hotmail.com'

def post_html(url,data):
    header = {
        "Accept": "text/html, */*; q=0.01",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Connection": "keep-alive",
        "Content-Length": "40",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        # "Cookie": "JSESSIONID=0329D143588548A6F1FE15FDD7E2888C; wzws_sessionid=gWQ5YzU0NIJkMTBiY2WAMjAyLjEwMS4wLjKgZEXnqw==; pcxxw=5529501c709dbfb32f534d3d4a825990",
        # "Host": "pccz.court.gov.cn",
        # "Origin": "https://pccz.court.gov.cn",
        # "Referer": "https://pccz.court.gov.cn/pcajxxw/gkaj/gkajxq?id=C1BD4759CD07840CF9098A4D9E36D41C&lx=999",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
        "sec-ch-ua-mobile": "?0"
    }

    response = requests.post(url=url,data=data,headers=header)
    soup = BeautifulSoup(response.content, 'html.parser')
    # print(soup)
    # print("*******************************************")
    for tag in ignore_tags:
        [x.extract() for x in soup.findAll(tag)]
    return soup

def get_html(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    # print(soup)
    for tag in ignore_tags:
        [x.extract() for x in soup.findAll(tag)]
    return soup

def send_email(subject, body):
    """发送邮件"""
    message = MIMEText(body)
    message['Subject'] = subject
    message['From'] = from_email
    message['To'] = to_email

    smtp = smtplib.SMTP(smtp_server, smtp_port)
    smtp.starttls()
    smtp.login(smtp_username, smtp_password)
    smtp.sendmail(from_email, to_email, message.as_string())
    smtp.quit()


def onWebsiteUpdate(website):
    subject = "Website {website} updated!"
    body = "The website {website} has been updated. Check it out now!"
    send_email(subject, body)

if __name__ == '__main__':
    print("Game Starting")
    path = os.path.join(os.path.dirname(__file__), 'config.json5')
    with open(path,encoding="utf-8") as fp:
        config = json5.load(fp)
        # print(config)

    test = json5.dumps(config, ensure_ascii=False, indent=4)
    path = os.path.join(os.path.dirname(__file__), 'test.json5')
    with open(path, 'w', encoding="utf-8") as fp:
        fp.write(test)

    while True:
        for websiteInfo, old_hash in get_websites.items():
            try:
                new_hash = hashlib.sha256(get_html(websiteInfo).encode()).hexdigest()
            except Exception as e:
                print("Exception occurred")
                print(str(e))
                continue
            if old_hash == "":
                old_hash = new_hash
                continue
            if old_hash != new_hash:
                get_websites[websiteInfo] = new_hash
                onWebsiteUpdate(websiteInfo)
                print("Website {website} updated!")

        for websiteInfo in post_websites:
            try:
                new_hash = hashlib.sha256(post_html(websiteInfo["url"], websiteInfo["data"]).encode()).hexdigest()
            except Exception as e:
                print("Exception occurred")
                print(str(e))
                continue
            if websiteInfo["hash"] == "":
                websiteInfo["hash"] = new_hash
                continue
            if websiteInfo["hash"] != new_hash:
                websiteInfo["hash"] = new_hash
                onWebsiteUpdate(websiteInfo)
                print("Website {website} updated!")
        time.sleep(60 * 30)
        # 休眠30分钟，避免过多请求导致被封禁或消耗资源过多
        print("sleep")
