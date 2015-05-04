import smtplib
import MySQLdb
import log_to_file


logger = log_to_file.log_file()

def connect_MySQLdb():
    # Connect to database
    logger.info('Try connected to MySQLdb database')
    for i in range(3):
        logger.info('Attempt No.: %s' % (i+1,))
        try:
            con = MySQLdb.connect(host='localhost',
                                 user='',
                                 passwd='',
                                 db='',
                                 use_unicode=True,
                                 charset="utf8")
            return con
        except Exception as e:
            logger.exception('Attempt %s failed, because: %s' % (i+1, str(e)))
    else:
        raise Exception
    
def connect_SMTP():

    # Connection to the SMTP mail server, 3 attempts
    logger.info('Connecting to SMTP server....')
    for i in range(3):
        logger.info('Attempt No.: %s' % (i+1,))
        try:
            serversmtp = smtplib.SMTP('p-qb-app0.surc.kiev.ua', 25)
            serversmtp.set_debuglevel(1)
            serversmtp.ehlo_or_helo_if_needed()
            return serversmtp
        except Exception as e:
            logger.exception('Attempt %s failed, because: %s' % (i+1, str(e)))
    else:
        raise Exception