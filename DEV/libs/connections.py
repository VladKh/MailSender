import smtplib
import ConfigParser

import MySQLdb

from MailSender.DEV.libs import log_to_file


logger = log_to_file.log_file()

def connect_MySQLdb():
    # Get login and password from file
    try:
        cfg = ConfigParser.SafeConfigParser()
        cfg.read('properties/db/mysql.conf')
        user = cfg.get('Mysqldb', 'login')
        pas = cfg.get('Mysqldb', 'password')
        database = cfg.get('Mysqldb', 'database')
    except Exception as e:
        logger.error('Check file mysql.conf!')
        logger.exception(str(e))
        raise Exception
    
    # Connect to database
    logger.info('Try connected to MySQLdb database')
    for i in range(3):
        logger.info('Attempt No.: %s' % (i+1,))
        try:
            db = MySQLdb.connect(host='localhost',
                                 user=user,
                                 passwd=pas,
                                 db=database,
                                 use_unicode=True,
                                 charset="utf8")

            return db
        except Exception as e:
            logger.exception('Attempt %s failed, because: %s' % (i+1, str(e)))
    else:
        raise Exception
    
def connect_SMTP(server, port):
    # Get login and password from file
    try:
        cfg = ConfigParser.SafeConfigParser()
        cfg.read('properties/smtp/smtp.conf')
        user = cfg.get('SMTP', 'login')
        pas = cfg.get('SMTP', 'password')
    except Exception as e:
        logger.error('Check file smtp.conf!')
        logger.exception(str(e))
        raise Exception
        
    # Connection to the SMTP mail server, 3 attempts
    logger.info('Connecting to SMTP server....')
    for i in range(3):
        logger.info('Attempt No.: %s' % (i+1,))
        try:
            serversmtp = smtplib.SMTP(server, port)
            serversmtp.ehlo_or_helo_if_needed()
            serversmtp.login(user, pas)
            serversmtp.ehlo_or_helo_if_needed()
            #serversmtp.set_debuglevel(1)
            return serversmtp
        except smtplib.SMTPException as e:
            logger.exception('Attempt %s failed, because: %s' % (i+1, str(e)))
    else:
        raise Exception