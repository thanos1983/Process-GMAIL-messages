#!/usr/bin/env python

import email
import pprint
import imaplib
import ParseEmailsPackage

__author__ = 'Athanasios Garyfalos'


def initialization_process(user_name, user_password, folder):
    try:
        imap4 = imaplib.IMAP4_SSL('imap.gmail.com')  # Connects over an SSL encrypted socket
        imap4.login(user_name, user_password)
        imap4.list()  # List of "folders" aka labels in gmail
        imap4.select(folder)  # Default INBOX folder alternative select('FOLDER')
    except imaplib.IMAP4.error as e:
        return "ERROR, Imap4 login: {}".format(e)
    return imap4


def logout_process(imap4):
    try:
        imap4.close()
        imap4.logout()
    except imaplib.IMAP4.error as e:
        return "ERROR, Imap4 logout: {}".format(e)
    return


def main(user_email, user_pass, scan_folder, subject_match, destination_folder):
    dictionary = {scan_folder: None}
    imap4 = initialization_process(user_email, user_pass, scan_folder)
    if "ERROR" in imap4:
        dictionary[scan_folder] = imap4
        return dictionary
    try:
        result, uids = imap4.uid('search', None, "ALL")  # search and return uids
        if uids == ['']:
            dictionary[scan_folder] = 'Is Empty'
        else:
            for uid in uids[0].split():  # Each uid is a space separated string
                dictionary[uid] = {'MESSAGE BODY': None, 'BOOKING': None, 'SUBJECT': None, 'RESULT': None}
                result, header = imap4.uid('fetch', uid, '(UID BODY[HEADER])')
                if result != 'OK':
                    raise Exception('Can not retrieve "Header" from EMAIL: {}'.format(uid))
                subject = email.message_from_string(header[0][1])
                subject = subject['Subject']
                if subject is None:
                    dictionary[uid]['SUBJECT'] = '(no subject)'
                else:
                    dictionary[uid]['SUBJECT'] = subject
                if subject_match in dictionary[uid]['SUBJECT']:
                    result, body = imap4.uid('fetch', uid, '(UID BODY[TEXT])')
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
                    result, copy = imap4.uid('COPY', uid, destination_folder)
                    if result == 'OK':
                        dictionary[uid]['RESULT'] = 'COPIED'
                        result, delete = imap4.uid('STORE', uid, '+FLAGS', '(\Deleted)')
                        imap4.expunge()
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
                    del dictionary[uid]['BOOKING']
                    result, trashed = imap4.uid('COPY', uid, '[Gmail]/Trash')
                    if result == 'OK':
                        dictionary[uid]['RESULT'] = 'TRASHED'
                    elif result != 'OK':
                        dictionary[uid]['RESULT'] = 'ERROR'
                        continue
            dictionary = {scan_folder: dictionary}
    except imaplib.IMAP4.error as e:
        print("Imap4 Exception")
        dictionary[scan_folder] = "ERROR, Imap4: {}".format(e)
        return dictionary
    except Exception as e:
        print("Exception")
        dictionary[scan_folder] = "ERROR, Exception: {}".format(e)
        return dictionary
    finally:
        print("Finally")
        dictionary[scan_folder] = logout_process(imap4)
        return dictionary

if __name__ == "__main__":
    username = 'example.email@gmail.com'
    password = 'examplePassword'
    main_dictionary = main(username, password, 'INBOX', 'BOKNING', 'tmp2')
    pprint.pprint(main_dictionary)
    exit(0)
