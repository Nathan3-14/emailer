import json
import smtplib
from rich.console import Console
import datetime
import xmltodict
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from jsonschema import validate
from jsonschema.exceptions import ValidationError
import xml.etree.ElementTree as ET
from xml.dom import minidom

console = Console()
print_json = lambda _dict: console.print_json(json.dumps(_dict))

def log(message):
    time = datetime.datetime.now()
    console.print(f"[grey]\[{time.strftime('%H:%M:%S')}\][/grey] {message}")
    

def _validate(instance, schema) -> bool:
    try:
        validate(instance=instance, schema=schema)
    except ValidationError:
        return False
    return True

def send_emails(email_name: str, email_address: str, subject: str, email_content: str | ET.Element="./email.hmtl", secret_path: str="./s--usr.pass", count: int=1):
    #? Changable Parameters
    count = count
    to = f"{email_name} <{email_address}>"
    filename = email_content if type(email_content) == str else None
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

    if filename == None:
        raw_string = ET.tostring(email_content)
        parsed_string = minidom.parseString(raw_string)
        pretty_string = parsed_string.toprettyxml(indent="  ")
        html = "".join([line.strip() for line in pretty_string.split("\n") if line.strip()])
    else:
        html = open(filename, "r").read()
    part1 = MIMEText(html, "html")
    message.attach(part1)

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(gmail_user, gmail_app_password)
        console.log("[bright_green bold]Logged in[/bright_green bold]")
        console.log(f"[bright_yellow]Sending {count} emails to {to}[/bright_yellow]")
        for i in range(count):
            server.sendmail(sent_from, sent_to, message.as_string())
            console.log(f"[bright_cyan]Sent email {i+1} out of {count}[/bright_cyan]")
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
        email_dict = xmltodict.parse(f.read())
    
    email_xml = ET.parse(file_path)
    email_xml_root = email_xml.getroot()
    
    if not _validate(email_dict, email_schema):
        console.log("[red]Email does not fit schema[/red]")
        return

    
    to = email_xml_root.find("to").text
    subject = email_xml_root.find("subject").text
    html = email_xml_root.find("html")

    send_emails("name", to, subject, email_content=html)

    
interpret_email("./email.xml")
# send_emails("Nathan", "nathan.watson@oasisbrislington.org", "Here's 10 emails (not 100)", "./email.html")
