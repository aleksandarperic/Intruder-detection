import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# sends email from gmail account
# you need to enable "using unsecure apps for sending email" on your gmail account which will be sender

def main(from_address, with_password, to_address, subject, file_path_with_extension, file_name_with_extension):

    fromaddr = from_address
    toaddr = to_address

    msg = MIMEMultipart()

    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = subject

    body = ""

    msg.attach(MIMEText(body, 'plain'))

    filename = file_name_with_extension
    attachment = open(file_path_with_extension, "rb")

    part = MIMEBase('application', 'octet-stream')
    part.set_payload((attachment).read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition',
                    "attachment; filename= %s" % filename)

    msg.attach(part)

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(fromaddr, with_password)
    text = msg.as_string()
    server.sendmail(fromaddr, toaddr, text)
    server.quit()


if __name__ == '__main__':
    sys.exit(main(sys.argv[1], sys.argv[2]))
