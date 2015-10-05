"""
	bitbucketacl module
"""

import requests
import yaml
from requests_oauthlib import OAuth1

# Class to maintain authentication for bitbucket
# on default use OAuth1 for its authentication from config file
# can use basic authentication as optional authentication
class BitbucketAcl:

    # Constructor can receive username, password for basic authentication
    # and config file's path for OAuth1 needs
    def __init__(self, username=None, password=None, conf='bitbucket.conf'):
        self.username = username
        self.password = password
        self.auth = {}

        # Try to load config file to set OAuth1 as its authentication
        try:
            self.config = yaml.load(file(conf))
            if self.config['CONSUMER_KEY'] is not None and self.config['CONSUMER_KEY'] != '':
                if self.config['CONSUMER_SECRET'] is not None and self.config['CONSUMER_SECRET'] != '':
                    self.auth = OAuth1(self.config['CONSUMER_KEY'],self.config['CONSUMER_SECRET'])
        except Exception, e:
            pass

        # Change authentication to be basic authentication
        # if username and password is given as argument of constructor
        if self.username is not None and self.password is not None:
            self.auth = {
                'username': self.username,
                'password': self.password
            }

    # Method for request bitbucket api, return requests.response
    # on default method for request is 'GET'
    def access_api(self, url=None, method='GET', auth=None, data=None, headers=None):
        res = None
        try:
            # print url
            res = requests.request(method=method or 'GET', url=url, auth=auth, data=data, headers=headers)
            pass
        except Exception, e:
            raise e
        finally:
            return res
