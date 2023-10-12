import youtube_dl
import requests
import sys
import urllib.parse as urlparse
import sqlite3
import os
from prettytable import PrettyTable
from sqlite3 import Error
from urllib import request
from bs4 import BeautifulSoup



database = "./database.db"


def alive_check(url):
    requested = requests.get(url)
    if requested.status_code == 200:
        print("and the URL is existing.")
    else:
        print("but the URL does not exist.")
        sys.exit()


def custom_dl(name_check):
    if name_check == "batch":
        u_input = input("Please enter full path to the batch-file.txt (or c to cancel): ")
        if u_input == "c":
            print("Operation canceled.")
        else:
            with open(u_input, 'r') as input_file:
                for line in input_file:
                    line = line.strip()
                    custom_dl_download(line)

    else:
        custom_dl_download(name_check)



def custom_dl_download(url):
    alive_check(url)

    outtmpl = get_dl_location('DownloadLocation') + '/handpicked/%(title)s.%(ext)s'
    ydl_opts = {
        'format': 'best',
        'outtmpl': outtmpl,
        'nooverwrites': True,
        'no_warnings': False,
        'ignoreerrors': True,
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])



def get_dl_location(option):
    conn = create_connection(database)
    if conn is not None:
        c = conn.cursor()
        c.execute("SELECT * FROM ph_settings WHERE option='" + option + "'")
        rows = c.fetchall()
        for row in rows:
            dllocation = row[2]
        return dllocation
    else:
        print("Error! somethings wrong with the query.")



def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)
    return conn



def check_for_database():
    print("Running startup checks...")
    if os.path.exists(database):
        print("Database exists.")
    else:
        print("Database does not exist.")
        print("Looks like this is your first time run...")
        first_run()


def first_run():
    create_tables()


def create_table(conn, create_table_sql):
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
        print("Tables created.")
    except Error as e:
        print(e)


def create_config(conn, item):
    sql = ''' INSERT INTO ph_settings(option, setting)
              VALUES(?,?) '''
    c = conn.cursor()
    c.execute(sql, item)
    return c.lastrowid


def prepare_config():
    conn = create_connection(database)
    u_input = input("Please enter the FULL PATH to your download location: ")
    with conn:
        item = ('DownloadLocation', u_input)
        item_id = create_config(conn, item)


def create_tables():
    sql_create_items_table = """ CREATE TABLE IF NOT EXISTS ph_items (
                                        id integer PRIMARY KEY,
                                        type text,
                                        url_name text,
                                        name text,
                                        new integer DEFAULT 1,
                                        datecreated DATETIME DEFAULT CURRENT_TIMESTAMP,
                                        lastchecked DATETIME DEFAULT CURRENT_TIMESTAMP
                                    ); """

    sql_create_settings_table = """ CREATE TABLE IF NOT EXISTS ph_settings (
                                        id integer PRIMARY KEY,
                                        option text,
                                        setting text,
                                        datecreated DATETIME DEFAULT CURRENT_TIMESTAMP
                                    ); """

    conn = create_connection(database)

    if conn is not None:
        create_table(conn, sql_create_items_table)
        create_table(conn, sql_create_settings_table)
        prepare_config()
    else:
        print("Error! cannot create the database connection.")
