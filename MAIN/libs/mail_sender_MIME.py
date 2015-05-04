'''
This script connects to the MySQL database,
receives data from the table, generate an emails and send it to recipients from database table.
Information about sending a message recorded in a database.
author v.khalamendi
'''

import datetime
import connections
import log_to_file
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate
from email.utils import make_msgid
from email.header import make_header
from time import sleep

def sendmailSMTP(mails):
    # Get SMTP server address and port from database
    try:
        con = connections.connect_MySQLdb()
        cur = con.cursor()
        cur.execute("SELECT mb_value FROM `mb_properties` WHERE mb_field = 'SMTP server'")
        server = cur.fetchone()[0]
        cur.execute("SELECT mb_value FROM `mb_properties` WHERE mb_field = 'SMTP port'")
        port = int(cur.fetchone()[0])
    except Exception as e:
        logger.error(str(e))
        raise Exception

    # Create connection to SMTP server
    try:
        serversmtp = connections.connect_SMTP(server, port)
    except Exception as e:
        logger.error(str(e))
        raise Exception

    logger.info('Connected\n')
    sended = 0
    notsendmsg = []

    for msg in mails:
        if serversmtp.noop()[0] != 250:
            # Create connection to SMTP server
            logger.info('Attempts to connect to the SMTP server will be retried after 5 seconds')
            sleep(5)
            try:
                serversmtp.quit()
                serversmtp = connections.connect_SMTP(server, port)
            except Exception as e:
                logger.error(str(e))
                raise Exception
        # Sending messages from the message list
        try:
            serversmtp.sendmail(str(msg[1]['From']),
                                [msg[1]['To']],
                                msg[1].as_string())
            logger.info('Mail was send to %s' % (msg[1]['To']))
            # Add the date of sending letters to MySQL database
            time = datetime.datetime.now().strftime('%Y:%m:%d %H:%M:%S')
            # cur.execute("UPDATE `mb_mail_buffer` SET `date_send` = '%s' WHERE `mail_id` = %s" % (time, msg[0]))
            con.commit()
            # Counter sent letters
            sended += 1
        except Exception as e:
            logger.error(str(e))
            cur.execute("UPDATE `mb_mail_buffer` SET `Attempt`=`Attempt` + %s WHERE `mail_id` = %s" % (1, msg[0]))
            con.commit()
            logger.info('Number of unsuccessful attempts to send an email to the %s increased by 1\n' % (msg[1]['To']))
            notsendmsg.append([str(msg[1]['To']), str(e)])

    serversmtp.quit()
    cur.close()
    con.close()
    # Send email about error to admin
    if notsendmsg:
        logger.info('Send email about error to admin')
        send_to_admin(notsendmsg)

    logger.info('%s mails were send' % sended)
    logger.info('Disconnect from MySQLdb and SMTP servers')

def send_to_admin(notsendmsg):
    try:
        con = connections.connect_MySQLdb()
        cur = con.cursor()
        cur.execute("SELECT mb_value FROM `mb_properties` WHERE mb_field='Sender'")
        sender = cur.fetchone()[0]
        # Get SMTP server address and port from database
        cur.execute("SELECT mb_value FROM `mb_properties` WHERE mb_field = 'SMTP server'")
        server = cur.fetchone()[0]
        cur.execute("SELECT mb_value FROM `mb_properties` WHERE mb_field = 'SMTP port'")
        port = int(cur.fetchone()[0])
        # Get admin email address from database
        cur.execute("SELECT mb_value FROM `mb_properties` WHERE mb_field='Admin email'")
        admin = cur.fetchone()[0]
        cur.close()
        con.close()
    except Exception as e:
        logger.error(str(e))
        raise Exception

    # Create connection to SMTP server
    try:
        serversmtp = connections.connect_SMTP(server, port)
    except Exception as e:
        logger.error(str(e))
        raise Exception
    logger.info('Connected\n')
    serversmtp.noop()

    for msg in notsendmsg:
        # Create email fo admin
        email = MIMEMultipart('related')
        email['Subject'] = make_header([('SRK DPIportal [Mail Sender] Impossible send email!', 'UTF-8')])
        email['Date'] = formatdate(localtime=True)
        email['Organization'] = make_header([('SAMSUNG', 'UTF-8')])
        email['X-Mailer'] = make_header([('MailSender', 'UTF-8')])
        email['Message-ID'] = make_msgid()
        email['From'] = make_header([(sender, 'UTF-8')])
        email['To'] = make_header([(admin, 'UTF-8')])
        email.preamble = "This is a multi-part message in MIME format."
        email.epilogue = "End of message"
        partbody = MIMEText('Impossible send email to ' + msg[0] + '\n' + 'Error:\n' + msg[1], '', 'UTF-8')
        email.attach(partbody)
        try:
            serversmtp.sendmail(str(email['From']),
                                str(email['To']).split('; '),
                                email.as_string())
            logger.info('Mail was send to %s' % admin)
        except Exception as e:
            logger.error(e)
            logger.info('Impossible send email to admin %s' % admin)

    serversmtp.quit()

def get_data():
    mails = []
    # Create connection to MySQL db
    try:
        con = connections.connect_MySQLdb()
    except Exception as e:
        logger.error(str(e))
        raise Exception

    logger.info('Successful connection to MySQLdb')
    cur = con.cursor()
    # Get value sender from database
    try:
        cur.execute("SELECT mb_value FROM `mb_properties` WHERE mb_field='Sender'")
        sender = cur.fetchone()[0]
        cur.execute("SELECT mb_value FROM `mb_properties` WHERE mb_field='Attempts'")
        attempt = cur.fetchone()[0]
        # Get all necessary information from database
        cur.execute("""
                    SELECT mb_mail_buffer.mail_id, p4s_srk_perforce_users.user_email,
                    mb_mail_buffer.mail_subject, mb_mail_buffer.mail_body,
                    mb_mail_buffer.sender_marker
                    FROM mb_mail_buffer, p4s_srk_perforce_users
                    WHERE (
                    mb_mail_buffer.destination_id = p4s_srk_perforce_users.user_id
                    AND mb_mail_buffer.attempt < %s
                    AND mb_mail_buffer.date_send is NULL)
                    """ % attempt)
        rows = cur.fetchall()
    except Exception as e:
        logger.error(str(e))
        raise Exception

    logger.info('Information from database is obtained')
    # Create email from obtained information
    for row in rows:
        msg = MIMEMultipart('related')
        msg['Subject'] = make_header([(row[2], 'UTF-8')])
        msg['Date'] = formatdate(localtime=True)
        msg['Organization'] = make_header([('SAMSUNG', 'UTF-8')])
        msg['X-Mailer'] = make_header([('MailSender', 'UTF-8')])
        msg['Message-ID'] = make_msgid()
        msg['From'] = make_header([(sender, 'UTF-8')])
        if ';' in row[1]:
            msg['To'] = make_header([(row[1].split('; '), 'UTF-8')])
        else:
            msg['To'] = make_header([(row[1], 'UTF-8')])
        msg.preamble = "This is a multi-part message in MIME format."
        msg.epilogue = "End of message"
        partbody = MIMEText(row[3], '', 'UTF-8')
        msg.attach(partbody)
        # Create a list with tags mail_id, email object and sender_marker
        mails.append((row[0], msg))
    cur.close()
    con.close()
    if mails:
        logger.info('Created %s letters' % len(mails))
    return mails


if __name__ == '__main__':
    logger = log_to_file.log_file()
    logger.info('#'*40 + ' START ' + '#'*40 + '\n')
    mails = []
    # Get data from database
    logger.info('Step get information from database start...')
    try:
        try:
            mails = get_data()
            logger.info('Step get information from database finished\n')
        except Exception as e:
            logger.error(str(e))
            logger.error('Problem to connection or get information from MySQLdb!')
            raise
        if mails:
            # Send mail to recipient
            try:
                logger.i.nfo('Step send mails start...')
                sendmailSMTP(mails)
                logger.info('Step send mails finished\n')
            except Exception:
                logger.error('Connection to SMTP failed!')
                logger.error('Mails were not send!')
        else:
           logger.info('There is no new information in database!')
    finally:
            logger.info('#'*40 + ' FINISH ' + '#'*40 + '\n')
