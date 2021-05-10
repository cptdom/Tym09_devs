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

today = date.today().strftime("%d/%m/%Y")

with open('recommendations.json', 'r') as f:
    data = json.load(f)

for tracker, recommendations in data.items():
    tracker_id = tracker
    receiver_email = recommendations['email']
    district = recommendations['district']
    links = recommendations['links']   

receiver_email = 'jachym.dvorak@seznam.cz'

port = 587  # For starttls
smtp_server = "smtp.seznam.cz"
sender_email = "realquik@seznam.cz"
password = 'R34lquik'
    
message = MIMEMultipart("alternative")
message["Subject"] = f"Podceněné byty v den {today} na základě hlídacího psa {tracker_id}"
message["From"] = sender_email
message["To"] = receiver_email

# Create the plain-text and HTML version of your message
text = f"""\
Dobrý den,

na základě vašeho hlídacího psa {tracker_id} vám posíláme následující byty, které
{today} náš systém vyhodnotil jako pravděpodobně podceněné.

Hezký zbytek dne přeje,

RealQuik a.s."""


html = f"""\
<html>
  <body>
    <p>Dobrý den,<br>
    <br>
    na základě vašeho hlídacího psa {tracker_id} vám posíláme následující byty, které
    {today} náš systém vyhodnotil jako pravděpodobně podceněné.
       <br>
       <ul>
       <li>{links[0]}</li>
      <li> {links[1]}</li>
       <li>{links[2]}</li>
       <li>{links[3]}</li>
       <li>{links[4]}</li>
       <li>{links[5]}</li>
       <li>{links[6]}</li>
       <li>{links[7]}</li>
      <li> {links[8]}</li>
       <li>{links[9]}</li>
       </ul>
       <br>
       Hezký zbytek dne přeje,<br>
       <br>
       RealQuik a.s.
    </p>
  </body>
</html>
"""

# Turn these into plain/html MIMEText objects
part1 = MIMEText(text, "plain")
part2 = MIMEText(html, "html")

# Add HTML/plain-text parts to MIMEMultipart message
# The email client will try to render the last part first
message.attach(part1)
message.attach(part2)

# Create secure connection with server and send email
context = ssl.create_default_context()
with smtplib.SMTP_SSL("smtp.seznam.cz", 465, context=context) as server:
    server.login(sender_email, password)
    server.sendmail(
        sender_email, receiver_email, message.as_string()
    )