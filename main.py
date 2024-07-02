import smtplib
from rich.console import Console
import datetime
from email.mime.multipart import MIMEMultipart

console = Console()

count = 20
# to = "Joseph <josepn.williams@oasisbrislington.org>"
to = "Nathan <nathan.watson.172>@gmail.com"


usrpass = open("./s--usr.pass", "r").readlines()
gmail_user = usrpass[0].strip()
gmail_app_password = usrpass[1].strip()

sent_from = gmail_user
sent_to = to

message = MIMEMultipart("alternative")
message["Subject"] = "multipart test"
message["From"] = sent_from
message["To"] = sent_to

email_text = message
try:
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server. ehlo()
    server.login(gmail_user, gmail_app_password)
    console.print("[bright_green]Logged in[/bright_green]")
    console.print(f"[bright_yellow]Sending {count} emails to {to}[/bright_yellow]")
    for i in range(count):
        t_start = datetime.datetime.now()
        server.sendmail(sent_from, sent_to, email_text)
        t_end = datetime.datetime.now()
        t_dif = t_end - t_start
        console.print(f"[bright_cyan] Sent email {i+1} out of {count} - took {t_dif.microseconds / 1_000_000}secs[/bright_cyan]")
    server.close()
except Exception as exception:
    console.print("Error: %s!\n\n" % exception)
    open("test.html", "w").write(str(exception))