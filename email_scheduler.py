import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import schedule
import time
import ssl
import threading


# Email settings (replace with actual details)
status = 'pending'
finalstatus =''

# Email settings
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465  # SSL port
SENDER_EMAIL = ""
SENDER_PASSWORD = ""
RECIPIENT_EMAIL = ""
EMAIL_SUBJECT = "HRBook- Test mail"


# Function to send email
def send_email(currentstatus,newstatus):
    try:
      msg = MIMEMultipart()
      msg['From'] = SENDER_EMAIL
      msg['To'] = RECIPIENT_EMAIL
      msg['Subject'] = EMAIL_SUBJECT
      EMAIL_BODY = f"The status of the task has changed. Privious Status: {currentstatus} Current status: {newstatus} " 

        # Attach the email body
      msg.attach(MIMEText(EMAIL_BODY, 'plain'))

        # Set up the SSL context and the SMTP server connection
      context = ssl.create_default_context()
      with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, RECIPIENT_EMAIL, msg.as_string())

      print("Email sent successfully!")
    except Exception as e:
        print(f"Error sending email: {e}")

def email_scheduler(currentstatus,newstatus):
  # Simulating a status change. This can be dynamic.
    print('js execution started 1'+ currentstatus+ newstatus);
    # When the status changes, trigger the email sending
    if currentstatus != newstatus:
        print(f"Status changed from {currentstatus} to {newstatus}. Sending email...")
        send_email(currentstatus,newstatus)
        status = newstatus
    else:
        print("No status change.")