import sqlite3
import threading

from settings import settings
from util.decorators import catch_exceptions


class Database(threading.Thread):
    def __init__(self, database_filename: str = settings["POSTS_DATABASE"]) -> None:
        super(Database, self).__init__()
        self.conn = sqlite3.connect(database_filename, check_same_thread=False, timeout=120.0)
        self.cursor = self.conn.cursor()

    def fetch_all(self) -> tuple:
        """
        Fetch all data from table

        :yield: (id, profile) in a tuple
        """
        for article in self.cursor.execute(f'SELECT * FROM posts;').fetchall():
            yield article

    @catch_exceptions
    def insert_post(self, record: tuple) -> bool:
        """
        insert a record to the tweets table.

        :param record: all the x values in a tuple for database insertion
        :type record: tuple

        :rtype: bool
        :return: True if inserted successfully False otherwise
        """
        try: self.cursor.execute('INSERT INTO posts ([post_type], [text_body], [media_file_path], [upload_date], [bot_username]) VALUES (?, ?, ?, ?, ?)', record)
        except sqlite3.IntegrityError: return False
        else: self.conn.commit()

        return True

    @catch_exceptions
    def insert_tweet(self, record: tuple) -> bool:
        """
        insert a posted tweet to the tweets table.

        :param record: all the x values in a tuple for database insertion
        :type record: tuple

        :rtype: bool
        :return: True if inserted successfully False otherwise
        """
        try: self.cursor.execute('INSERT INTO tweets ([post_type], [text_body], [media_file_path], [upload_date], [bot_username]) VALUES (?, ?, ?, ?, ?)', record)
        except sqlite3.IntegrityError: return False
        else: self.conn.commit()

        return True

    def delete_record(self, record_id: int, table_name: str = 'posts') -> None:
        """ Delete a record from a table """
        self.cursor.execute(f'DELETE FROM {table_name} WHERE id={record_id};')
        self.conn.commit()

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.conn.commit()
        self.cursor.close()
        self.conn.close()

    def __del__(self) -> None:
        self.conn.commit()
        self.cursor.close()
        self.conn.close()
