"""
    team module for maintaining team
"""

from . import BitbucketAcl


class Group(BitbucketAcl):
    """Class for maintaining a group in team"""
    def __init__(self, slug=None, team_name='', team=None, group_json=None,):
        """Constructor
                Args:
                    slug: group slug
                    team_name: name of the team who owns the group
                    team: Team object which owns the group
                    group_json: group detail with json format and
                                will be translated to Group object
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
        res = BitbucketAcl.access_api(self, url=url, method=method,
                                      data=data, auth=self.auth)
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
            url = ('{}{}/{}/members/'.format(base_url, account_name,
                                             group_slug))
            res = self.access_api(url=url)
            self.members = res.json()
        return self.members

    def __delete_member(self, username):
        """ Call access_api for delete member purpose
                Return:
                    response
        """
        base_url = 'https://bitbucket.org/api/1.0/groups/'
        url = ('{}{}/{}/members/{}'.format(base_url, self.team_name,
                                           self.slug, username))
        res = self.access_api(method='DELETE', url=url)
        return res

    def remove_member(self, *usernames):
        """Remove member(s) from group
                Args:
                    *usernames: list of usernames that will be
                                removed from group
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
        url = ('{}{}/{}/members/{}/'.format(base_url, self.team_name,
                                            self.slug, username))
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


class Team(BitbucketAcl):
    """Class to manage team in bitbucket"""
    def __init__(self, team_slug=None, username=None, password=None):
        """Constructor
                Args:
                    team_slug: Team's slug
                    username : username for authentication
                               (can be generated from its parent)
                    password : password for authentication
        """
        BitbucketAcl.__init__(self, username=username, password=password)
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
        res = BitbucketAcl.access_api(self, url=url, method=method,
                                      data=data, auth=self.auth)
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
        elif group_slug != '':
            return Group(team=self, slug=group_slug)
        else:
            raise ValueError("group_slug or group_json must be specified")

    def get_groups(self):
        """Get list of groups
                Return: list of groups with json format
        """
        base_url = 'https://bitbucket.org/api/1.0/groups/'
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
        url = ('{}{}/{}/{}/{}'.format(base_url, account_name,
                                      repo_slug, group_owner, group_slug))
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
        base_url = 'https://bitbucket.org/api/1.0/group-privileges/'
        account_name = self.team_slug
        group_owner = account_name
        url = ('{}{}/{}/{}/{}'.format(base_url, account_name,
                                      repo_slug, group_owner, group_slug))
        method = 'DELETE'
        res = self.access_api(url=url, method=method)
        return res

    def remove_all_group_privileges(self, *group_slugs):
        """Delete privilege for a group across all team repositories
                Args:
                    *group_slugs: list of group slugs that its privilege
                                  will be removed
                Return:
                    response
        """
        base_url = 'https://bitbucket.org/api/1.0/group-privileges/'
        account_name = self.team_slug
        group_owner = account_name
        res = []
        for group_slug in group_slugs:
            url = ('{}{}/{}/{}'.format(base_url, account_name,
                                       group_owner, group_slug))
            method = 'DELETE'
            _res = self.access_api(url=url, method=method)
            res.append(_res.status_code)
        return res

    def add_member_to_groups(self, username, *group_slugs):
        """Add member to multiple groups
                Args:
                    username    : username of account that will be
                                  added to groups
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

    def remove_member_from_groups(self, username, *group_slugs):
        """Remove member from multiple groups
                Args:
                    username    : username of account that will be
                                  removed from group
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
                    *usernames: list of usernames that will be
                                removed from group
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
