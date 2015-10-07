"""
    Group module
"""

from . import BitbucketAcl
from .team import *

class Group(BitbucketAcl):
    """Class for maintaining a group in team"""
    def __init__(self, slug=None, team_name='', team=None, group_json=None,):
        """Constructor
                Args:
                    slug: group slug
                    team_name: name of the team who owns the group
                    team: Team object which owns the group
                    group_json: group detail with json format and will be translated to Group object
        """

        # Call parent's constructor
        BitbucketAcl.__init__(self)
        self.slug = slug
        self.team = team
        self.team_name = team.team_slug if team is not None else team_name
        self.members = None
        if group_json is not None:
            self.name = group_json['name']
            self.slug = group_json['slug']

        # Checking if it is valid or not
        exist = self.__verify()
        if not exist:
            raise ValueError('Invalid group_slug or team_name')
        self.get_members()
        pass


    def __verify(self):
        """Verify whether given group_slug and team_name is valid or not"""
        base_url = 'https://bitbucket.org/api/1.0/groups/'
        url = '{}{}/{}'.format(base_url, self.team_name, self.slug)
        res = self.access_api(url=url)
        if res.status_code != 200:
            return False
        return True


    def access_api(self, url=None, method='', data=None):
        """ Access api, call its super's method (BitbucketAcl)"""
        res = BitbucketAcl.access_api(self, url=url, method=method, data=data, auth=self.auth)
        return res


    def get_members(self):
        """ Get members of the group
                Return:
                    json of list of members
        """
        if self.members is None:
            base_url = 'https://bitbucket.org/api/1.0/groups/'
            account_name = self.team_name
            group_slug = self.slug
            url = ('{}{}/{}/members/'.format(base_url, account_name, group_slug))
            res = self.access_api(url=url)
            self.members = res.json()
        return self.members


    def __delete_member(self, username):
        """ Call access_api for delete member purpose
                Return:
                    response
        """
        base_url = 'https://bitbucket.org/api/1.0/groups/'
        url = ('{}{}/{}/members/{}'.format(base_url, self.team_name, self.slug, username))
        res = self.access_api(method='DELETE', url=url)
        return res


    def remove_member(self, *usernames):
        """Remove member(s) from group
                Args:
                    *usernames: list of usernames that will be removed from group
                Return:
                    True if nothing wrong happened, otherwise False
        """
        flag = True
        for username in usernames:
            res = self.__delete_member(username)
            if res.status_code != 204:
                flag = False
        return flag


    def __put_member(self, username):
        """Call access_api for put member purpose
                Return:
                    response
        """
        base_url = 'https://bitbucket.org/api/1.0/groups/'
        url = ('{}{}/{}/members/{}/'.format(base_url, self.team_name, self.slug, username))
        res = self.access_api(url=url, method='PUT', data='{}')
        return res


    def add_member(self, *usernames):
        """Add member(s) to group
                Args:
                    *usernames: list of usernames that will be added to group
                Return:
                    True if nothing wrong happened, otherwise False
        """
        flag = True
        for username in usernames:
            res = self.__put_member(username)
            if res.status_code != 200:
                flag = False
        return flag

