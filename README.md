# MailSender

Script connect to data base, get information from table, create a letter and sent to recipient(s).

To start the script need to fill fields in the files: </br>
 
 properties/db/mysql.conf.txt</br>
 
  login: logint_to_DB</br>
  password: password_to_DB</br>
  database: name_of_DB</br>

 properties/smtp/smtp.conf.txt</br>
 
  server : server_name/IP</br>
  port : 25 (usually) </br>
  login: logint_to_SMTP</br>
  password: password_to_SMTP</br>
 
 To run the script use: bin/startMS.sh
