#!/usr/bin/python

import imaplib
import logging
import UnreadEmailPackage

__author__ = 'Athanasios Garyfalos'

class ImapLibSslConnectionProcess(object):

def __init__(self, imap4_obj):

    self.imap4_obj

    def connection_ssl(username, password, folder):
        try:
            imap4 = imaplib.IMAP4_SSL('imap.gmail.com')  # Connects over an SSL encrypted socket
            imap4.login(username, password)
            imap4.list()  # List of "folders" aka labels in gmail
            imap4.select(folder)  # Default INBOX folder alternative select('FOLDER')
        except imaplib.IMAP4.error as e:
            self.imap4 = "ERROR, Imap4 login: {}".format(e)
            return self.imap4
        return self.imap4_obj