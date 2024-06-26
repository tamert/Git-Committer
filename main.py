import git
import requests
import os
import time
import click

ollama_api_root = 'http://localhost:11434'


def success(message):
    print('\033[92m ======== %s ======== \033[0m' % message)


def warning(message):
    print('\033[93m ======== %s ======== \033[0m' % message)


def alert(message):
    print('\033[91m ======== %s ======== \033[0m' % message)


@click.command()
@click.option('--fast', default=False, help='Run in fast mode', is_flag=True)
@click.option('-f', default=False, help='Run in fast mode' + ' (alias for --fast)', is_flag=True)
def hello(fast=False, f=False):
    time_start = time.time()
    if fast or f:
        fast = True

    print('🐙 Hello, This is Git Committer!')

    path = os.getcwd() + '/.git'
    print('Looking for git repo: %s' % path)
    if not os.path.exists(path):
        alert('Current directory is not a git repo')
        exit(1)
    from_repo = git.Repo(path)
    if not from_repo:
        alert('The git repo is not valid')
        exit(1)

    active_branch = from_repo.active_branch
    # get current branch
    print('Active branch: %s' % active_branch)

    # check ollama is running
    print('Checking ollama')
    try:
        result = requests.get(ollama_api_root)
    except Exception as e:
        alert('Ollama is not running')
        print('Please run "ollama run mistral"')
        exit(1)

    if result.status_code != 200 or result.text != 'Ollama is running':
        alert('Ollama is not running')
        print('Please run "ollama run mistral"')
        exit(1)
    else:
        print('Ollama is running...')

    # get diff between branches
    diff = from_repo.git.diff('origin/%s' % active_branch)

    if diff:
        prompt = 'You are a machine which return a Git commit message. You use different as the programming language. I\'ll provide you with the code before and after the changes, so please give me the best commit message.'
        if fast:
            prompt = 'You are a machine which return a Git commit message. Only the code before and after the changes, so please give me a basic commit message, fastly.'

        # send mistral with request
        prompt += '\n\n' + diff
        payload = {'model': 'mistral', 'stream': False, 'prompt': prompt}
        result = requests.post('%s/api/generate' % ollama_api_root, json=payload)
        # Response Json
        data = result.json()
        # print color green
        success('SUCCESS')
        print(data['response'])
        time_diff = time.time() - time_start
        warning('The passing time is %s:%s' % (round(time_diff // 60), round(time_diff % 60)))

    else:
        # print color red
        alert('NO CHANGES')

    exit(0)


if __name__ == '__main__':
    hello()
