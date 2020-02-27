from __future__ import print_function
import os
import subprocess
import shlex
import datetime
import traceback
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import cred
# there's some cruft up there. get off my back.

dt = datetime.datetime.today() # Get today's date
dts = dt.strftime("%Y_%m_%d")
ddi = int(dt.day)-1 # Isolate day of the month and subtract one because list starts at zero.
# Paths to born digital directories
avd = '//roxanne/roxanne/BORN_DIG/AVD/'
ma = '//roxanne/roxanne/BORN_DIG/MANUSCRIPTS/'
emhf = '//roxanne/roxanne/BORN_DIG/EMHF/Accessions'
acc = '/Accessions'
# Make lists of directories within born dig directories
avd1 = os.listdir(avd)
ma1 = os.listdir(ma)
# Slice everything after #29 to overflow into secondary lists
avd2 = avd1[29:]
ma2 = ma1[29:]

# Path to fixity database files
avddb = '//roxanne/roxanne/ADMIN/cyrano/data/AVD/'
madb = '//roxanne/roxanne/ADMIN/cyrano/data/MANUSCRIPTS/'
emhfdb = '//roxanne/roxanne/ADMIN/cyrano/data/EMHF/emhf.csv'

# Logs
runlog = 'log_' + dts + '.txt'
errlog = 'err_' + dts + '.csv'


# pass target directory and corresponding database csv to rficg to compare checksums, etc

def fixityCheck(target,dbtarget):
    try:
        command = ["python", "rfigc.py", "-i", "{}".format(target), "-d", "{}".format(dbtarget), "-e", "//roxanne/roxanne/ADMIN/cyrano/logs/{}".format(errlog), "-l", "//roxanne/roxanne/ADMIN/cyrano/logs/{}".format(runlog)]
        process = subprocess.Popen(command,stdout=subprocess.PIPE)
        stdout = process.communicate()[0]
        print('STDOUT:{}'.format(stdout))
    except:
        print('Nope.')

# Take error log as argument and mail it in body of message.		
def mailErrorLog(efn):
    try:
        sender = "PyFileFixity <system@hagley.org>"
        message = """\
Subject: Fixity Failure!
To: mdemers@hagley.org
From: system@hagley.org

Error Log: 
"""
        msg = message + efn
        context=ssl.create_default_context()
        with smtplib.SMTP("smtp.office365.com", 587) as server:
            server.connect("smtp.office365.com", 587)
            server.ehlo()
            server.starttls(context=context)
            server.login(cred.user, cred.pwd) # credentials for system address in cred.py
            server.sendmail(sender, "mdemers@hagley.org", msg)
            server.quit()
    except:
         print('Delivery failed')

# if the num of directories in list is higher than date, use date as index on directory list. send the final paths to fixity. i know this looks weird, it's easier to track like this atm
if len(avd1) > ddi:
    target = avd + avd1[ddi] + acc
    dbtarget = avddb + avd1[ddi] + '.csv'
    fixityCheck(target,dbtarget)
else:
    print('Nothing today...AVD')
if len(avd2) > ddi:
    target = avd + avd2[ddi] + acc
    dbtarget = avddb + avd2[ddi] + '.csv'
    fixityCheck(target,dbtarget)
else:
    print('None extra...AVD')
if len(ma1) > ddi:
    target = ma + ma1[ddi] + acc
    dbtarget = madb + ma1[ddi] + '.csv'
    fixityCheck(target,dbtarget)
else:
    print('Nothing today...MA')
if len(ma2) > ddi:
    target = ma + ma2[ddi] + acc
    dbtarget = madb + ma2[ddi] + '.csv'
    fixityCheck(target,dbtarget)
else:
    print('None extra...MA')
# Check EMHF on every 31st
if ddi == 30:
    target = emhf
    dbtarget = emhfdb
    fixityCheck(target,dbtarget)
else:
    print('Nothing today...EMHF')
	
# Look in error log for failures. Pass any data to mail.
with open('//roxanne/roxanne/ADMIN/cyrano/logs/{}'.format(errlog)) as f:
    if 'failed' or 'missing' in f.read():
        ef = open('//roxanne/roxanne/ADMIN/cyrano/logs/{}'.format(errlog))
        efn = ef.read()
        mailErrorLog(efn)