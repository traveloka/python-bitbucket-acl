"""
    Group module
"""

from . import BitbucketAcl
from .team import *

class Group(BitbucketAcl):

    def __init__(self, slug=None, team=None, group_json=None):
        BitbucketAcl.__init__(self)
        self.slug = slug
        self.team = team
        self.members = None
        if group_json is not None:
            print group_json
            self.name = group_json['name']
            self.slug = group_json['slug']
        pass

    # Access api, call its super's method (BitbucketAcl)
    def access_api(self, url=None, method='', data=None):
        res = BitbucketAcl.access_api(self, url=url, method=method, data=data, auth=self.auth)
        return res

    # Get members of the group, return list of member with json format
    def get_members(self):
        if self.members is None:
            base_url = 'https://bitbucket.org/api/1.0/groups/'
            account_name = self.team.team_slug
            group_slug = self.slug
            url = ('{}{}/{}/members/'.format(base_url, account_name, group_slug))
            res = self.access_api(url=url)
            self.members = res.json()
            return res
        return self.members


    # Method for accessing access_api that receives only one username
    # only for delete a member purpose
    def __delete_member(self, username):
        base_url = 'https://bitbucket.org/api/1.0/groups/'
        url = ('{}{}/{}/members/{}'.format(base_url, self.team.team_slug, self.slug, username))
        res = self.access_api(method='DELETE', url=url)
        return res

    # Remove member(s) from group, return booelan
    # True if nothing wrong happened, otherwise return False
    # with parameter username, can be list or string
    # NOTE: for list as parameter hasn't tested yet
    def remove_member(self, username):
        flag = True
        if type(username) == list:
            for _username in username:
                res = self.__delete_member(_username)
                if res.status_code != 204:
                    flag = False
            return flag

        return True if self.__delete_member(username).status_code == 204 else False

    # Method for accessing access_api that recieves only one username
    # only for put a member
    # for cleaner code :)
    def __put_member(self, username):
        base_url = 'https://bitbucket.org/api/1.0/groups/'
        url = ('{}{}/{}/members/{}/'.format(base_url, self.team.team_slug, self.slug, username))
        res = self.access_api(url=url, method='PUT', data='{}')
        return res

    # Add member(s) to group, return requests.response
    # with parameter username, can be list or string
    def add_member(self, username):
        flag = True
        if type(username) == list:
            for _username in username:
                res = self.__put_member(_username)
                if res.status_code != 200:
                    flag = False
            return flag

        return True if self.__put_member(username).status_code == 200 else False
        pass
