import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

class MailSender():

    def send_mail(self, mail_to, filename, newformat):
        ME = ""
        my_password = r""

        msg = MIMEMultipart('alternative')
        msg['Subject'] = filename +"  processed to "+ newformat
        msg['From'] = ME
        msg['To'] = mail_to
        
        message = "Your audio file "+ filename +" has been processed to "+ newformat +" succesfully"
        html = f'<html><body><p>{message}</p></body></html>'
        msg.attach(MIMEText(html, 'html'))

        # Send the message via gmail's regular server, over SSL - passwords are being sent, afterall
        s = smtplib.SMTP_SSL('smtp.gmail.com')
        # uncomment if interested in the actual smtp conversation
        # s.set_debuglevel(1)
        # do the smtp auth; sends ehlo if it hasn't been sent already
        s.login(ME, my_password)
        print(f"Enviando mensaje: {message} to: {mail_to}")
        s.sendmail(ME, mail_to, msg.as_string())
        s.quit()
