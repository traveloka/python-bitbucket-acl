"""
    team module for maintaining team
"""

from . import BitbucketAcl
from .group import *

# Team class to manage team in bitbucket
# most of process related to its groups
# with BitbucketAcl as its parent class
class Team(BitbucketAcl):
    def __init__(self, team_slug=None, username=None, password=None):
        BitbucketAcl.__init__(self,username=username, password=password)
        self.team_slug = team_slug
        self.__verify()
        pass

    def __verify(self):
        base_url = 'https://bitbucket.org/api/1.0/users/'
        url = '{}{}'.format(base_url, self.team_slug)
        res = self.access_api(url=url)
        if res.status_code != 200:
            raise ValueError('Invalid team_name')

    # Method to request api, call its super method
    # with parameter url, method type, data
    def access_api(self, url=None, method='', data=None):
        res = BitbucketAcl.access_api(self, url=url, method=method, data=data, auth=self.auth)
        return res

    def get_group(self, group_slug='', group_json=None):
        if group_json is not None:
            return Group(team=self, group_json=group_json)
        if group_slug != '':
            base_url = 'https://bitbucket.org/api/1.0/groups/'
            account_name = self.team_slug
            url = ('{}{}/{}/'.format(base_url, account_name, group_slug))
            res = self.access_api(url=url)
            return Group(team=self, slug=group_slug)

    # Get list of groups in team, return json
    # if succeed, res.status_code == 200
    def get_groups(self):
        base_url = 'https://bitbucket.org/api/1.0/groups/'
        account_name = self.team_slug
        url = ('{}{}'.format(base_url, self.team_slug))
        res = self.access_api(url=url)
        return res.json()

    # Get members of group, return json
    # with parameter group_slug
    # if succeed, res.status_code == 200
    def get_group_members(self, group_slug=''):
        base_url = 'https://bitbucket.org/api/1.0/groups/'
        account_name = self.team_slug
        url = ('{}{}/{}/members/'.format(base_url, account_name, group_slug))
        res = self.access_api(url=url)
        return res.json()

    # Get list of team's repositories, return json
    # if succeed, res.status_code == 200
    def get_repositories(self):
        base_url = 'https://api.bitbucket.org/2.0/repositories/'
        team_name = self.team_slug
        url = ('{}{}/'.format(base_url, team_name))
        res = self.access_api(url=url)
        temp_res = res.json()
        repo = []
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

    # Put privilege for a group in a repository with role, return requests.response
    # with parameter group_slug, repo_slug and role
    # if succeed, res.status_code == 200
    def grant_group_privilege(self, group_slug, repo_slug, role='read'):
        base_url = 'https://bitbucket.org/api/1.0/group-privileges/'
        account_name = self.team_slug
        group_owner = account_name
        url = ('{}{}/{}/{}/{}'.format(base_url, account_name, repo_slug, group_owner, group_slug))
        method = 'PUT'
        data = role
        res = self.access_api(url=url, method=method, data=data)
        return res

    # Delete privilege for a group in repository, return requests.response
    # with parameter group_slug and remove privilege across team repositories
    # if succeed, res.status_code == 204
    def remove_group_privilege(self, group_slug, repo_slug):
        if repo_slug == '':
            return self.remove_all_group_privileges(group_slug=group_slug)
        base_url= 'https://bitbucket.org/api/1.0/group-privileges/'
        account_name = self.team_slug
        group_owner = account_name
        url = ('{}{}/{}/{}/{}'.format(base_url, account_name, repo_slug, group_owner, group_slug))
        method = 'DELETE'
        res = self.access_api(url=url, method=method)
        return res

    # Delete privilege for a group across all team repositories, return requests.response
    # with parameter group_slug
    # if succeed, res.status_code == 204
    def remove_all_group_privileges(self, *group_slugs):
        base_url = 'https://bitbucket.org/api/1.0/group-privileges/'
        account_name = self.team_slug
        group_owner = account_name
        res = []
        for group_slug in group_slugs:
            url = ('{}{}/{}/{}'.format(base_url, account_name, group_owner, group_slug))
            method = 'DELETE'
            res += self.access_api(url=url, method=method)
        return res

    # Add member to multiple groups
    # with parameter username and group_slugs (*args)
    def add_member_to_groups(self, username, *group_slugs):
        flag = True
        for group_slug in group_slugs:
            try:
                group = Group(group_slug, self.team_slug)
                group.add_member(username)
            except Exception as e:
                print e
                flag = False

        return flag


    # Add multiple members to group
    # with parameter group_slug and usernames (*args)
    def add_members_to_group(self, group_slug, *usernames):
        flag = True
        try:
            group = Group(group_slug, self.team_slug)
        except Exception as e:
            print e
            flag = False
        group.add_member(*usernames)
        return flag

    # Remove member from multiple groups
    # with parameter username and group_slugs (*args)
    def remove_member_from_groups(self, username, *groups_slug):
        flag = True
        for group_slug in group_slugs:
            try:
                group = Group(group_slug, self.team_slug)
                group.remove_member(username)
            except Exception as e:
                print e
                flag = False

        return flag


    # Remove multiple members from group
    # with parameter group_slug and usernames (*args)
    def remove_members_from_group(self, group_slug, *usernames):
        flag = True
        try:
            group = Group(group_slug, self.team_slug)
        except Exception as e:
            print e
            flag = False
        group.remove_member(*usernames)
        return flag
