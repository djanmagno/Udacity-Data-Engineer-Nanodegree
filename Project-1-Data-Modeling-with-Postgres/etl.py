import os
import glob
import psycopg2
import pandas as pd
from sql_queries import *


def process_song_file(cur, filepath):
    """Process the song files and load data into the songs and artists table on Postgres.

    Args:
    cur: cursor to sparkifydb.
    filepath: string. Path of each file in the song_data folder.

    Returns:
    None
    """
    # open song file
    df = pd.read_json(filepath, lines = True)

    # insert song record
    song_columns = ['song_id', 'title', 'artist_id', 'year', 'duration']
    song_data = df[song_columns].values.tolist()[0]
    cur.execute(song_table_insert, song_data)
    
    # insert artist record
    artist_columns = [
        'artist_id', 
        'artist_name', 
        'artist_location', 
        'artist_latitude', 
        'artist_longitude'
    ]
    artist_data = df[artist_columns].values.tolist()[0]
    cur.execute(artist_table_insert, artist_data)


def process_log_file(cur, filepath):
    """Process the log files and load data into the time, users, and songplays table on Postgres.

    Args:
    cur: cursor to sparkifydb.
    filepath: string. Path of each file in the log_data folder.

    Returns:
    None
    """    
    # open log file
    df = pd.read_json(filepath, lines=True)

    # filter by NextSong action
    df = df[df.page == 'NextSong']

    # convert timestamp column to datetime
    t = pd.to_datetime(df.ts, unit='ms')
    
    # insert time data records
    dict_time = {
        'start_time' : t,
        'hour' : t.dt.hour,
        'day' : t.dt.day, 
        'week' : t.dt.isocalendar().week, 
        'month' : t.dt.month, 
        'year' : t.dt.year, 
        'weekday' : t.dt.weekday
    }
    time_df = time_df = pd.DataFrame(data = dict_time)

    for i, row in time_df.iterrows():
        cur.execute(time_table_insert, list(row))

    # load user table
    user_columns = ['userId', 'firstName', 'lastName', 'gender', 'level']
    user_df = df[user_columns]

    # insert user records
    for i, row in user_df.iterrows():
        cur.execute(user_table_insert, row)

    # insert songplay records
    for index, row in df.iterrows():
        
        # get songid and artistid from song and artist tables
        cur.execute(song_select, (row.song, row.artist, row.length))
        results = cur.fetchone()
        
        if results:
            songid, artistid = results
        else:
            songid, artistid = None, None

        # insert songplay record
        songplay_data = (
            pd.to_datetime(row.ts, unit='ms'), 
            row.userId, 
            row.level, 
            songid, 
            artistid, 
            row.sessionId, 
            row.location, 
            row.userAgent
        ) 
        cur.execute(songplay_table_insert, songplay_data)


def process_data(cur, conn, filepath, func):
    """Process the data folder in order to get all relative path of each file inthis folder than pass the file into functions that will and load data into the tables of saprkifydb on Postgres.

    Args:
    conn: conector of sparkifydb.
    cur: cursor to sparkifydb.
    filepath: string. Path of each subfolder on the data folder.
    func: function to process the files and load the data into a specific table in the sparkifydb on Postgres.

    Returns:
    None
    """
    # get all files matching extension from directory
    all_files = []
    for root, dirs, files in os.walk(filepath):
        files = glob.glob(os.path.join(root,'*.json'))
        for f in files :
            all_files.append(os.path.abspath(f))

    # get total number of files found
    num_files = len(all_files)
    print('{} files found in {}'.format(num_files, filepath))

    # iterate over files and process
    for i, datafile in enumerate(all_files, 1):
        func(cur, datafile)
        conn.commit()
        print('{}/{} files processed.'.format(i, num_files))


def main():
    """Creates connection with sparkifydb and execute functions to load data into tables on sparkifydb.

    Args:
    None

    Returns:
    None
    """    
    conn = psycopg2.connect("host=127.0.0.1 dbname=sparkifydb user=udacity_de password=djan08099")
    cur = conn.cursor()

    process_data(cur, conn, filepath='data/song_data', func=process_song_file)
    process_data(cur, conn, filepath='data/log_data', func=process_log_file)

    conn.close()


if __name__ == "__main__":
    main()