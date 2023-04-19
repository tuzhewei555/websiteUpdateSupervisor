import requests
import hashlib
import time
import smtplib
from email.mime.text import MIMEText
from bs4 import BeautifulSoup

# 定义需要监测的网站列表和对应的哈希值
websites = {
    'https://pccz.court.gov.cn/pcajxxw/gkaj/gkajxq?id=019BB709472B4921E36A549D1762AFED&lx=999': '',
    'https://pccz.court.gov.cn/pcajxxw/gkaj/gkajxq?id=9DEC24DE35F9FE35713AFDF51D687EDB&lx=999': '',
    'https://pccz.court.gov.cn/pcajxxw/gkaj/gkajxq?id=222ABB16C416C8B0C4F6A067C78FAB86&lx=999': '',
    'https://pccz.court.gov.cn/pcajxxw/gkaj/gkajxq?id=7C99CEFDCDCE8BE5302046D3EA45EDC1&lx=999': '',
    'https://pccz.court.gov.cn/pcajxxw/gkaj/gkajxq?id=C1BD4759CD07840CF9098A4D9E36D41C&lx=999': ''
}

# 定义需要忽略的时间戳相关字段
ignore_tags = ['script', 'style', 'time']

# 定义发送邮件的参数
smtp_server = 'smtp.263.net'
smtp_port = 25
smtp_username = 'jerry.tan@cilslaw.com'
smtp_password = 'Tht961002'
from_email = 'jerry.tan@cilslaw.com'
to_email = 'haotian.tan@hotmail.com'


def get_html_hash(url):
    """计算网页内容的哈希值"""
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    for tag in ignore_tags:
        [x.extract() for x in soup.findAll(tag)]
    return hashlib.sha256(soup.encode()).hexdigest()


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


if __name__ == '__main__':
    print("Game Starting")
    while True:
        for website, old_hash in websites.items():
            try:
                new_hash = get_html_hash(website)
            except Exception as e:
                print("Exception occurred")
                print(str(e))
                continue
            if old_hash == "":
                old_hash = new_hash
                continue
            if old_hash != new_hash:
                websites[website] = new_hash
                subject = "Website {website} updated!"
                body = "The website {website} has been updated. Check it out now!"
                print("The website {"+website+"} has been updated.")
                send_email(subject, body)
                print("Website {website} updated!")
        time.sleep(60 * 30)
        # 休眠30分钟，避免过多请求导致被封禁或消耗资源过多
        print("sleep")
