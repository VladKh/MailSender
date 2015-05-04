'''
This script connects to the MySQL database,
receives data from the table, generates an email and sends it to recipient from database table.
author v.khalamendi.
'''

import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from MailSender.DEV.libs_test import connections
import log_to_file


def sendmailSMTP(mails):
    # Get SMTP server address and port from database
    try:
        con = connections.connect_MySQLdb()
        cur = con.cursor()
    except Exception as e:
        logger.error(str(e))
        raise Exception

    # Create connection to SMTP server
    try:
        serversmtp = connections.connect_SMTP()
    except Exception as e:
        logger.error(str(e))
        raise Exception

    logger.info('Connected\n')
    sended = 0
    for msg in mails:
        # Sending messages from the message list
        try:
            serversmtp.sendmail(msg[1]['From'],
                                msg['To'].split(', '),
                                msg[1].as_string())
            logger.info('Mail was send to %s' % (msg[1]['To']))
            # Add the date of sending letters to MySQL database
            time = datetime.datetime.now().strftime('%Y:%m:%d %H:%M:%S')
            cur.execute("UPDATE `mb_mail_buffer` SET `date_send` = '%s' WHERE `mail_id` = %s" % (time, msg[0]))
            con.commit()
            # Counter sent letters
            sended += 1
        except Exception as e:
            logger.error(str(e))
            cur.execute("UPDATE `mb_mail_buffer` SET `Attempt`=`Attempt` + %s WHERE `mail_id` = %s" % (1, msg[0]))
            con.commit()
            logger.info('Number of unsuccessful attempts to send an email to the %s increased by 1\n' % (msg[1]['To']))
            # Send email about error to admin
            send_to_admin(serversmtp, msg[1]['From'], msg[1]['To'], str(e), cur)

    logger.info('%s mails were send' % sended)
    serversmtp.quit()
    cur.close()
    con.close()
    logger.info('Disconnect from MySQLdb and SMTP servers')

def send_to_admin(serversmtp, frm, to, error, cur):
    logger.info('Send email about error to admin')
    # Get admin email address from database
    cur.execute("SELECT mb_value FROM `mb_properties` WHERE mb_field='Admin email'")
    admin = cur.fetchone()[0]
    logger.info(type(admin))
    logger.info(admin)
    # Create email fo admin
    msg = MIMEMultipart('mixed')
    msg['Subject'] = 'SRK DPIportal [Mail Sender] Impossible send email!'
    msg['From'] = frm
    msg['To'] = admin
    partbody = MIMEText('Impossible send email to ' + to + '\n' + 'Error:\n' + error, 'plain')
    msg.attach(partbody)
    serversmtp.set_debuglevel(3)
    try:
        serversmtp.sendmail(msg['From'],
                            msg['To'].split(', '),
                            msg.as_string())
        logger.info('Mail was send to %s' % admin)
    except Exception as e:
        logger.error(str(e))        
    logger.info('Impossible send email to admin %s' % admin)
        
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
                    SELECT mb_mail_buffer.mail_id,
                    users.user_email,
                    mb_mail_buffer.mail_subject,
                    mb_mail_buffer.mail_body,
                    mb_mail_buffer.sender_marker
                    FROM mail_sender.mb_mail_buffer, p4sync.users
                    WHERE
                    mb_mail_buffer.destination_id = users.user_id
                    AND mb_mail_buffer.attempt < %s
                    AND mb_mail_buffer.date_send is NULL
                    """ % attempt)
        rows = cur.fetchall()
    except Exception as e:
        logger.error(str(e))
        raise Exception

    logger.info('Information from database is obtained')
    # Create email from obtained information
    for row in rows:
        msg = MIMEMultipart('mixed')
        msg['Subject'] = row[2]
        msg['From'] = sender
        msg['To'] = 'vfghfgjrykfghkfm'
        partbody = MIMEText(row[3])
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
                logger.info('Step send mails start...')
                sendmailSMTP(mails)
                logger.info('Step send mails finished\n')
            except Exception:
                logger.error('Connection to SMTP failed!')
                logger.error('Mails were not send!')
        else:
           logger.info('There is no new information in database!')
    finally:
            logger.info('#'*40 + ' FINISH ' + '#'*40 + '\n')
