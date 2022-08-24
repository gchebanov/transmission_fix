import re
import requests
from pathlib import Path, PurePath
from win32_setctime import setctime
from tabulate import tabulate
from configparser import ConfigParser
import pandas as pd

XT = 'X-Transmission-Session-Id'

cfg = ConfigParser()
with open('cfg.ini') as f:
    cfg.read_file(f)
    auth = cfg['auth']
    login = auth['login']
    password = auth['password']
    url = cfg['default']['url']
    XV = auth.get('XV', 'A' * 48)


def api(*args, **kwargs):
    global XV
    kwargs.setdefault('url', url)
    kwargs.setdefault('auth', (login, password))
    kwargs.setdefault('headers', {}).setdefault(XT, XV)
    r = requests.post(*args, **kwargs)
    if r.status_code == 409:
        print(r.text)
        print(f'old {XV=}')
        XV = re.search('Id: ([0-9a-zA-Z])+<', r.text).group()[4:-1]
        print(f'new {XV=}')
        with open('cfg.ini', 'wt') as f:
            cfg.set('auth', 'XV', XV)
            cfg.write(f)
        kwargs.setdefault('headers', {}).setdefault(XT, XV)
        r = requests.post(*args, **kwargs)
        assert r.status_code != 409
    return r


def process(e, dry_run, ignore_time_diff=3600):
    ddir = Path(e['downloadDir'])
    roots = set()
    for file in e['files']:
        roots.add(ddir / PurePath(file['name']).parts[0])
    added_date = e['addedDate']
    for r in roots:
        st = r.stat()
        if abs(st.st_ctime - added_date) < ignore_time_diff:
            break
        print(r)
        print(f'atime={st.st_atime - added_date} mtime={st.st_mtime - added_date} ctime={st.st_ctime - added_date}')
        if not dry_run:
            setctime(r, added_date)
            st = r.stat()
            print(f'atime={st.st_atime-added_date} mtime={st.st_mtime-added_date} ctime={st.st_ctime-added_date}')


def main(dry_run=True, n_torrents=1500):
    r = api(
        json={
            'method': 'torrent-get',
            'arguments': {
                'ids': list(range(1, 1 + n_torrents)),
                'fields': [
                    'addedDate', 'downloadDir', 'downloadedEver', 'error', 'name', 'status',
                    'files'
                ]
            },
        }
    )
    r = r.json()['arguments']['torrents']
    for e in r:
        process(e, dry_run)
    df = pd.DataFrame(r)
    df.index += 1
    df.drop(columns=['files'], inplace=True)
    print(tabulate(df, headers='keys'))


if __name__ == '__main__':
    main()
