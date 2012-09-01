# -*- coding: utf-8 -*-

#
# Copyright (c) 2010 MatToufoutu
#

"""
virtualenvwrapper.project plugin for github repositories
"""

from __future__ import print_function

import os

from git import *
from github import Github, GithubException
from github.GithubObject import NotSet


def get_environment():
    """
    Get required environment variables.
    """
    env_is_ok = True
    github_user = os.environ.get('GITHUB_USER')
    if github_user is None:
        print('GITHUB_USER not found')
        print('Add \'export GITHUB_USER="username"\' to your .bashrc')
        env_is_ok = False
    api_token = os.environ.get('GITHUB_API_TOKEN')
    if api_token is None:
        print('GITHUB_API_TOKEN not found')
        print('Add \'export GITHUB_API_TOKEN"=api_token"\' to your .bashrc')
        env_is_ok = False
    if not env_is_ok:
        return None
    return github_user, api_token


def template(args):
    """
    Creates a GitHub repository into the project directory,
    if the GitHub project still exists, clone the repository.
    """
    prj_name = args[0]
    print('Initializing git repository and creating GitHub project for %s' % prj_name)
    # src_dir = os.path.join(os.getcwd(), 'src')
    src_dir = os.getcwd()

    env_vars = get_environment()
    if env_vars is None:
        print('Repository was not created')
        return

    username, api_token = env_vars
    github = Github(api_token)
    github_user = github.get_user()
    try:
        repo = github_user.get_repo(prj_name)
        repo_exists = True
    except GithubException:
        repo_exists = False

    if repo_exists:
        print('Repository already exists on GitHub')
        print('[C]lone or [A]bort? ', end='')
        choice = raw_input().lower()
        if choice == 'c':
            print('Cloning repository from %s' % repo.clone_url)
            try:
                # # delete src folder to prevent error when cloning (will be re-created by the clone command)
                # if os.path.exists(src_dir):
                #     os.rmdir(src_dir)
                Repo.clone_from(repo.clone_url, src_dir)
                repo_created = True
            except GitCommandError:
                print('An error occured while cloning the repository')
                if os.path.exists(os.path.join(src_dir, '.git')):
                    os.rmdir(os.path.join(src_dir, '.git'))
                repo_created = False
        else:
            repo_created = False

    else:
        prj_desc = raw_input('Project description (default=None): ')
        prj_url = raw_input('Project homepage (default=None): ')
        github_user.create_repo(
                prj_name,
                description=prj_desc or NotSet,
                homepage=prj_url or NotSet,
        )
        repo = Repo.init(src_dir)
        ## TODO: get this from the repo object?
        git_url = 'git@github.com:%s/%s.git' % (username, prj_name)
        repo.create_remote('origin', git_url)
        repo_created = True
    if repo_created:
        print('Repository was successfuly created')
    else:
        print('Repository was not created')
    return
