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
    <meta charset="UTF-8"> 
    <meta content="width=device-width, initial-scale=1" name="viewport"> 
    <meta name="x-apple-disable-message-reformatting"> 
    <meta http-equiv="X-UA-Compatible" content="IE=edge"> 
    <meta content="telephone=no" name="format-detection"> 
    <body style="width:100%;font-family:arial, 'helvetica neue', helvetica, sans-serif;-webkit-text-size-adjust:100%;-ms-text-size-adjust:100%;padding:0;Margin:0"> 
        <div class="es-wrapper-color" style="background-color:#9FC5E8"> 
                <body>
            <table class="es-wrapper" width="100%" cellspacing="0" cellpadding="0" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;padding:0;Margin:0;width:100%;height:100%;background-repeat:repeat;background-position:center top;background-color:#9FC5E8"> 
                <tr style="border-collapse:collapse"> 
                    <td valign="top" style="padding:0;Margin:0"> 
                    <table class="es-content-body" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;background-color:transparent;width:600px" cellspacing="0" cellpadding="0" align="center" bgcolor="#333333"> 
                        <tr style="border-collapse:collapse"> 
                         <td align="left" style="padding:10px;Margin:0"> 
                            <table class="es-left" cellspacing="0" cellpadding="0" align="left" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;float:left"> 
                                <tr style="border-collapse:collapse"> 
                                <td class="es-m-p0r es-m-p20b" valign="top" align="center" style="padding:0;Margin:0;width:369px"> 
                                <table width="100%" cellspacing="0" cellpadding="0" role="presentation" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px"> 
                                    <tr style="border-collapse:collapse"> 
                                    <td align="center" bgcolor="#ffffff" style="padding:0;Margin:0"><p style="Margin:0;-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;font-family:arial, 'helvetica neue', helvetica, sans-serif;line-height:24px;color:#333333;font-size:16px"><strong>Váš RealQuik Report Tracker</strong></p></td> 
                                    </tr> 
                                </table></td> 
                                </tr> 
                            </table>


                            <table cellspacing="0" cellpadding="0" align="right" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px"> 
                            <tr style="border-collapse:collapse"> 
                            <td align="left" style="padding:0;Margin:0;width:191px"> 
                                <table width="100%" cellspacing="0" cellpadding="0" role="presentation" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px"> 
                                <tr style="border-collapse:collapse"> 
                                <td align="center" bgcolor="#ffffff" style="padding:0;Margin:0"><p style="Margin:0;-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;font-family:arial, 'helvetica neue', helvetica, sans-serif;line-height:21px;color:#333333;font-size:14px">Pravidelný report ve 13:05</p></td> 
                                </tr> 
                                </table></td> 
                            </tr> 
                            </table> 
                         </td> 
                       </tr> 
                   </table> 
                   <table class="es-content" cellspacing="0" cellpadding="0" align="center" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;table-layout:fixed !important;width:100%"> 
                    <tr style="border-collapse:collapse"> 
                     <td align="center" style="padding:0;Margin:0"> 
                      <table class="es-content-body" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px;background-color:transparent;width:600px" cellspacing="0" cellpadding="0" align="center" bgcolor="#333333"> 
                        <tr style="border-collapse:collapse"> 
                         <td align="left" bgcolor="#ffffff" style="padding:0;Margin:0;padding-top:20px;padding-left:20px;padding-right:20px;background-color:#FFFFFF"> 
                          <table cellpadding="0" cellspacing="0" width="100%" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px"> 
                            <tr style="border-collapse:collapse"> 
                             <td align="center" valign="top" style="padding:0;Margin:0;width:560px"> 
                              <table cellpadding="0" cellspacing="0" width="100%" role="presentation" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px"> 
                                <tr style="border-collapse:collapse"> 
                                 <td align="left" bgcolor="#ffffff" style="padding:0;Margin:0"><p style="Margin:0;-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;font-family:arial, 'helvetica neue', helvetica, sans-serif;line-height:21px;color:#333333;font-size:14px">Dobrý den,</p><p style="Margin:0;-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;font-family:arial, 'helvetica neue', helvetica, sans-serif;line-height:21px;color:#333333;font-size:14px"><br></p><p style="Margin:0;-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;font-family:arial, 'helvetica neue', helvetica, sans-serif;line-height:21px;color:#333333;font-size:14px">na základě vašeho hlídacího psa <strong>{tracker_id}</strong> vám posíláme následující byty ve vámi zadané lokalitě <strong>{district}</strong>, které <strong>{today}</strong> náš systém vyhodnotil jako pravděpodobně podceněné.</p></td> 
                                </tr> 
                              </table></td> 
                            </tr> 
                          </table></td> 
                        </tr> 
                        <tr style="border-collapse:collapse"> 
                         <td align="center" bgcolor="#ffffff" style="padding:0;Margin:0;padding-top:20px;padding-left:20px;padding-right:20px;background-color:#FFFFFF"> 
                          <table cellpadding="0" cellspacing="0" width="100%" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px"> 
                            <tr style="border-collapse:collapse"> 
                             <td align="center" valign="top" style="padding:0;Margin:0;width:560px"> 
                              <table cellpadding="0" cellspacing="0" width="100%" role="presentation" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px"> 
                                <tr style="border-collapse:collapse"> 
                                 <td align="center" style="padding:0;Margin:0"  style="border-style:solid;border-color:#ffffff;background:#ffffff;border-width:0px;display:inline-block;border-radius:15px;width:auto"><a  style="mso-style-priority:100 !important;text-decoration:none;-webkit-text-size-adjust:none;box-shadow: 1px 1px 4px black;-ms-text-size-adjust:none;mso-line-height-rule:exactly;color:#000000;  font-size:18px;border-style:solid;border-color:#ffffff;border-width:10px 20px 10px 20px;display:inline-block;background:#ffffff;border-radius:15px;font-family:arial, 'helvetica neue', helvetica, sans-serif;font-weight:normal;font-style:normal;line-height:22px;width:auto;text-align:center;"> 
                                    <ul>{links_joined}
                                    </ul></td> 
                                </tr> 
                              </table></td> 
                            </tr> 
                          </table></td> 
                        </tr> 
                        <tr style="border-collapse:collapse"> 
                         <td align="left" bgcolor="#ffffff" style="padding:0;Margin:0;padding-top:20px;padding-left:20px;padding-right:20px;background-color:#FFFFFF"> 
                          <table cellpadding="0" cellspacing="0" width="100%" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px"> 
                            <tr style="border-collapse:collapse"> 
                             <td align="center" valign="top" style="padding:0;Margin:0;width:560px"> 
                              <table cellpadding="0" cellspacing="0" width="100%" role="presentation" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px"> 
                                <tr style="border-collapse:collapse"> 
                                 <td align="left" bgcolor="#ffffff" style="padding:0;Margin:0"><p style="Margin:0;-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;font-family:arial, 'helvetica neue', helvetica, sans-serif;line-height:21px;color:#333333;font-size:14px">Hezký zbytek dne přeje,</p><p style="Margin:0;-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;font-family:arial, 'helvetica neue', helvetica, sans-serif;line-height:21px;color:#333333;font-size:14px"><br></p><p style="Margin:0;-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;font-family:arial, 'helvetica neue', helvetica, sans-serif;line-height:21px;color:#333333;font-size:14px"><strong>RealQuik a.s.</strong></p></td> 
                                </tr> 
                              </table></td> 
                            </tr> 
                          </table></td> 
                        </tr> 
                        <tr style="border-collapse:collapse"> 
                         <td align="left" bgcolor="#ffffff" style="padding:0;Margin:0;padding-top:20px;padding-left:20px;padding-right:20px;background-color:#FFFFFF"> 
                          <table cellpadding="0" cellspacing="0" width="100%" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px"> 
                            <tr style="border-collapse:collapse"> 
                             <td align="center" valign="top" style="padding:0;Margin:0;width:560px"> 
                              <table cellpadding="0" cellspacing="0" width="100%" role="presentation" style="mso-table-lspace:0pt;mso-table-rspace:0pt;border-collapse:collapse;border-spacing:0px"> 
                                <tr style="border-collapse:collapse"> 
                                 <td align="center" style="padding:0;Margin:0;font-size:0px"><img class="adapt-img" src="https://lolofb.stripocdn.email/content/guids/50063606-1cf0-4b63-b046-265c7f7f4a6b/images/48381621333814262.jpg" alt style="display:block;border:0;outline:none;text-decoration:none;-ms-interpolation-mode:bicubic" width="350"></td> 
                                </tr> 
                              </table></td> 
                            </tr> 
                          </table></td> 
                        </tr> 
                      </table></td> 
                    </tr> 
                  </table>
                </td> 
            </tr> 
          </table> 
                </div>

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
