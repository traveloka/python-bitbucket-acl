"""
    team module for maintaining team
"""

from . import BitbucketAcl
from .group import *


class Team(BitbucketAcl):
    """Class to manage team in bitbucket"""
    def __init__(self, team_slug=None, username=None, password=None):
        """Constructor
                Args:
                    team_slug: Team's slug
                    username : username for authentication (can be generated from its parent)
                    password : password for authentication
        """
        BitbucketAcl.__init__(self,username=username, password=password)
        self.team_slug = team_slug
        self.__verify()
        pass

    def __verify(self):
        """Verify whether team is valid or not"""
        base_url = 'https://bitbucket.org/api/1.0/users/'
        url = '{}{}'.format(base_url, self.team_slug)
        res = self.access_api(url=url)
        if res.status_code != 200:
            raise ValueError('Invalid team_name')


    def access_api(self, url=None, method='', data=None):
        """ Access api, call its super's method (BitbucketAcl)"""
        res = BitbucketAcl.access_api(self, url=url, method=method, data=data, auth=self.auth)
        return res


    def get_group(self, group_slug='', group_json=None):
        """Get a group in a team
                Args:
                    group_slug: Group's slug
                    group_jsonL group detail with json format
                Return:
                    Group object
        """
        if group_json is not None:
            return Group(team=self, group_json=group_json)
        if group_slug != '':
            base_url = 'https://bitbucket.org/api/1.0/groups/'
            account_name = self.team_slug
            url = ('{}{}/{}/'.format(base_url, account_name, group_slug))
            res = self.access_api(url=url)
            return Group(team=self, slug=group_slug)


    def get_groups(self):
        """Get list of groups
                Return: list of groups with json format
        """
        base_url = 'https://bitbucket.org/api/1.0/groups/'
        account_name = self.team_slug
        url = ('{}{}'.format(base_url, self.team_slug))
        res = self.access_api(url=url)
        return res.json()


    def get_group_members(self, group_slug=''):
        """Get member of groups
                Args:
                    group_slug: group slug
                Return:
                    list of members of group with json format
        """
        base_url = 'https://bitbucket.org/api/1.0/groups/'
        account_name = self.team_slug
        url = ('{}{}/{}/members/'.format(base_url, account_name, group_slug))
        res = self.access_api(url=url)
        return res.json()


    def get_repositories(self):
        """Get team repositories
                Return:
                    list of repositories with json format
        """
        base_url = 'https://api.bitbucket.org/2.0/repositories/'
        team_name = self.team_slug
        url = ('{}{}/'.format(base_url, team_name))
        res = self.access_api(url=url)
        temp_res = res.json()
        repo = []
        # maintaining list-based pagination
        if 'next' in temp_res:
            while True:
                repo += temp_res['values']
                if 'next' not in temp_res:
                    break
                url = temp_res['next']
                res = self.access_api(url=url)
                temp_res = res.json()
            return repo
        return res.json()['values']


    def grant_group_privilege(self, group_slug, repo_slug, role='read'):
        """Put privilege for a group in a repository with given role
                Args:
                    group_slug: group that will be given a privilege
                    repo_slug : repository destination
                    role      : Role access for group, default is read
                Return:
                    response
        """
        base_url = 'https://bitbucket.org/api/1.0/group-privileges/'
        account_name = self.team_slug
        group_owner = account_name
        url = ('{}{}/{}/{}/{}'.format(base_url, account_name, repo_slug, group_owner, group_slug))
        method = 'PUT'
        data = role
        res = self.access_api(url=url, method=method, data=data)
        return res

    def remove_group_privilege(self, group_slug, repo_slug):
        """ Delete privilege for a group in repository
                Args:
                    group_slug: group that its privilege will be removed
                    repo_slug : repository destination
                Return:
                    response
        """
        if repo_slug == '':
            return self.remove_all_group_privileges(group_slug=group_slug)
        base_url= 'https://bitbucket.org/api/1.0/group-privileges/'
        account_name = self.team_slug
        group_owner = account_name
        url = ('{}{}/{}/{}/{}'.format(base_url, account_name, repo_slug, group_owner, group_slug))
        method = 'DELETE'
        res = self.access_api(url=url, method=method)
        return res


    def remove_all_group_privileges(self, *group_slugs):
        """Delete privilege for a group across al team repositories
                Args:
                    *group_slugs: list of group slugs that its privilege will be removed
                Return:
                    response
        """
        base_url = 'https://bitbucket.org/api/1.0/group-privileges/'
        account_name = self.team_slug
        group_owner = account_name
        res = []
        for group_slug in group_slugs:
            url = ('{}{}/{}/{}'.format(base_url, account_name, group_owner, group_slug))
            method = 'DELETE'
            res += self.access_api(url=url, method=method)
        return res


    def add_member_to_groups(self, username, *group_slugs):
        """Add member to multiple groups
                Args:
                    username    : username of account that will be added to groups
                    *group_slugs: list of group slugs destination
                Return:
                    Boolean that decides something wrong happened or not
        """
        flag = True
        for group_slug in group_slugs:
            try:
                group = Group(group_slug, self.team_slug)
                group.add_member(username)
            except Exception as e:
                print e
                flag = False

        return flag


    def add_members_to_group(self, group_slug, *usernames):
        """ Add multiple members to group
                Args:
                    group_slug: group slug destination
                    *usernames: list of usernames that will be added to group
                Return:
                    Boolean that decides something wrong happened or not
        """
        flag = True
        try:
            group = Group(group_slug, self.team_slug)
        except Exception as e:
            print e
            flag = False
        group.add_member(*usernames)
        return flag


    def remove_member_from_groups(self, username, *groups_slug):
        """Remove member from multiple groups
                Args:
                    username    : username of account that will be removed from group
                    *groups_slug: list of group_slugs destination
                Return:
                    Boolean that decides something wrong happened or not
        """
        flag = True
        for group_slug in group_slugs:
            try:
                group = Group(group_slug, self.team_slug)
                group.remove_member(username)
            except Exception as e:
                print e
                flag = False

        return flag


    def remove_members_from_group(self, group_slug, *usernames):
        """Remove multiple members from a group
                Args:
                    group_slug: group slug destination
                    *usernames: list of usernames that will be removed from group
                Return:
                    Boolean that decides something wrong happened or not
        """
        flag = True
        try:
            group = Group(group_slug, self.team_slug)
        except Exception as e:
            print e
            flag = False
        group.remove_member(*usernames)
        return flag
