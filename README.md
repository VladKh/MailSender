# MailSender

Script connect to data base, get information from table, create a letter and sent to recipient(s).

To start the script need to fill fields in the files:
 
 properties/db/mysql.conf.txt
 
  login: logint_to_DB
  password: password_to_DB
  database: name_of_DB

 properties/smtp/smtp.conf.txt
 
  server : server_name/IP
  port : 25 (usually)
  login: logint_to_SMTP
  password: password_to_SMTP
 
 To run the script use: bin/startMS.sh
