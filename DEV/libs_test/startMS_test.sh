#!/bin/bash

ROOT_PATH=$(cd $(dirname $0)/.. && pwd);
cd $ROOT_PATH

python ./libs_test/mail_sender_test.py