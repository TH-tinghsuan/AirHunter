import os
import logging
import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

logging.basicConfig(level=logging.INFO)

def send_noti_email(title: str, email_content: str, receiver: str, is_html=False):
    content = MIMEMultipart() 

    content["subject"] = title
    content["from"] = "airhunter.biz@gmail.com"  #sender
    content["to"] = receiver #receiver
    
    if is_html:
        content.attach(MIMEText(email_content, "html"))
    else:
        content.attach(MIMEText(email_content, "plain"))

    with smtplib.SMTP(host="smtp.gmail.com", port="587") as smtp:  # setup SMTP server
        try:
            smtp.ehlo()  # verify SMTP server
            smtp.starttls()  
            smtp.login("airhunter.biz@gmail.com", os.getenv("GOOGLE_EMAIL"))  # log in sender's gmail
            smtp.send_message(content)  # send email
            logging.info(f"Complete!, email: {receiver}, title: {title}")
        except Exception as e:
            logging.error("Error message: ", e)
