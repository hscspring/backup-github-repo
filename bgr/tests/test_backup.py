import os
import sys
import pytest
import types
from pyhocon import ConfigFactory

ROOT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_PATH)

from backup import GitRepo, check_dir

conf_path = os.path.join(ROOT_PATH, "env.conf")
conf = ConfigFactory.parse_file(conf_path)
username = conf.get('username')
password = conf.get('password')
token = conf.get('token')


@pytest.fixture
def get_orgrepo():
    return "AIHackers/NLP101.OC"

def test_get():
    repo =GitRepo(username, password, token)
    url = "https://api.github.com/user"
    headers = {'Accept': 'application/vnd.github.v3+json', }
    headers.update({'Authorization': 'token ' + token})
    resp, links = repo.get(url, headers)
    assert type(resp) == dict
    assert type(links) == dict

def test_get_info(get_orgrepo):
    repo =GitRepo(username, password, token)
    resp = repo.get_info(get_orgrepo, "stargazers")
    assert type(resp) == list
    assert len(resp) == 1


def test_clone(get_orgrepo):
    code_path = os.path.join(ROOT_PATH, "tests", "test_clone_data")
    check_dir(code_path)
    repo =GitRepo(username, password, token)
    repo.clone(get_orgrepo, code_path)
    assert "README.md" in os.listdir(code_path)

def test_get_issues(get_orgrepo):
    repo =GitRepo(username, password, token)
    issues = repo.get_issues(get_orgrepo)
    assert type(issues) == list
    assert len(issues) == 2
    assert type(issues[0]) == dict
    assert type(issues[0]['comments_items']) == list


if __name__ == '__main__':
    print(ROOT_PATH)
