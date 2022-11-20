import email
import imaplib
from email.header import decode_header, make_header


class IMAP:

    def __init__(self, login_id, login_pwd):
        self.__imap = imaplib.IMAP4_SSL('imap.gmail.com')

        self.__imap.login(login_id, login_pwd)
        self.__imap.select("INBOX")

    def get_recent_email(self, search_mail_address):

        if search_mail_address != "ALL":
            search_range = f'(FROM "{search_mail_address}")'
        else:
            search_range = 'ALL'

        # 사서함의 모든 메일의 uid 정보 가져오기
        status, messages = self.__imap.uid('search', None, search_range)
        messages = messages[0].split()

        # 0이 가장 마지막 메일, -1이 가장 최신 메일
        recent_email = messages[-1]

        # fetch 명령어로 메일 가져오기
        res, msg = self.__imap.uid('fetch', recent_email, "(RFC822)")

        # 사람이 읽을 수 있는 형태로 변환
        raw = msg[0][1].decode('utf-8')
        
        return Email(raw)


class Email:

    def __init__(self, raw):
        self.__raw = raw
        self.__email_message = email.message_from_string(self.__raw)
        self.__from_address = make_header(decode_header(self.__email_message.get('From')))
        self.__subject = make_header(decode_header(self.__email_message.get('Subject')))
        
        self.__set_body()

    def __set_body(self):
        if self.__email_message.is_multipart():
            for part in self.__email_message.walk():
                ctype = part.get_content_type()
                cdispo = str(part.get('Content-Disposition'))
                if ctype == 'text/plain' and 'attachment' not in cdispo:
                    self.__body = part.get_payload(decode=True)  # decode
                    break
        else:
            self.__body = self.__email_message.get_payload(decode=True)
            
        self.__body = self.__body.decode('utf-8')


    def get_from_address(self):
        return self.__from_address


    def get_subject(self):
        return self.__subject

    
    def get_body(self):
        return self.__body

