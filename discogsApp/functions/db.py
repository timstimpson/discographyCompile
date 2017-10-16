import sqlite3
from discogsApp.functions.globals import database_path

# Database_project class:
# Database ORM to simplify the interaction with sqlite database
# Simple database function methods to simplify the complex data requests
# Methods for retrieving track, release and master data based on relational fields in database
# Database join methods kept to a minimum due to the memory overhead for large queries


class Database_project(object):

    def __init__(self):

        self.database_name = database_path
        self.file_path = ''

        super().__init__()

    def database_connect(self):

        self.connection_path = '{0}{1}'.format(self.file_path, self.database_name)
        self.conn = sqlite3.connect(self.connection_path, detect_types=sqlite3.PARSE_DECLTYPES)
        self.cursor = self.conn.cursor()

    def database_disconnect(self):

        self.conn.close()

    def database_create_table(self, database_table=None, database_table_headers=None):

        self.database_connect()
        cursor_command = 'CREATE TABLE {0} ({1})'.format(database_table, ','.join(database_table_headers))
        self.cursor.execute(cursor_command)
        self.conn.commit()
        self.database_disconnect()

    def database_delete_table(self, database_table=None):

        self.database_connect()
        cursor_command = 'DROP TABLE {0}'.format(database_table)
        self.cursor.execute(cursor_command)
        self.conn.commit()
        self.database_disconnect()

    def get_columns(self, database_table=None):

        self.database_connect()
        cursor_command = 'SELECT * from {0}'.format(database_table=None)
        self.cursor.execute(cursor_command)
        columns = [desc[0] for desc in self.cursor.description]
        self.database_disconnect()

        return columns

    def get_tables(self):

        self.database_connect()
        cursor_command = "SELECT name FROM sqlite_master WHERE type='table';"
        self.cursor.execute(cursor_command)
        tables = self.cursor.fetchall()
        self.database_disconnect()

        return tables

    def add_new_data(self, database_table=None, data=None):

        object_attributes = [key for key, value in data[0].items()]
        database_table = database_table
        insert_data = []

        for each_object in data:

            insert_data.append([each_object[attribute] for attribute in object_attributes])

        print('adding to db: {0}', database_table)

        cursor_command = 'INSERT INTO {0} VALUES({1})'.format(database_table, ','.join(['?'] * len(object_attributes)))

        self.database_connect()
        self.cursor.executemany(cursor_command, insert_data)
        self.conn.commit()
        self.database_disconnect()

    def get_pragma(self):

        cursor_command = 'PRAGMA temp_store = 2'

        self.database_connect()
        self.cursor.execute(cursor_command)
        self.conn.commit()
        self.database_disconnect()

        cursor_command = 'PRAGMA temp_store'

        self.database_connect()
        self.cursor.execute(cursor_command)
        data = self.cursor.fetchall()
        self.database_disconnect()

        return data

    def get_track_credits(self, artist_id=None):

        artist_str = ""

        for artist in artist_id:

            artist_str += '"' + str(artist) + '"' + ','

        artist_str = artist_str[:-1]

        cursor_command = 'SELECT artists.name, artists.anv, artists.role, tracks.artists, releases.artists, ' +\
            'artists.featured, releases.format_types, releases.formats, tracks.title, releases.labels, releases.catno, ' +\
            'releases.released, releases.title, tracks.ref,  ' +\
            'artists.ref, artists.id, releases.ds_id, tracks.position, artists.tracks, releases.master_id ' +\
            'FROM artists ' +\
            'JOIN tracks ON tracks.ref = artists.track_ref ' +\
            'JOIN releases ON releases.ref = tracks.release_ref ' +\
            'WHERE artists.id in ({0}) '.format(artist_str)

        self.database_connect()
        self.cursor.execute(cursor_command)
        data = (x for x in self.cursor.fetchall())
        self.database_disconnect()

        return data

    def get_release_credits(self, artist_id=None, release_ref=None):

        artist_str = ""

        for artist in artist_id:

            artist_str += '"' + str(artist) + '"' + ','

        artist_str = artist_str[:-1]

        cursor_command = 'SELECT artists.name, artists.anv, artists.role, tracks.artists, releases.artists, ' +\
            'artists.featured, releases.format_types, releases.formats, tracks.title, releases.labels, releases.catno, ' +\
            'releases.released, releases.title, tracks.ref,  ' +\
            'artists.ref, artists.id, releases.ds_id, tracks.position, artists.tracks, releases.master_id ' +\
            'FROM artists ' +\
            'JOIN releases ON artists.release_ref = releases.ref ' +\
            'JOIN tracks ON releases.ref = tracks.release_ref ' +\
            'WHERE artists.format = "release" ' +\
            'AND artists.id in ({0}) '.format(artist_str)

        self.database_connect()
        self.cursor.execute(cursor_command)
        data = (x for x in self.cursor.fetchall())
        self.database_disconnect()

        return data

    def get_masters_details(self, masters=None):

        master_str = ""

        for master in masters:

            master_str += '"' + str(master) + '"' + ','

        master_str = master_str[:-1]

        cursor_command = 'SELECT masters.ds_id, masters.main_release, masters.first_released ' +\
            'FROM masters ' +\
            'WHERE masters.ds_id in ({0}) '.format(master_str)

        self.database_connect()
        self.cursor.execute(cursor_command)
        data = self.cursor.fetchall()
        self.database_disconnect()
        return data
