# Copyright (c) 2012, Braiden Kindt.
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 
#   1. Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
# 
#   2. Redistributions in binary form must reproduce the above
#      copyright notice, this list of conditions and the following
#      disclaimer in the documentation and/or other materials
#      provided with the distribution.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDER AND CONTRIBUTORS
# ''AS IS'' AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY
# WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.


import logging
import os
import sys
import urllib
import urllib2
import cookielib
import json

import poster.encode
import poster.streaminghttp

_log = logging.getLogger("antagent.connect")

class GarminConnect(object):

    username = None
    password = None

    def __init__(self):
        cookies = cookielib.CookieJar()
        cookie_handler = urllib2.HTTPCookieProcessor(cookies)
        self.opener = urllib2.build_opener(
                cookie_handler,
                poster.streaminghttp.StreamingHTTPHandler,
                poster.streaminghttp.StreamingHTTPRedirectHandler,
                poster.streaminghttp.StreamingHTTPSHandler)

    def login(self):
        # get session cookies
        _log.debug("Fetching cookies from Garmin Connect.")
        self.opener.open("http://connect.garmin.com/signin")
        # build the login string
        login_dict = {
            "login": "login",
            "login:loginUsernameField": self.username,
            "login:password": self.password,
            "login:signInButton": "Sign In",
            "javax.faces.ViewState": "j_id1",
        }
        login_str = urllib.urlencode(login_dict)
        # post login credentials
        _log.debug("Posting login credentials to Garmin Connect. username=%s", self.username)
        self.opener.open("https://connect.garmin.com/signin", login_str)
        # verify we're logged in
        _log.debug("Checking if login was successful.")
        reply = self.opener.open("http://connect.garmin.com/user/username")
        if json.loads(reply.read())["username"] != self.username: 
            raise InvalidLogin()
    
    def upload(self, tcx):
        with open(tcx) as file:
            upload_dict = {
                "responseContentType": "text/html",
                "data": file,
            }
            data, headers = poster.encode.multipart_encode(upload_dict)
            _log.info("Uploading %s to Garmin Connect.", tcx) 
            request = urllib2.Request("http://connect.garmin.com/proxy/upload-service-1.1/json/upload/.tcx", data, headers)
            self.opener.open(request)
        

class InvalidLogin(Exception): pass


if __name__ == "__main__":
    connect = GarminConnect()
    connect.username = sys.argv[1]
    connect.password = sys.argv[2]
    connect.login()
    for file in sys.argv[3:]:
        connect.upload(file)

    
# vim: ts=4 sts=4 et
