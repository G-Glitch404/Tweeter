import os
import re
import subprocess
import configparser
from typing import Hashable, Optional
from GUI.error_dialog import ErrorDialogUI

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


def status_manager(
        checking: bool,
        *,
        total: Optional[int] = None,
        scheduled: Optional[int] = None,
        uploaded: Optional[int] = None,
        failed: Optional[int] = None,
) -> list[str]:
    """
    updates how the system is running and how things are going

    :param checking: if this flag is True it will return with no updating
    :type checking: bool

    :param total: total number of posts that are available for posting
    :type total: int

    :param scheduled: total number of scheduled posts that are still not uploaded yet
    :type scheduled: int

    :param uploaded: total number of successfully uploaded posts
    :type uploaded: int

    :param failed: total number of failed to upload posts
    :type failed: int

    :rtype: list[str]
    :return: all the updated values in a list
    """
    status_ini = configparser.ConfigParser()
    status_ini_filepath: str = path('config', 'status.ini')

    status_ini.read(status_ini_filepath, 'utf-8')
    if not status_ini.has_section('status'):
        status_ini.add_section('status')
    section = status_ini['status']

    if isinstance(total, int): section["total_posts"] = str(int(section.get("total_posts", '0')) + total)
    if isinstance(scheduled, int): section["scheduled_posts"] = str(int(section.get("scheduled_posts", '0')) + scheduled)
    if isinstance(uploaded, int): section["uploaded_posts"] = str(int(section.get("uploaded_posts", '0')) + uploaded)
    if isinstance(failed, int): section["failed_posts"] = str(int(section.get("failed_posts", '0')) + failed)
    if checking is True: return list(status_ini['status'].values())

    with open(status_ini_filepath, 'w') as configfile:
        status_ini.write(configfile)
    return list(section.values())


def get_available_bots() -> list[dict[str, dict]]:
    """ adds a new bot to the system """
    bots_ini = configparser.ConfigParser()
    bots_ini_filepath: str = path('config', 'bots.ini')

    bots_ini.read(bots_ini_filepath)

    return [{bot: {k: v for k, v in bots_ini.items(bot)}} for bot in bots_ini.sections() if bot]


def add_new_bot(username: str, subreddit: str | list[str], consumer_key: str, consumer_secret: str, access_token: str, access_secret: str) -> bool:
    """ adds a new bot to the system """
    bots_ini = configparser.ConfigParser()
    bots_ini_filepath: str = path('config', 'bots.ini')

    bots_ini.read(bots_ini_filepath, 'utf-8')
    bots_ini.add_section(username)

    if isinstance(subreddit, list):
        bots_ini[username]['subreddit'] = ','.join(subreddit)
    else:
        bots_ini[username]['subreddit'] = subreddit

    bots_ini[username]['consumer_key'] = consumer_key
    bots_ini[username]['consumer_secret'] = consumer_secret
    bots_ini[username]['access_token'] = access_token
    bots_ini[username]['access_secret'] = access_secret

    with open(bots_ini_filepath, 'w') as configfile:
        bots_ini.write(configfile)
    return True


def remove_bot(bot_username: str) -> bool:
    if not bot_username: return True

    bots_ini = configparser.ConfigParser()
    bots_ini_filepath: str = path('config', 'bots.ini')

    bots_ini.read(bots_ini_filepath)
    if not bots_ini.has_section(bot_username):
        ErrorDialogUI(f'bot username: "{bot_username}" does not exist')
        return False

    bots_ini.remove_section(bot_username)
    with open(bots_ini_filepath, 'w') as configfile:
        bots_ini.write(configfile)
    return True
