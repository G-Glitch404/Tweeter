import os
import re
import subprocess
import configparser
from typing import Hashable

FFMPEG = "ffmpeg"  # change this for windows

clean_text = lambda text: re.sub(
    '\n+|\\s+|\\t+|\\r+|\\r\\n+|\\r\\n',
    ' ',
    ''.join(text)
).strip()

convert_to_mp4 = lambda file_path: subprocess.run([FFMPEG, '-i', file_path, file_path.split('.')[0] + '.mp4'])


def path(file_path: str, secondary_path: str = None) -> str:
    """ converts a relative path to an absolute path """
    seperator = '\\' if 'nt' in os.name.lower() else '/'
    file = os.path.join(
        seperator.join(
            os.path.realpath(
                os.path.join(
                    os.getcwd(),
                    os.path.dirname(__file__)
                )
            ).split(seperator)[:-1]),  # remove the current folder from path
        file_path
    )
    return file if secondary_path is None else os.path.join(file, secondary_path)


def get_filename(file_path: str) -> str:
    """ returns the filename from a file path """
    if "/" in file_path:
        return file_path.split("/")[-1]
    elif "\\" in file_path:
        return file_path.split("\\")[-1]

    return file_path


def fingerprint(obj: Hashable) -> str:
    """
    create an identifier for hashable objects by hashing them and getting their binary
    used for creating unique identifiers so nothing gets duplicated

    :param obj: the hashable object
    :type obj: Hashable

    :rtype: str
    :return: the binary of the hash of the hashable object
    """
    if isinstance(obj, Hashable):
        return bin(hash(obj))


def add_new_bot(username: str, consumer_key: str, consumer_secret: str, access_token: str, access_secret: str) -> None:
    """ adds a new bot to the system """
    bots_ini = configparser.ConfigParser()
    bots_ini_filepath: str = path('Bots', 'bots.ini')

    bots_ini.read(bots_ini_filepath, 'utf-8')
    bots_ini.add_section(username)

    bots_ini[username]['consumer_key'] = consumer_key
    bots_ini[username]['consumer_secret'] = consumer_secret
    bots_ini[username]['access_token'] = access_token
    bots_ini[username]['access_secret'] = access_secret

    with open(bots_ini_filepath, 'w') as configfile:
        bots_ini.write(configfile)


def get_available_bots() -> dict[str, dict[str, str]]:
    """ adds a new bot to the system """
    bots_ini = configparser.ConfigParser()
    bots_ini_filepath: str = path('Bots', 'bots.ini')

    bots_ini.read(bots_ini_filepath)

    for bot in bots_ini.sections():
        if not bot: continue
        yield {bot: {k: v for k, v in bots_ini.items(bot)}}
