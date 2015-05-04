import os
import logging.config

def log_file():
    # if os.path.isfile('logs/mail_sender.log'):
    #     if os.path.getsize('logs/mail_sender.log') > 10*1024*1024:
    #         os.remove('logs/mail_sender.log')
        
    # Get configuration of the logger
    logging.config.fileConfig('properties/logger/logger.conf')
    logger = logging.getLogger('file')
    
    return logger