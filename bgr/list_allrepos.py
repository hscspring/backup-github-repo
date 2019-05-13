import argparse
import requests
from pnlp import piop
from backup import GitRepo
from pyhocon import ConfigFactory


class ListRepos(GitRepo):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_repos(self, url: str):
        suffix = "?page="
        items = self.get_items(url, suffix)
        all_repos = [_['full_name'] for _ in items]
        return all_repos


def main():

    ap = argparse.ArgumentParser()
    ap.add_argument("-P", "--out_path", default="./backup_data",
                    help="back up out path.")
    ap.add_argument("-I", "--info", default=False,
                    help="if watch, star, folks info needed.")
    args = vars(ap.parse_args())

    conf = ConfigFactory.parse_file("env.conf")
    username = conf.get('username')
    password = conf.get('password')
    token = conf.get('token')

    out_path = args['out_path']
    if_info = args['info']

    url = "https://api.github.com/user/repos"
    repo = ListRepos(username, password, token)
    all_repos = repo.get_repos(url)

    out = []
    for rname in all_repos:
        line = "python backup.py -O " + rname
        line = line + " -P " + out_path + " -I " + if_info
        out.append(line)
    piop.write_file('batch.sh', out)


if __name__ == '__main__':
    main()
