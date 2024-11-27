# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_data_files, collect_submodules
import os

# automatically find all submodules from the 'util', 'Bots', 'Crawlers', 'GUI', and other modules
hiddenimports = collect_submodules('util') + collect_submodules('Bots') + collect_submodules('Crawlers') + collect_submodules('GUI') + collect_submodules('logger')
seperator = '\\' if 'nt' in os.name.lower() else '/'

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
    (f'.db{seperator}*', '.db'),
    (f'.db{seperator}sql{seperator}*', f'.db{seperator}sql'),  # include the SQL files for recreating the database
    (f'Bots{seperator}*', 'Bots'),
    (f'Crawlers{seperator}*', 'Crawlers'),
    (f'GUI{seperator}*', 'GUI'),
    (f'config{seperator}*', 'config'),
    (f'logger{seperator}*', 'logger'),
    (f'media{seperator}*', 'media'),
    (f'util{seperator}*', 'util'),
    ('*.py', '.'),

	# explicitly include the missing files for the dependency 'browserforge'
	(f'util{seperator}browserforge{seperator}fingerprints', f'browserforge{seperator}fingerprints{seperator}data'),
	(f'util{seperator}browserforge{seperator}headers', f'browserforge{seperator}headers{seperator}data'),

]

# analyze the app and bundle everything needed
a = Analysis(
    [f'GUI{seperator}app.py'],  # main script to start
    pathex=['GUI', 'Bots', 'Crawlers', 'logger', 'util'],  # include all directories
    binaries=[],
    datas=datas,  # include all the data files
    hiddenimports=hiddenimports,  # make sure all submodules are included
    hookspath=[],
    runtime_hooks=[],
    excludes=[]
)

pyz = PYZ(a.pure, a.zipfiles)
exe = EXE(pyz, a.scripts, a.binaries, a.zipfiles, a.datas, [], name='Tweeter', icon='./icon.ico', debug=False, strip=False, upx=False, console=False)
COLLECT(exe, a.binaries, a.zipfiles, a.datas, strip=False, upx=False, name='Tweeter')
