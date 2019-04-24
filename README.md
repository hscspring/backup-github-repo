# backup-github-repo
This is a simple tool to backup a github repo.

## Features

- watch, star, fork info preserve
- code clone
- wiki clone (if exist)
- issues and comments preserve

## Install

If you have [pipenv](https://github.com/pypa/pipenv), it's easy to use `pipenv install` to install all the dependences, then you can use `pipenv shell` to enter the virtual environment. 

Also, you could directly install all the dependences to your system using this command: `pipenv install --system --deploy`.

Otherwise, `pip install -r requirements.txt` will be OK.

## Usage

First of all, edit the `env.conf` to add authentication info. Pay attention, `token` is necessary, `username` and `password` could be empty.

Here are some steps to generate a token:

- Login `https://github.com` 
- Enter `Settings -> Developer settings -> Personal access tokens -> Generate new token`
- Enter a description ,whatever you like.
- Select scopes following the [help](https://developer.github.com/apps/building-oauth-apps/understanding-scopes-for-oauth-apps/), or simply you could select all of them.

```bash
python backup.py [OPTIONS]

Options:
	-O or --orgrepo_name	orgrepo name, like AIHackers/IAOC, username/reponame
	-P or --out_path		directory to save your repo, default is "./backup_data
	-I or --info			whether to save watch, star and folk info, default is False

Examples:
Backup repo, wiki, and issues to ./backup_data
$ python backup.py -O AIHackers/IAOC
Backup repo, wiki, issues and info to ~/backup_data
$ python backup.py -O AIHackers/IAOC -P ~/backup_data -I True

The final directory tree is like (cd ~/backup_data):
.
└── AIHackers
    └── IAOC
    	├── code
    	│   ├── README.md
    	│   ├── ...
        └── info
        │   ├── forkers.txt
        │   ├── starers.txt
        │   └── watchers.txt
        └── issue
        │   ├── open_0_Hello1.txt // state + number + title for each issue
        │   ├── closed_1_Hello2.txt // state + number + title for each issue
        │   ├── ...
        └── wiki
        │   ├── README.md
    	│   ├── ...
```

