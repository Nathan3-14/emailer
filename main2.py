from rich.console import Console
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from jsonschema import validate
from jsonschema.exceptions import ValidationError
import xml.etree.ElementTree as ET
from xml.dom import minidom
from xml.parsers.expat import ExpatError
from xml.etree.ElementTree import ParseError
import xmltodict
import sys
import os
import csv
from typing import Dict

console = Console()


def _validate(instance, schema) -> bool:
    try:
        validate(instance=instance, schema=schema)
    except ValidationError:
        return False
    return True


def send_email(to: str, subject: str, html_content: str, secret_path: str="s--usr.pass"):
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

    message.attach(MIMEText(html_content, "html"))
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


def replace_html(html_xml: ET.Element, replace: Dict[str, str]):
    html_string = ET.tostring(html_xml, encoding='unicode')
    
    for replace_phrase, replace_value in replace.items():
        html_string = html_string.replace(f"<r>{replace_phrase}</r>", replace_value) #? isnt actually a string???
    
    return html_string


def interpret_email_file(file_path: str):
    email_schema = {
        "type": "object",
        "properties": {
            "email": {
                "type": "object",
                "properties": {
                    "subject": {"type": "string"},
                    "html": {"type": "object"},
                    # "attachments": {"type": "array"}
                },
                "required": ["subject", "html"]
            },
            "data": {"type": "string"}
        },
        "required": ["email"]
    }

    #* Validate File *#
    with open(file_path, "r") as f:
        try:
            email_dict = xmltodict.parse(f.read())
            if not _validate(email_dict, email_schema):
                console.log("[red][bold]FATAL[/bold] - Email does not fit schema[/red]")
                quit()
        except ExpatError:
            console.log("[red]Error while parsing xml, cannot convert to dict, cannot validate[/red]")
    
    #* Convert to xml *#
    try:
        email_xml = ET.parse(file_path)
    except ParseError as e:
        console.log("[red][bold]FATAL[/bold] - Error while parsing xml, cannot get tree[/red]")
        console.log(f"[dark_red]{e}[/dark_red]")
        quit()
    email_xml_root = email_xml.getroot()
    
    #* Load CSV *#
    send_to_list = []

    csv_path = email_xml_root.find("data").text
    with open(csv_path) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=",")

        replaces = {}
        for line_index, row in enumerate(csv_reader):
            if line_index == 0:
                for property in row:
                    replaces[property] = ""
            else:
                for i, property in enumerate(list(replaces.keys())):
                    replaces[property] = row[i]
            send_to_list.append(replaces)
            console.log(f"[red]replaces added, is now [/red]{send_to_list}")

    subject = email_xml_root.find("subject").text
    html = email_xml_root.find("html")

    console.print(send_to_list)
    for data in send_to_list:
        try:
            to_name = data["name"]
            to_email = data["email"]
        except KeyError:
            console.log("[red][bold]FATAL[/bold] - No name or email present in csv file")
        
        console.log(f"[bright_cyan]Sending email to {to_email}[/bright_cyan]")
        # send_email(to_email, subject, replace_html(html, data))



if __name__ == "__main__":
    def incorrect_arguments_error():
        console.log(f"[red][bold]FATAL[/bold] - Incorrect arguments supplied, expected 'main.py <path: str>', recieved '{''.join(sys.argv)}[/red]")
        quit()

    if len(sys.argv) < 2:
        incorrect_arguments_error()
    
    xml_path = sys.argv[1]
    if not os.path.exists(xml_path):
        incorrect_arguments_error()
    
    interpret_email_file(xml_path)
