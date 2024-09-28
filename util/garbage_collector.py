import os

from util.utils import get_filename
from logger.logger import Logger

logger = Logger('GarbageCollector')


def tmp_recycler(*items_paths) -> bool:
    """ delete a file or a folder if it exists. """
    logger.debug(f'recycling {len(items_paths)} items')
    for item_path in items_paths:
        if not isinstance(item_path, str):
            logger.error(f"tmp_dir '{item_path}' must be a path to a file not a {type(item_path)}")
            continue

        if os.path.exists(item_path):
            if os.path.isfile(item_path):
                os.remove(item_path)
            else: os.rmdir(item_path)
        else:
            logger.warning(f"file '{get_filename(item_path) if len(item_path) > 69 else item_path}' does not exist to be cleared with the tmp_recycler")

    return True
