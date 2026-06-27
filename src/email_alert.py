import config
import smtplib
from email.message import EmailMessage

PATHS = config.PATHS

# Function to build and send the email of the price alerts
# Pulls all the parameters from the config file except the main message/body of the email
def sendEmail():
    msg = EmailMessage()

    with open(PATHS["flight_alert"], "r") as f:
        message = f.read()
        
    if message.strip():     # Check if message/file is empty or not
        msg["From"] = config.FROM_EMAIL
        msg["To"] = config.TO_EMAIL
        msg["Subject"] = config.EMAIL_SUBJECT
        msg.set_content(message)
        
        with smtplib.SMTP(config.SMTP_SERVER, config.SMTP_PORT) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(config.FROM_EMAIL, config.EMAIL_PASSWORD)
            server.send_message(msg)
        
            print("Email has been sent to " + config.TO_EMAIL)
    else:
        print("File was empty, didn't send email")
    # Clear file once email is sent
    open(PATHS["flight_alert"], "w").close()