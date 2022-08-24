import re
import requests
from pathlib import Path, PurePath
from win32_setctime import setctime
from tabulate import tabulate
from configparser import ConfigParser
import pandas as pd


XT='X-Transmission-Session-Id'
XV='LeM5PUM7XHwdQdLNYppmx1DG6ectOHl4QNW28O1Hoj1EO2W4'


cfg = ConfigParser()
with open('cfg.ini') as f:
    cfg.read_file(f)
    auth = cfg['auth']
    login = auth['login']
    password = auth['password']
    url = cfg['default']['url']


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
        kwargs.setdefault('headers', {}).setdefault(XT, XV)
        r = requests.post(*args, **kwargs)
        assert r.status_code != 409
    return r


def process(e):
    ddir = Path(e['downloadDir'])
    # if ddir.parts[-1] == 'Downloads':
    #     return
    roots = set()
    for file in e['files']:
        roots.add(ddir / PurePath(file['name']).parts[0])
    del e['files']
    added_date = e['addedDate']
    # print(e)
    # assert(len(roots) == 1)
    for r in roots:
        st = r.stat()
        if abs(st.st_ctime - added_date) < 3_600:
            break
        print(r)
        print(f'atime={st.st_atime-added_date} mtime={st.st_mtime-added_date} ctime={st.st_ctime-added_date}')
        setctime(r, added_date)
        # st = r.stat()
        # print(f'atime={st.st_atime-added_date} mtime={st.st_mtime-added_date} ctime={st.st_ctime-added_date}')


def main():
    r = api(
        json = {
            'method': 'torrent-get',
            'arguments': {
                'ids': list(range(1, 1500)),
                'fields': [
                    'addedDate', 'downloadDir', 'downloadedEver', 'error', 'name', 'status',
                    'files'
                ]
            },
        }
    )
    r = r.json()['arguments']['torrents']
    for e in r:
        process(e)

    # df = pd.DataFrame(r)
    # print(tabulate(df, headers='keys'))



if __name__ == '__main__':
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
