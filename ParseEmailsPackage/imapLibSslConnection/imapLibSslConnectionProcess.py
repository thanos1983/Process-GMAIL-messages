#!/usr/bin/python

import email
import imaplib

__author__ = 'Athanasios Garyfalos'

# TODO: Create send email process


class ImapLibSslConnectionProcess(object):

    def __init__(self):

        self.error_str = None
        self.imap4_obj = None

    def check_if_folder_exists(self, folder):
        try:
            # Create a new folder if does not exist
            result, info = self.imap4_obj.select(folder)
            if result != 'OK':
                result, data = self.imap4_obj.create(folder)
                # Check if folder has been created before
                if result != 'OK':
                    self.error_str = 'ERROR, creating folder: {}'.format(folder)
                    return self.error_str
                elif result == 'OK':
                    return True
                elif result == 'OK':
                    # Folder exist proceed, nothing to do here
                    return True
            elif result == 'OK':
                return True
        except imaplib.IMAP4.error as e:
            self.error_str = "ERROR, Imap4 creating folder: {}".format(e)
            return self.error_str

    def initialization(self, username, password, folder_scan, folder_destination, imap):
        try:
            self.imap4_obj = imaplib.IMAP4_SSL(imap)  # Connects over an SSL encrypted socket
            self.imap4_obj.login(username, password)
            self.imap4_obj.list()  # List of "folders" aka labels in gmail
            result = self.check_if_folder_exists(folder_destination)
            if "ERROR" in str(result):
                return self.error_str
            self.imap4_obj.select(folder_scan)  # Default INBOX folder alternative select('FOLDER')
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

    def email_process(self, scan_folder, subject_match, sender_match, destination_folder):
        dictionary = {}
        try:
            result, uids = self.imap4_obj.uid('search', None, "ALL")  # search and return uids
            if uids == ['']:
                dictionary[scan_folder] = 'Is Empty'
                return dictionary
            else:
                for uid in uids[0].split():  # Each uid is a space separated string
                    dictionary[uid] = {'MESSAGE BODY': None, 'SUBJECT': None, 'RESULT': None}
                    result, header = self.imap4_obj.uid('fetch', uid, '(UID BODY[HEADER])')
                    if result != 'OK':
                        dictionary[uid] = 'ERROR, Can not retrieve "Header" from EMAIL'
                    header = email.message_from_string(header[0][1])
                    dictionary[uid]['FROM'] = header['From']
                    header = header['Subject']
                    if header is None:
                        dictionary[uid]['SUBJECT'] = '(no subject)'
                    else:
                        dictionary[uid]['SUBJECT'] = header
                    if subject_match in dictionary[uid]['SUBJECT'] and sender_match in dictionary[uid]['FROM']:
                        del dictionary[uid]['SUBJECT']
                        del dictionary[uid]['FROM']
                        result, body = self.imap4_obj.uid('fetch', uid, '(UID BODY[TEXT])')
                        if result != 'OK':
                            dictionary[uid] = 'ERROR, Can not retrieve "Body" from EMAIL'
                            continue
                        dictionary[uid]['MESSAGE BODY'] = body[0][1]
                        list_body = dictionary[uid]['MESSAGE BODY'].splitlines()
                        del dictionary[uid]['MESSAGE BODY']
                        result, copy = self.imap4_obj.uid('COPY', uid, destination_folder)
                        if result == 'OK':
                            dictionary[uid]['RESULT'] = 'COPIED'
                            result, delete = self.imap4_obj.uid('STORE', uid, '+FLAGS', '(\Deleted)')
                            self.imap4_obj.expunge()
                            if result == 'OK':
                                dictionary[uid]['RESULT'] = 'COPIED/DELETED'
                            elif result != 'OK':
                                dictionary[uid]['RESULT'] = 'ERROR'
                                continue
                        elif result != 'OK':
                            dictionary[uid]['RESULT'] = 'ERROR'
                            continue
                    else:
                        del dictionary[uid]['MESSAGE BODY']
                        del dictionary[uid]['SUBJECT']
                        del dictionary[uid]['FROM']
                        result, trashed = self.imap4_obj.uid('COPY', uid, '[Gmail]/Trash')
                        if result == 'OK':
                            dictionary[uid]['RESULT'] = 'TRASHED'
                        elif result != 'OK':
                            dictionary[uid]['RESULT'] = 'ERROR'
                            continue
                dictionary = {scan_folder: dictionary}
                return dictionary
        except imaplib.IMAP4.error as e:
            dictionary[scan_folder] = "ERROR, Imap4: {}".format(e)
            return dictionary
        except Exception as e:
            dictionary[scan_folder] = "ERROR, Exception: {}".format(e)
            return dictionary
