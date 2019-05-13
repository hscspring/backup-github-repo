import argparse
from git import Repo
import json
import os
import random
import requests
import time
from pyhocon import ConfigFactory


class GitRepo:

    base_api = "https://api.github.com/repos"

    def __init__(self, username: str, password: str, token: str = ""):
        self.auth = (username, password)
        self.token = token
        self.token_api = "https://" + self.token + ":x-oauth-basic@github.com"
        self.headers = {'Accept': 'application/vnd.github.v3+json', }
        if len(self.token) > 0:
            self.headers.update({'Authorization': 'token ' + self.token})

    def __repr__(self) -> str:
        return "GitRepo(username=%r)" % (self.username)

    @classmethod
    def get(cls, url: str, headers: dict, auth: tuple = ()):
        resp = requests.get(url, auth=auth, headers=headers)
        if resp.status_code != 200:
            print("Error: ", resp.json())
            return [], resp.links
        else:
            return resp.json(), resp.links

    def get_info(self, orgrepo_name: str, info_type: str) -> list:
        suffix = "?page="
        info_url = "/".join((self.base_api, orgrepo_name, info_type))
        info = self.get_items(info_url, suffix)
        return info

    def clone(self, orgrepo_name: str, to_path: str, wiki=False):
        if wiki:
            suffix = ".wiki.git"
        else:
            suffix = ".git"
        url = "/".join((self.token_api, orgrepo_name)) + suffix
        try:
            Repo.clone_from(url, to_path)
        except Exception as e:
            print("Error: ", e)

    def get_issues(self, orgrepo_name: str) -> list:
        suffix = "&page="
        url = "/".join((self.base_api, orgrepo_name, "issues?state=all"))
        issues = self.get_items(url, suffix)
        print("issues done, we got %d issues." % len(issues))
        print("comments for each issue start...")
        if len(issues) > 0:
            for i, issue in enumerate(issues):
                print("\tcomments for No.%d issue done..." % (i+1))
                issue['comments_items'] = self.get_comments(issue)
        return issues

    def get_comments(self, issue: str) -> list:
        suffix = "?page="
        comments_url = issue['comments_url']# + '?page=1&per_page=100'
        comments = self.get_items(comments_url, suffix)
        return comments

    def get_items(self, item_url: str, suffix: str) -> list:
        try:
            items, links = self.get(item_url, self.headers)
        except Exception as e:
            print("Error: ", e)
            items, links = [], {}

        try:
            pnum = int(links['last']['url'].split("page=")[-1])
        except KeyError as e:
            pnum = 0

        if pnum > 1:
            time.sleep(random.randint(1,3))
            for p in range(2, pnum+1):
                url = item_url + suffix + str(p)
                resp_items, _ = self.get(url, self.headers)
                time.sleep(random.randint(1,3))
                items.extend(resp_items)
        
        # while 1:
        #     nextlink = links['next']['url']
        #     resp_items, links = self.get(nextlink, self.headers)
        #     items.extend(resp_items)

        return items

def write_json(fpath: str, data, **kwargs):
    fout = open(fpath, 'w')
    json.dump(data, fout, **kwargs)
    fout.close()


def check_dir(dirname: str):
    if os.path.exists(dirname):
        pass
    else:
        os.makedirs(dirname)


def main():

    ap = argparse.ArgumentParser()
    ap.add_argument("-O", "--orgrepo_name",
                    help="orgrepo name. for example: org/repo")
    ap.add_argument("-P", "--out_path", default="./backup_data",
                    help="back up out path.")
    ap.add_argument("-I", "--info", default=False,
                    help="if watch, star, folks info needed.")
    args = vars(ap.parse_args())

    conf = ConfigFactory.parse_file("env.conf")

    username = conf.get('username')
    password = conf.get('password')
    token = conf.get('token')

    orgrepo_name = args['orgrepo_name']
    out_path = args['out_path']
    if_info = args['info']

    repo_path = os.path.join(out_path, orgrepo_name)
    info_path = os.path.join(repo_path, "info")
    code_path = os.path.join(repo_path, "code")
    issue_path = os.path.join(repo_path, "issue")
    wiki_path = os.path.join(repo_path, "wiki")

    check_dir(repo_path)
    check_dir(info_path)
    check_dir(code_path)
    check_dir(issue_path)
    check_dir(wiki_path)

    repo = GitRepo(username, password, token)

    if if_info:
        print("Processing Info of %s ..." % orgrepo_name)
        watchers = repo.get_info(orgrepo_name, "subscribers")
        starers = repo.get_info(orgrepo_name, "stargazers")
        forkers = repo.get_info(orgrepo_name, "forks")
        write_json(os.path.join(info_path, "watchers.txt"),
                   watchers, indent=4, ensure_ascii=False)
        write_json(os.path.join(info_path, "starers.txt"),
                   starers, indent=4, ensure_ascii=False)
        write_json(os.path.join(info_path, "forkers.txt"),
                   forkers, indent=4, ensure_ascii=False)

    print("Cloning Code of %s ..." % orgrepo_name)
    repo.clone(orgrepo_name, code_path)
    print("Cloning Wiki of %s ..." % orgrepo_name)
    repo.clone(orgrepo_name, wiki_path, wiki=True)

    print("Processing Issues of %s ..." % orgrepo_name)
    issues = repo.get_issues(orgrepo_name)
    for issue in issues:
        fname = "_".join((issue['state'],
                          str(issue['number']), issue['title'])) + ".txt"
        fname = fname.replace("/", "-")
        fname = fname.replace(".", "-")
        fname = fname.replace(" ", "-")
        if len(fname) > 255:
            fname = fname[:50] + "xxx" + fname[-50:]
        fpath = os.path.join(issue_path, fname)
        write_json(fpath, issue, indent=4, ensure_ascii=False)


if __name__ == '__main__':
    main()
