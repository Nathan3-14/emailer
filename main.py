import smtplib
from rich.console import Console
import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

console = Console()

#? Changable Parameters
count = 50
to = "Ethan <ethan.denton@oasisbrislington.org>"
filename = "./email.html"
subject = "Funny Email"

#? Login Info
usrpass = open("./s--usr.pass", "r").readlines()
gmail_user = usrpass[0].strip()
gmail_app_password = usrpass[1].strip()

sent_from = gmail_user
sent_to = to

#? Message Setup
message = MIMEMultipart("alternative")
message["Subject"] = subject
message["From"] = sent_from
message["To"] = sent_to

html = open(filename, "r").read()
part1 = MIMEText(html, "html")
message.attach(part1)

try:
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server. ehlo()
    server.login(gmail_user, gmail_app_password)
    console.print("[bright_green bold]Logged in[/bright_green bold]")
    console.print(f"[bright_yellow]Sending {count} emails to {to}[/bright_yellow]")
    for i in range(count):
        t_start = datetime.datetime.now()
        server.sendmail(sent_from, sent_to, message.as_string())
        t_end = datetime.datetime.now()
        t_dif = t_end - t_start
        console.print(f"[bright_cyan]  Sent email {i+1} out of {count} - took {t_dif.microseconds / 1_000_000}secs[/bright_cyan]")
    server.close()
except Exception as exception:
    console.print("[red]Error: %s[/red]\n\n" % exception)
