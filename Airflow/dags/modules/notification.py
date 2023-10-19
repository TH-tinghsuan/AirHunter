from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import os

def send_noti_email(title, email_content, receiver):
    content = MIMEMultipart() 

    content["subject"] = title
    content["from"] = "airhunter.biz@gmail.com"  #寄件者
    content["to"] = receiver #收件者
    
    content.attach(MIMEText(email_content))

    with smtplib.SMTP(host="smtp.gmail.com", port="587") as smtp:  # 設定SMTP伺服器
        try:
            smtp.ehlo()  # 驗證SMTP伺服器
            smtp.starttls()  # 建立加密傳輸
            smtp.login("airhunter.biz@gmail.com", os.getenv("GOOGLE_EMAIL"))  # 登入寄件者gmail
            smtp.send_message(content)  # 寄送郵件
            print(f"Complete!, email: {receiver}")
        except Exception as e:
            print("Error message: ", e)
