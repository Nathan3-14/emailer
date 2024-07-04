import json
import smtplib
from rich.console import Console
import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import xmltodict
import dicttoxml
from jsonschema import validate
from jsonschema.exceptions import ValidationError

def _validate(instance, schema) -> bool:
    try:
        validate(instance=instance, schema=schema)
    except ValidationError:
        return False
    return True

console = Console()
print_json = lambda _dict: console.print_json(json.dumps(_dict))

def send_emails(email_name: str, email_address: str, subject: str, file: str="./email.xml", secret_path: str="./s--usr.pass"):
    #? Changable Parameters
    count = 100
    to = f"{email_name} <{email_address}>"
    filename = file
    subject = subject

    #? Login Info
    usrpass = open(secret_path, "r").readlines()
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

def interpret_email(file_path: str):
    email_schema = {
        "type": "object",
        "properties": {
            "email": {
                "type": "object",
                "properties": {
                    "to": {"type": "string"},
                    "subject": {"type": "string"},
                    "html": {"type": "object"},
                    "attachments": {"type": "array"}
                },
                "required": ["to", "html"]
            }
        },
        "required": ["email"]
    }

    with open(file_path, "r") as f:
        email_xml = f.read()
    
    email_dict = xmltodict.parse(email_xml)
    if not _validate(email_dict, email_schema):
        print("Bad Email")
        return
    
    email_dict = email_dict["email"]
    to = email_dict["to"]
    subject = email_dict["subject"]
    html_dict = email_dict["html"]
    html = dicttoxml.dicttoxml(html_dict, custom_root="html")

    print(to)
    print(subject)
    print(html)

    
# interpret_email("./email.xml")
send_emails("Nathan", "nathan.watson@oasisbrislington.org", "trolled", "./email.html")
