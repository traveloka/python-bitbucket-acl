"""
    bitbucketacl module
"""

import requests
import yaml
from requests_oauthlib import OAuth1


class BitbucketAcl:
    """Base class to manage authentication and acccess Bitbucket API"""

    def __init__(self, username=None, password=None, conf='bitbucket.conf'):
        """Args:
                username: username of account whose admin privilege in Team
                passowrd: password of account
                conf    : path to file for config file
                            that has consumer key & secret
        """
        self.username = username
        self.password = password
        self.auth = {}
        self.conf = conf
        self.load_authentication()

    def load_authentication(self):
        """Setup authentication for Bitbucket
        use basic auth or OAuth1
        """
        # Try to load config file to set OAuth1 as its authentication
        try:
            self.config = yaml.load(file(self.conf))
            if (self.config['CONSUMER_KEY'] is not None and
                    self.config['CONSUMER_KEY'] != ''):
                if (self.config['CONSUMER_SECRET'] is not None and
                        self.config['CONSUMER_SECRET'] != ''):
                    self.auth = OAuth1(self.config['CONSUMER_KEY'],
                                       self.config['CONSUMER_SECRET'])
        except Exception, e:
            pass

        # Change authentication to basic authentication
        # if username and password is given as argument of constructor
        if self.username is not None and self.password is not None:
            self.auth = {
                'username': self.username,
                'password': self.password
            }

    def access_api(
            self, url=None, method='GET', auth=None, data=None, headers=None
    ):
        """Handle request Bitbucket api
        Args:
            url     : destination url
            method  : access method e.g GET, PUT, DELETE etc.
            auth    : authentication. default is the given auth
            data    : additional data to be placed in body
            headers : headers setting to be sent
        """
        if auth is None:
            auth = self.auth
        res = None
        try:
            res = requests.request(method=method or 'GET',
                                   url=url, auth=auth,
                                   data=data,
                                   headers=headers)
            pass
        except Exception, e:
            raise e
        finally:
            return res
