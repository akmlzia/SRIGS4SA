import sqlite3
import pandas as pd
import pickle
import base64

sqlite3.register_converter("pickle", pickle.loads)
sqlite3.register_adapter(pd.DataFrame, pickle.dumps) 

#read
deck = pd.read_csv('deck-example.csv')
print(deck)

name = "irregVerb Example"
date = "27/12/2021"

#pickle
pickled_deck = pickle.dumps(deck)

row = [name, deck, pickled_date]

connection = sqlite3.connect("data.db")

crsr = connection.cursor()

crsr.execute("INSERT INTO decks (deck_name, deck, add_date) VALUES (?, ?, ?);", row)

connection.commit()

connection.close()

#get deck from db

connection = sqlite3.connect("data.db")

crsr = connection.cursor()

command = "SELECT * FROM decks WHERE id=1;"

crsr.execute(command)

row_list = crsr.fetchall()

connection.close()

#unpickled
deck = pickle.loads(row_list[0][2])

print(deck)