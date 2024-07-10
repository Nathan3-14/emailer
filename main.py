from codecs import replace_errors
import json
import csv
# import tqdm
import os
import smtplib
from pyparsing import delimited_list
from rich.console import Console
import datetime
import xmltodict
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from jsonschema import validate
from jsonschema.exceptions import ValidationError
import xml.etree.ElementTree as ET
from xml.dom import minidom
from xml.parsers.expat import ExpatError
from xml.etree.ElementTree import ParseError
import sys

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

def send_email(to_email: str, subject: str, email_content: ET.Element, csv_path: str, secret_path: str="./s--usr.pass"):
    to = f"<{to_email}>"
    subject = subject
    content = email_content
    secret_path = secret_path
    csv_path = csv_path
    with open(csv_path) as csv_file:
        csv_reader =csv.reader(csv_file, delimiter=",")

        replaces = {}
        for line_index, row in enumerate(csv_reader):
            if line_index == 0:
                for property in row:
                    replaces[property] = ""
            else:
                for i, property in enumerate(list(replaces.keys())):
                    replaces[property] = row[i]
            print(replaces)

    #? Login Info
    usrpass = open(secret_path, "r").readlines()
    gmail_user = usrpass[0].strip()
    gmail_app_password = usrpass[1].strip()

    sent_from = gmail_user
    sent_to = to

    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = sent_from
    message["To"] = sent_to

    raw_string = ET.tostring(content)
    parsed_string = minidom.parseString(raw_string)
    pretty_string = parsed_string.toprettyxml(indent="  ")
    content_html = "".join([line.strip() for line in pretty_string.split("\n") if line.strip()])
    

    message.attach(MIMEText(content_html, "html"))
    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(gmail_user, gmail_app_password)
        console.log("[bright_green bold]Logged in[/bright_green bold]")
        server.sendmail(sent_from, sent_to, message.as_string())
        console.log(f"[bright_cyan]Sent email to {to}[/bright_cyan]")
        server.close()
    except Exception as exception:
        console.print("[red]Error: %s[/red]\n\n" % exception)

# def send_emails(email_name: str, email_address: str, subject: str, email_content: str | ET.Element="./email.hmtl", secret_path: str="./s--usr.pass", count: int=1):
#     #? Changable Parameters
#     count = count
#     to = f"{email_name} <{email_address}>"
#     filename = email_content if type(email_content) == str else None
#     subject = subject

#     #? Login Info
#     usrpass = open(secret_path, "r").readlines()
#     gmail_user = usrpass[0].strip()
#     gmail_app_password = usrpass[1].strip()

#     sent_from = gmail_user
#     sent_to = to

#     #? Message Setup
#     message = MIMEMultipart("alternative")
#     message["Subject"] = subject
#     message["From"] = sent_from
#     message["To"] = sent_to

#     if filename == None:
#         raw_string = ET.tostring(email_content)
#         parsed_string = minidom.parseString(raw_string)
#         pretty_string = parsed_string.toprettyxml(indent="  ")
#         html = "".join([line.strip() for line in pretty_string.split("\n") if line.strip()])
#     else:
#         html = open(filename, "r").read()
#     part1 = MIMEText(html, "html")
#     message.attach(part1)

#     try:
#         server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
#         server.ehlo()
#         server.login(gmail_user, gmail_app_password)
#         console.log("[bright_green bold]Logged in[/bright_green bold]")
#         console.log(f"[bright_yellow]Sending {count} emails to {to}[/bright_yellow]")
#         for i in tqdm.tqdm(range(count)):
#             server.sendmail(sent_from, sent_to, message.as_string())
#             console.log(f"[bright_cyan]Sent email {i+1} out of {count}[/bright_cyan]")
#         server.close()
#     except Exception as exception:
#         console.print("[red]Error: %s[/red]\n\n" % exception)

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
        try:
            email_dict = xmltodict.parse(f.read())
            dict_errored = False
        except ExpatError:
            console.log("[red]Error while parsing xml, cannot convert to dict")
            dict_errored = True
    
    try:
        email_xml = ET.parse(file_path)
    except ParseError as e:
        console.log("[red][bold]FATAL[/bold] - Error while parsing xml, cannot get tree[/red]")
        console.log(f"[dark_red]{e}[/dark_red]")
        quit()
    email_xml_root = email_xml.getroot()
        
    if not dict_errored:
        if not _validate(email_dict, email_schema):
            console.log("[red]Email does not fit schema[/red]")
            return

    
    to = email_xml_root.find("to").text
    subject = email_xml_root.find("subject").text
    html = email_xml_root.find("html")

    send_emails("name", to, subject, email_content=html, count=5) #? Change this value to change the number of emails sent


def interpret_email2(email_path: str):
    email_schema = {
        "type": "object",
        "properties": {
            "email": {
                "type": "object",
                "properties": {
                    "subject": {"type": "string"},
                    "html": {"type": "object"},
                    "data": {"type": "string"},
                    "attachments": {"type": "array"}
                },
                "required": ["subject", "html"]
            }
        },
        "required": ["email"]
    }

    with open(email_path, "r") as f:
        try:
            email_dict = xmltodict.parse(f.read())
            dict_errored = False
        except ExpatError:
            console.log("[red]Error while parsing xml, cannot convert to dict")
            dict_errored = True
    
    try:
        email_xml = ET.parse(email_path)
    except ParseError as e:
        console.log("[red][bold]FATAL[/bold] - Error while parsing xml, cannot get tree[/red]")
        console.log(f"[dark_red]{e}[/dark_red]")
        quit()
    email_xml_root = email_xml.getroot()
        
    if not dict_errored:
        if not _validate(email_dict, email_schema):
            console.log("[red][bold]FATAL[/bold] - Email does not fit schema[/red]")
            return
        console.log("[bright_cyan]Email validated, continuing[/bright_cyan]")
    else:
        console.log("[bright_cyan]Email failed to validate, continuing anyway[/bright_cyan]")
    
    csv = email_xml_root.find("data")
    csv_path = None if csv == None else csv.text
    subject = email_xml_root.find("subject").text
    html = email_xml_root.find("html")

    send_email("nathan.watson@oasisbrislington.org", subject, html, csv_path=csv_path)


    
# interpret_email("./email.xml")
# send_emails("Nathan", "nathan.watson@oasisbrislington.org", "Here's 10 emails (not 100)", "./email.html")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        console.log(f"[red]Incorrect arguments supplied. Expected [/red][bright_cyan]main.py <path>[/bright_cyan][red], recieved [/red][bright_cyan]{''.join(sys.argv)}[/bright_cyan][red][/red]")
        quit()
    else:
        path = os.path.normpath(f"{os.getcwd()}/{sys.argv[1]}")
        if not os.path.exists(path):
            console.log(f"[red]Incorrect arguments supplied. [/red][bright_cyan]{path}[/bright_cyan][red] is not a valid path[/red]")
            quit()
        # interpret_email(path)
        interpret_email2(path)
