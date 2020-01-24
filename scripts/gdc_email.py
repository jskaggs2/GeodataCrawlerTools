# -*- coding: utf-8 -*-
"""
Created on Tue Nov 26 13:50:16 2019

@author: jskaggs
"""
import smtplib

print "testing email"

subject = "Crawler Job Ended"
text = "Good luck bastard"
content = 'Subject: %s\n\n%s' % (subject, text)
mail = smtplib.SMTP('smtp.gmail.com', 587)
mail.ehlo()
mail.starttls()
mail.login('geodatacrawler@gmail.com','XXX')
mail.sendmail('geodatacrawler@gmail.com','jonathon.skaggs@gmail.com', content) 
mail.close()

print "email sent"