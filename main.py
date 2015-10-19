import click
import yaml
from bitbucketacl.team import Team


@click.group()
def acl():
    pass


@acl.command()
@click.argument('groups', nargs=-1)
@click.option('--repo', required=True)
@click.option('--role', default='read')
@click.option('--all', default=False, is_flag=True)
@click.option('--allgroups', default=False, is_flag=True)
def addprivilege(groups, repo, role, all, allgroups):
    if allgroups:
        groups_json = t.get_groups()
        groups_name = map(lambda group: group['slug'], groups_json)
        for group in groups_name:
            t.grant_group_privilege(group, repo, role)
    else:
        for group in groups:
            t.grant_group_privilege(group, repo, role)


@acl.command()
@click.argument('groups', nargs=-1)
@click.option('--repo', nargs=1)
@click.option('--all', default=False, is_flag=True)
@click.option('--allgroups', default=False, is_flag=True)
def removeprivilege(groups, repo, all, allgroups):
    if allgroups:
        groups_json = t.get_groups()
        groups_name = map(lambda group: group['slug'], groups_json)
        for group in groups_name:
            t.remove_group_privilege(group, repo)
    else:
        for group in groups:
            if all:
                t.remove_all_group_privileges(group)
            elif repo is not None:
                t.remove_group_privilege(group, repo)


@acl.command()
@click.option('--list', '_list', default=False, is_flag=True)
def group(_list):
    if _list:
        groups_json = t.get_groups()
        groups_name = map(lambda group: group['slug'], groups_json)
        for group_name in groups_name:
            print group_name


@acl.command()
@click.argument('usernames', nargs=-1, required=True)
@click.option('--group', required=True)
def addmember(usernames, group):
    t.add_members_to_group(group, *(usernames))


@acl.command()
@click.argument('usernames', nargs=-1, required=True)
@click.option('--group', required=True)
def removemember(usernames, group):
    t.remove_members_from_group(group, *(usernames))


if __name__ == '__main__':
    team_name = yaml.load(file('bitbucket.conf'))['TEAM_NAME']
    t = Team(team_name)
    acl()
