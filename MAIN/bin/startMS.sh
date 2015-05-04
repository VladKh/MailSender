#!/bin/bash

ROOT_PATH=$(cd $(dirname $0)/.. && pwd);
cd $ROOT_PATH

python ./libs/mail_sender_MIME.py
