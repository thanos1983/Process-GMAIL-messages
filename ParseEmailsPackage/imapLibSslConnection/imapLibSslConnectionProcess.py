#!/usr/bin/python

import imaplib

__author__ = 'Athanasios Garyfalos'


class ImapLibSslConnectionProcess(object):

    def __init__(self):

        self.imap4_obj = None

    def connection_ssl(self, username, password, folder='INBOX'):
        try:
            imap4 = imaplib.IMAP4_SSL('imap.gmail.com')  # Connects over an SSL encrypted socket
            imap4.login(username, password)
            imap4.list()  # List of "folders" aka labels in gmail
            imap4.select(folder)  # Default INBOX folder alternative select('FOLDER')
            self.imap4_obj = imap4
        except imaplib.IMAP4.error as e:
            self.imap4_obj = "ERROR, Imap4 login: {}".format(e)
            return self.imap4_obj
        return self.imap4_obj

    def connection_ssl_logout(self):
        try:
            self.imap4_obj.close()
            self.imap4_obj.logout()
        except imaplib.IMAP4.error as e:
            self.imap4_obj = "ERROR, Imap4 logout: {}".format(e)
            return self.imap4_obj
        return True
