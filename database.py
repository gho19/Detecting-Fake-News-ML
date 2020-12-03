import unittest
import sqlite3
import json
import os



# Connects this file to the database.
def setUpDatabase(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn

def getSourceID(cur, conn, source_name):
    cur.execute('CREATE TABLE IF NOT EXISTS Sources (source_id INT, source_name TEXT)')
    
    cur.execute('SELECT source_id, source_name FROM Sources')
    
    id_name_tups = cur.fetchall()
    source_ids = [tup[0] for tup in id_name_tups]
    source_names = [tup[1] for tup in id_name_tups]

    # if we already have this source in the sources_table
    if source_name in source_names:
        cur.execute('SELECT source_id FROM Sources WHERE Sources.source_name = "{}"'.format(source_name))
        source_id = cur.fetchone()[0]
        
    # if we don't already have this source in the sources table
    else:
        highest_id = getHighestId(cur, conn, 'source_id', 'Sources')
        cur.execute('INSERT INTO Sources (source_id, source_name) VALUES (?,?)', (highest_id, source_name))
        source_id = highest_id
    
    conn.commit()
    return source_id

def getHighestId(cur, conn, column_name, table_name):
    cur.execute('SELECT {} FROM {}'.format(column_name, table_name))
    
    section_id_list = [int(tup[0]) for tup in cur.fetchall()]

    if section_id_list != []: 
        highest_id = max(section_id_list) + 1
    
    else:
        highest_id = 0
    
    conn.commit()
    return highest_id



# def main():
#     cur, conn = setUpDatabase('finalProject.db')
#     conn.close()


# if __name__ == "__main__":
#     main()
