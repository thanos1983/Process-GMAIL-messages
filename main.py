#!/usr/bin/env python

import pprint
import config
import ParseEmailsPackage

__author__ = 'Athanasios Garyfalos'

sslConnectionObj = ParseEmailsPackage.imapLibSslConnection.ImapLibSslConnectionProcess()
initializationResult = sslConnectionObj.initialization(config.USERNAME,
                                                       config.PASSWORD,
                                                       config.FOLDER_TO_SCAN,
                                                       config.DESTINATION_FOLDER,
                                                       config.GMAIL_IMAP)

dictionary = {}
if "ERROR" in str(initializationResult):
    dictionary[config.GMAIL_IMAP] = initializationResult
    pprint.pprint(initializationResult)
    print("Send email")
else:
    dictionary[config.GMAIL_IMAP] = sslConnectionObj.email_process(config.FOLDER_TO_SCAN,
                                                                   config.SUBJECT_TO_MATCH,
                                                                   config.SENDER_EMAIL,
                                                                   config.DESTINATION_FOLDER)
    sslConnectionObj.connection_ssl_logout()
    pprint.pprint(dictionary)
exit(0)