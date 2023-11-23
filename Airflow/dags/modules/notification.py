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

def notify_on_failure(context):
    ti = context['ti']
    task_id = ti.task_id
    dag_id = ti.dag_id
    execution_date = ti.execution_date
    email_content = f"""Hi, 
                        Task ID {task_id} has error. Please check.
                        executed date: {execution_date}
                        dag ID: {dag_id}
                        Thank You."""
    email_subject = f"Airflow notification-task_id: {task_id} error occur."
    send_noti_email(email_subject, email_content, "tinghsuan1998@gmail.com")

def notify_on_success(context):
    ti = context['ti']
    task_id = ti.task_id
    dag_id = ti.dag_id
    execution_date = ti.execution_date
    email_content = f"""Hi, 
                        Task ID {task_id} has successfully executed.
                        executed date: {execution_date}
                        dag ID: {dag_id}
                        Thank You."""
    email_subject = f"Airflow notification-task_id: {task_id} job done."
    send_noti_email(email_subject, email_content, "tinghsuan1998@gmail.com")