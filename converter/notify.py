import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

class MailNotificator():

    def send_mail(self, mail_to, message):
        ME = ""
        my_password = r""

        msg = MIMEMultipart('alternative')
        msg['Subject'] = "Alerta"
        msg['From'] = ME
        msg['To'] = mail_to
        
        html = f'<html><body><p>{message}</p></body></html>'
        part2 = MIMEText(html, 'html')

        msg.attach(part2)

        # Send the message via gmail's regular server, over SSL - passwords are being sent, afterall
        s = smtplib.SMTP_SSL('smtp.gmail.com')
        # uncomment if interested in the actual smtp conversation
        # s.set_debuglevel(1)
        # do the smtp auth; sends ehlo if it hasn't been sent already
        s.login(ME, my_password)
        print(f"Enviando mensaje: {message} to: {mail_to}")
        s.sendmail(ME, mail_to, msg.as_string())
        s.quit()