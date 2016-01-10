#!/usr/bin/python

import email
import imaplib
import pprint

__author__ = 'Athanasios Garyfalos'


class ImapLibSslConnectionProcess(object):

    def __init__(self):

        self.imap4_obj = None

    def initialization(self, username, password, folder, imap):
        try:
            self.imap4_obj = imaplib.IMAP4_SSL(imap)  # Connects over an SSL encrypted socket
            self.imap4_obj.login(username, password)
            self.imap4_obj.list()  # List of "folders" aka labels in gmail
            self.imap4_obj.select(folder)  # Default INBOX folder alternative select('FOLDER')
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

    def email_process(self, scan_folder, subject_match, destination_folder):
        dictionary = {}
        try:
            result, uids = self.imap4_obj.uid('search', None, "ALL")  # search and return uids
            if uids == ['']:
                dictionary[scan_folder] = 'Is Empty'
                return dictionary
            else:
                for uid in uids[0].split():  # Each uid is a space separated string
                    dictionary[uid] = {'MESSAGE BODY': None, 'BOOKING': None, 'SUBJECT': None, 'RESULT': None}
                    result, header = self.imap4_obj.uid('fetch', uid, '(UID BODY[HEADER])')
                    if result != 'OK':
                        raise Exception('Can not retrieve "Header" from EMAIL: {}'.format(uid))
                    subject = email.message_from_string(header[0][1])
                    subject = subject['Subject']
                    if subject is None:
                        dictionary[uid]['SUBJECT'] = '(no subject)'
                    else:
                        dictionary[uid]['SUBJECT'] = subject
                    if subject_match in dictionary[uid]['SUBJECT']:
                        result, body = self.imap4_obj.uid('fetch', uid, '(UID BODY[TEXT])')
                        if result != 'OK':
                            raise Exception('Can not retrieve "Body" from EMAIL: {}'.format(uid))
                        dictionary[uid]['MESSAGE BODY'] = body[0][1]
                        list_body = dictionary[uid]['MESSAGE BODY'].splitlines()
                        found_list = []
                        for i, j in enumerate(list_body):
                            if 'Bokningsnummer:' in j:
                                found_list.append(list_body[i])
                                booking = found_list[0].split()
                                dictionary[uid]['BOOKING'] = booking[1]
                                del dictionary[uid]['MESSAGE BODY']
                                del dictionary[uid]['SUBJECT']
                                result, copy = self.imap4_obj.uid('COPY', uid, destination_folder)
                                if result == 'OK':
                                    dictionary[uid]['RESULT'] = 'COPIED'
                                    result, delete = self.imap4_obj.uid('STORE', uid, '+FLAGS', '(\Deleted)')
                                    self.imap4_obj.expunge()
                                    if result == 'OK':
                                        dictionary[uid]['RESULT'] = 'COPIED/DELETED'
                                        pprint.pprint(dictionary)
                                        exit(0)
                                    elif result != 'OK':
                                        dictionary[uid]['RESULT'] = 'ERROR'
                                        continue
                                elif result != 'OK':
                                    dictionary[uid]['RESULT'] = 'ERROR'
                                    continue
                    else:
                        del dictionary[uid]['MESSAGE BODY']
                        del dictionary[uid]['SUBJECT']
                        del dictionary[uid]['BOOKING']
                        result, trashed = self.imap4_obj.uid('COPY', uid, '[Gmail]/Trash')
                        if result == 'OK':
                            dictionary[uid]['RESULT'] = 'TRASHED'
                        elif result != 'OK':
                            dictionary[uid]['RESULT'] = 'ERROR'
                            continue
                dictionary = {scan_folder: dictionary}
                pprint.pprint(dictionary)
                exit(0)
                return dictionary
        except imaplib.IMAP4.error as e:
            dictionary[scan_folder] = "ERROR, Imap4: {}".format(e)
            return dictionary
        except Exception as e:
            dictionary[scan_folder] = "ERROR, Exception: {}".format(e)
            return dictionary
