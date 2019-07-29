#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""This executable module is used as an import for the etl and create_tables 
modules. It contains sql which is run by these repective modules.
"""
__author__ = "Tim Fenton"
__copyright__ = "Copyright 2019"
__credits__ = ["Tim Fenton"]
__license__ = "GPL"
__version__ = "1.0"
__maintainer__ = "Tim Fenton"
__email__ = "tfenton@gmail.com"
__status__ = "Production"

import configparser
import psycopg2
from sql_queries import create_table_queries, drop_table_queries


def drop_tables(cur, conn):
    for query in drop_table_queries:
        cur.execute(query)
        conn.commit()


def create_tables(cur, conn):
    for query in create_table_queries:
        cur.execute(query)
        conn.commit()


def main():
    config = configparser.ConfigParser()
    config.read('dwh.cfg')

    conn = psycopg2.connect("host={} dbname={} user={} password={} port={}".format(*config['CLUSTER'].values()))
    cur = conn.cursor()

    drop_tables(cur, conn)
    create_tables(cur, conn)

    conn.close()


if __name__ == "__main__":
    main()