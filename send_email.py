# -*- coding: utf-8 -*-
"""
Created on Mon May 10 16:10:05 2021

@author: ZZ03MG668
"""
    
import smtplib, ssl
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import date
import re

def send_email_with_recommendations(receiver_email, tracker_id, district, links):
    
    sender_email = "realquik@seznam.cz"
    password = 'R34lquik'
    today = date.today().strftime("%d/%m/%Y")
        
    message = MIMEMultipart("alternative")
    message["Subject"] = f"{today}: Podceněné byty v {district} na základě hlídacího psa číslo {tracker_id}"
    message["From"] = sender_email
    message["To"] = receiver_email   
    
    link1 = str(links[0]) if len(links) > 0 else ""
    link2 = str(links[1]) if len(links) > 1 else ""
    link3 = str(links[2]) if len(links) > 2 else ""
    link4 = str(links[3]) if len(links) > 3 else ""
    link5 = str(links[4]) if len(links) > 4 else ""

    link1page = re.search(r'(?:https:\/\/)([\w.-]*)', link1).group(1) if re.search(r'(?:https:\/\/)([\w.-]*)', link1) is not None else ''
    link2page = re.search(r'(?:https:\/\/)([\w.-]*)', link2).group(1) if re.search(r'(?:https:\/\/)([\w.-]*)', link2) is not None else ''
    link3page = re.search(r'(?:https:\/\/)([\w.-]*)', link3).group(1) if re.search(r'(?:https:\/\/)([\w.-]*)', link3) is not None else ''
    link4page = re.search(r'(?:https:\/\/)([\w.-]*)', link4).group(1) if re.search(r'(?:https:\/\/)([\w.-]*)', link4) is not None else ''
    link5page = re.search(r'(?:https:\/\/)([\w.-]*)', link5).group(1) if re.search(r'(?:https:\/\/)([\w.-]*)', link5) is not None else ''
    
    html = f"""<html>
                <body>
                    <p>Dobrý den,</p><br>
                    <p>na základě vašeho hlídacího psa {tracker_id} vám posíláme následující byty ve vámi zadané lokalitě {district}, které
                    {today} náš systém vyhodnotil jako pravděpodobně podceněné.</p>
                    <ul>
                       <li><a href="{link1}">Byt 1 ({link1page})</a></li>
                       <li><a href="{link2}">Byt 2 ({link2page})</a></li>
                       <li><a href="{link3}">Byt 3 ({link3page})</a></li>
                       <li><a href="{link4}">Byt 4 ({link4page})</a></li>
                       <li><a href="{link5}">Byt 5 ({link5page})</a></li>
                    </ul>
                    <p>Hezký zbytek dne přeje,</p><br>
                    <p>RealQuik</p>
                </body>
            </html>
            """

    
    # Turn these into plain/html MIMEText objects
    part2 = MIMEText(html, "html")
    
    # Add HTML/plain-text parts to MIMEMultipart message
    # The email client will try to render the last part first
    message.attach(part2)
    
    # Create secure connection with server and send email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.seznam.cz", 465, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(
            sender_email, receiver_email, message.as_string()
        )
        
    
with open('recommendations.json', 'r') as f:
    data = json.load(f)

for tracker, recommendations in data.items():
    tracker_id = tracker
    receiver_email = recommendations['email']
    district = recommendations['district']
    links = recommendations['links']
    
    send_email_with_recommendations(receiver_email, tracker_id, district, links)
