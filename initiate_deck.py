import csv
import sqlite3

def initiate_deck():
    rows = []
    with open("deck-example.csv", 'r') as file:
        csvreader = csv.reader(file)
        header = next(csvreader)
        for row in csvreader:
            rows.append(row)

    connection = sqlite3.connect('data.db')
    cursor = connection.cursor()
    for card in rows:
        cursor.execute("INSERT INTO cards (front_side, back_side) VALUES (?, ?);", card)
        connection.commit()