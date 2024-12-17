# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_data_files, collect_submodules
import os

# automatically find all submodules from the 'util', 'Bots', 'Crawlers', 'GUI', and other modules
hiddenimports = collect_submodules('util') + collect_submodules('Bots') + collect_submodules('Crawlers') + collect_submodules('GUI') + collect_submodules('logger')
sep = '\\' if 'nt' in os.name.lower() else '/'

# add specific hiddenimports for dependencies from requirements.txt
hiddenimports += [
   	'requests',
	'curl_cffi',
	'browserforge',
	'parsel',

	# these has to be explicitly added
	'browserforge.fingerprints',
	'curl_cffi.requests',
    'logging.handlers',

    'python_twitter_v2',  # module 'pytwitter'
    'python_dotenv',      # module 'dotenv'

	# in case there are issues with the alias
	'pytwitter',
    'dotenv',

    'sqlite3',
    'logging',
    'time',
    'datetime',
    'typing',
    'dataclasses',
    'json',
    'multiprocessing',
    'threading',
]

# including .py files and other files from other directories
datas = [
    (f'.db{sep}*', '.db'),
    (f'.db{sep}sql{sep}*', f'.db{sep}sql'),  # include the SQL files for recreating the database
    (f'Bots{sep}*', 'Bots'),
    (f'Crawlers{sep}*', 'Crawlers'),
    (f'GUI{sep}*', 'GUI'),
    (f'config{sep}*', 'config'),
    (f'logger{sep}*', 'logger'),
    (f'media{sep}*', 'media'),
    (f'util{sep}*', 'util'),
    ('*.py', '.'),

	# explicitly include the missing files for the dependency 'browserforge'
	(f'util{sep}browserforge{sep}fingerprints', f'browserforge{sep}fingerprints{sep}data'),
	(f'util{sep}browserforge{sep}headers', f'browserforge{sep}headers{sep}data'),

]

# analyze the app and bundle everything needed
a = Analysis(
    [f'GUI{sep}app.py'],  # main script to start
    pathex=['GUI', 'Bots', 'Crawlers', 'logger', 'util'],  # include all directories
    binaries=[('/usr/local/lib/libpython3.12.so', 'libpython3.12.so')] if 'linux' in os.name.lower() else [],
    datas=datas,  # include all the data files
    hiddenimports=hiddenimports,  # make sure all submodules are included
    hookspath=[],
    runtime_hooks=[],
    excludes=[]
)

pyz = PYZ(a.pure, a.zipfiles)
exe = EXE(pyz, a.scripts, a.binaries, a.zipfiles, a.datas, [], name='Tweeter', icon='./icon.ico', debug=False, strip=False, upx=False, console=False)
