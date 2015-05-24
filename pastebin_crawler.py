#!/usr/bin/env python3
import os

import re
import time

from pyquery import PyQuery

class Logger:

    shell_mod = {
        '':'',
       'PURPLE' : '\033[95m',
       'CYAN' : '\033[96m',
       'DARKCYAN' : '\033[36m',
       'BLUE' : '\033[94m',
       'GREEN' : '\033[92m',
       'YELLOW' : '\033[93m',
       'RED' : '\033[91m',
       'BOLD' : '\033[1m',
       'UNDERLINE' : '\033[4m',
       'RESET' : '\033[0m'
    }

    def log ( self, message, is_bold=False, color=''):
        prefix = ''
        suffix = ''

        if os.name == 'posix':
            if is_bold:
                prefix += self.shell_mod['BOLD']
            prefix += self.shell_mod[color.upper()]

            suffix = self.shell_mod['RESET']

        message = prefix + message + suffix
        print ( message )

class Crawler:

    pastebin_url = 'http://pastebin.com'
    pastes_url = pastebin_url + '/archive'

    prev_checked_ids = []
    new_checked_ids = []

    regexes = [
        [r'(password\b|pass\b|pswd\b|passwd\b|pwd\b|pass\b)','passwords.txt','passwords'],
        [r'(serial\b|cd-key\b|key\b|license\b)','serials.txt','serials'],
        [r'(gmail.com|hotmail.com|live.com|yahoo)','mails.txt','mails'],
        [r'(hack|exploit|leak|usernames)','other.txt','other']
    ]

    def __init__(self):
        self.OK = 1
        self.ACCESS_DENIED = -1
        self.CONNECTION_FAIL = -2

    def get_pastes ( self ):
        Logger ().log ( 'Getting pastes', True )
        try:
            page = PyQuery ( url = self.pastes_url )
        except:
            return self.CONNECTION_FAIL,None
        page_html = page.html ()

        if re.match ( r'Pastebin\.com - Access Denied Warning', page_html, re.IGNORECASE ) or 'blocked your IP' in page_html:
            return self.ACCESS_DENIED,None
        else:
            return self.OK,page('.maintable img').next('a')

    def check_paste ( self, paste_id ):
        paste_url = self.pastebin_url + paste_id
        paste_txt = PyQuery ( url = paste_url )('#paste_code').text()

        for regex,file,directory in self.regexes:

            if re.match ( regex, paste_txt, re.IGNORECASE ):
                Logger ().log ( 'Found a matching paste: ' + paste_url + ' (' + file + ')', True, 'CYAN' )
                self.save_result ( paste_url,paste_id,file,directory )
                return True
            else:
                Logger ().log ( 'Not matching paste: ' + paste_url )
                return False

    def save_result ( self, paste_url, paste_id, file, directory ):
        timestamp = self.get_timestamp()
        with open ( file, 'a' ) as matching:
            matching.write ( timestamp + ' - ' + paste_url + '\n' )

        try:
            os.mkdir(directory)
        except:
            pass

        with open( directory + '/' + timestamp.replace('/','_') + paste_id + '.txt', 'w' ) as paste:
            paste_txt = PyQuery(url=paste_url)('#paste_code').text()
            paste.write(paste_txt)


    def start ( self, refresh_time = 30, delay = 1, ban_wait = 5, flush_after_x_refreshes=100, connection_timeout=60 ):
        count = 0
        while True:
            status,pastes = self.get_pastes ()

            if status == self.OK:
                for paste in pastes:
                    paste_id = PyQuery ( paste ).attr('href')
                    self.new_checked_ids.append ( paste_id )
                    if paste_id not in self.prev_checked_ids:
                        self.check_paste ( paste_id )
                        time.sleep ( delay )
                    count += 1

                if count == flush_after_x_refreshes:
                    self.prev_checked_ids = self.new_checked_ids
                    count = 0
                else:
                    self.prev_checked_ids += self.new_checked_ids
                self.new_checked_ids = []

                Logger().log('Waiting {:d} seconds to refresh...'.format(refresh_time), True)
                time.sleep ( refresh_time )
            elif status == self.ACCESS_DENIED:
                Logger ().log ( 'Damn! It looks like you have been banned (probably temporarily)', True, 'YELLOW' )
                for n in range ( 0, ban_wait ):
                    Logger ().log ( 'Please wait ' + str ( ban_wait - n ) + ' minute' + ( 's' if ( ban_wait - n ) > 1 else '' ) )
                    time.sleep ( 60 )
            elif status == self.CONNECTION_FAIL:
                Logger().log ( 'Connection down. Waiting {:s} seconds and trying again'.format(connection_timeout), True, 'RED')
                time.sleep(connection_timeout)


    def get_timestamp(self):
        return time.strftime('%Y/%m/%d %H:%M:%S')

try:
    Crawler ().start ()
except KeyboardInterrupt:
    Logger ().log ( 'Bye! Hope you found what you were looking for :)', True )
