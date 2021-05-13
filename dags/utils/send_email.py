# -*- coding: utf-8 -*-
"""
Created on Mon May 10 16:10:05 2021

@author: ZZ03MG668
"""

import smtplib, ssl
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from datetime import date
import re
import requests
from PIL import Image
import io


def send_email_with_recommendations(receiver_email, tracker_id, district, links):
    '''
    sends one email to each tracker with underpriced flats
    
    receiver_email = who to send email to (info from tracker)
    tracker_id = unique id of tracker
    district = submitted district by customer
    links = links to underpriced appartments
    
    '''

    # establish authentication for email sending
    # TODO: move credentials to airflow storage
    sender_email = "realquik@seznam.cz"
    password = 'R34lquik'

    # set needed variables
    today = date.today().strftime("%d/%m/%Y")

    links_joined = []

    for link in links:
        page = re.search(r'(?:https:\/\/)([\w.-]*)', link).group(1) if re.search(r'(?:https:\/\/)([\w.-]*)',
                                                                                 link) is not None else ''

        link = '<li>' + f'<a href="{link}">' + str(page) + '</a>' + '</li>'
        links_joined.append(link)

    links_joined = ''.join(links_joined)

    ### set up message
    message = MIMEMultipart("alternative")
    message["Subject"] = f"{today}: Podceněné byty v lokalitě {district} na základě hlídacího psa číslo {tracker_id}"
    message["From"] = sender_email
    message["To"] = receiver_email

    # write body
    html = f"""<html>
                <body>
                    <p>Dobrý den,</p><br>
                    <p>na základě vašeho hlídacího psa <b>{tracker_id}</b> vám posíláme následující byty ve vámi zadané lokalitě 
                    <b>{district}</b>, které <b>{today}</b> náš systém vyhodnotil jako pravděpodobně podceněné.</p>
                    <ul>
                       {links_joined}
                    </ul>
                    <p>Hezký zbytek dne přeje,</p><br>
                    <p>RealQuik a.s.</p>
                    <p><img src="cid:realquik_logo"</p>
                </body>
            </html>
            """

    # Turn these into plain/html MIMEText objects
    main_text = MIMEText(html, "html")
    message.attach(main_text)
    logo = MIMEImage(open('realquik_logo.JPG', 'rb').read(), 'jpg')
    logo.add_header('Content-ID', '<realquik_logo>')
    message.attach(logo)
    # Add HTML/plain-text parts to MIMEMultipart message
    # The email client will try to render the last part first

    # Create secure connection with server and send email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.seznam.cz", 465, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(
            sender_email, receiver_email, message.as_string()
        )


def send_email_recommendations(recc):
    print('SENDING EMAILS...')
    # send emails to all customers
    for tracker, recommendations in recc.items():
        send_email_with_recommendations(recommendations['email'], tracker, recommendations['district'],
                                        recommendations['links'])
