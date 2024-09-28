import os
import re
import subprocess

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
