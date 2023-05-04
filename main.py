import os
import requests
import hashlib
import time
import smtplib
import json5
from email.mime.text import MIMEText
from bs4 import BeautifulSoup

path = os.path.join(os.path.dirname(__file__), "config.json5")
with open(path, encoding="utf-8") as fp:
    config = json5.load(fp)
    # print(config)

# 定义需要忽略的时间戳相关字段
ignore_tags = ['script', 'style', 'time']


def post_html(url, data):
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

    response = requests.post(url=url, data=data, headers=header)
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
    message['From'] = config["from_email"]
    message['To'] = config["to_email"]

    smtp = smtplib.SMTP(config["smtp_server"], config["smtp_port"])
    smtp.starttls()
    smtp.login(config["smtp_username"], config["smtp_password"])
    smtp.sendmail(config["from_email"], config["to_email"], message.as_string())
    print("sent email to " + config["to_email"] + " successfully")
    smtp.quit()


def onWebsiteUpdate(website):
    subject = "Website " + website + " updated!"
    body = "The website " + website + " has been updated. Check it out now!"
    if config["send_email_enabled"]:
        send_email(subject, body)


if __name__ == '__main__':
    print("Game Starting")
    while True:
        persistedFilePath = os.path.join(os.path.dirname(__file__), config["persist_target_filename"])
        bool_PersistedFileExist = os.path.exists(persistedFilePath)
        if bool_PersistedFileExist:
            with open(persistedFilePath, encoding="utf-8") as fp:
                persistedResults = json5.load(fp)
                # print(persisted)

        websites = config["websites"]
        # print(websites)
        serialNumber = 0
        for websiteInfo in websites:
            # print(websiteInfo)
            serialNumber += 1
            websiteInfo["serial"] = serialNumber

            try:
                if websiteInfo["method"] == "post":
                    new_hash = hashlib.sha256(post_html(websiteInfo["url"], websiteInfo["data"]).encode()).hexdigest()
                elif websiteInfo["method"] == "get":
                    new_hash = hashlib.sha256(get_html(websiteInfo["url"]).encode()).hexdigest()
                else:
                    print("WARN: Unrecognized method " + websiteInfo["method"])
                    continue
            except Exception as e:
                print("Exception occurred")
                print(str(e))
                continue

            if bool_PersistedFileExist:
                storedHash = ""
                for result in persistedResults:
                    if result["serial"] == websiteInfo["serial"]:
                        storedHash = result["hash"]
                        if storedHash != new_hash:
                            onWebsiteUpdate(websiteInfo["description"])
                            print("Website " + websiteInfo["description"] + " updated!")
                        break
                if storedHash == "":
                    print("ERROR: couldn't find the persisted result")
            websiteInfo["hash"] = new_hash

        newResult = json5.dumps(websites, ensure_ascii=False, indent=4)
        targetPath = os.path.join(os.path.dirname(__file__), config["persist_target_filename"])
        with open(targetPath, 'w', encoding="utf-8") as fp:
            fp.write(newResult)

        # 休眠30分钟，避免过多请求导致被封禁或消耗资源过多
        print("sleep for " + str(config["recalculate_interval_seconds"]) + " seconds......")
        time.sleep(config["recalculate_interval_seconds"])
