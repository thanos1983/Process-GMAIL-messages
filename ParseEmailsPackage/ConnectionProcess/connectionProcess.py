#!/usr/bin/env python

import logging
import UnreadEmailPackage

__author__ = 'Athanasios Garyfalos'


class ImapLibSslConnectionProcess(object):
    """ Login, Logout imap4 process """


def __init__(self):
        """
        :rtype: object.output ssl connection object imaplib.IMAP4_SSL instance
        """
        self.imap4 = imap4
        # self.output = output


def initialization_process(user_name, user_password, folder):
    try:
        imap4 = imaplib.IMAP4_SSL('imap.gmail.com')  # Connects over an SSL encrypted socket
        imap4.login(user_name, user_password)
        imap4.list()  # List of "folders" aka labels in gmail
        imap4.select(folder)  # Default INBOX folder alternative select('FOLDER')
    except imaplib.IMAP4.error as e:
        self.imap4 = "ERROR, Imap4 login: {}".format(e)
        return self.imap4
    self.imap4 = imap4
    return self.imap4


def logout_process(imap4):
    try:
        imap4.close()
        imap4.logout()
    except imaplib.IMAP4.error as e:
        return "ERROR, Imap4 logout: {}".format(e)
    return