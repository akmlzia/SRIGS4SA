#import csv
#import sqlite3
#import json
#dicta = {1:2, 3:4}
#lista = list(dicta)
#print(lista)
#print(dicta)

#fetch all student
#connection = sqlite3.connect('data.db')
#welcome_cursor = connection.cursor()
#welcome_cursor.execute("SELECT * FROM students;")
#students_list = welcome_cursor.fetchall()
#students_list_combo_box = {students_list[i][2]: students_list[i] for i in range(len(students_list))}
#print(students_list)

#rows = []
#with open("deck-example.csv", 'r') as file:
#    csvreader = csv.reader(file)
#    header = next(csvreader)
#    for row in csvreader:
#        rows.append(row)
#print(header)
#print(rows)

#connection = sqlite3.connect('data.db')
#cursor = connection.cursor()
#for card in rows:
#    cursor.execute("INSERT INTO cards (front_side, back_side) VALUES (?, ?);", card)
#    connection.commit()

#connection = sqlite3.connect('data.db')
#cursor = connection.cursor()
#cursor.execute("SELECT id FROM students ORDER BY id DESC LIMIT 1;")
#last_id = cursor.fetchall()
#print(last_id)

import tkinter as tk
root = tk.Tk()

var = tk.IntVar()
button = tk.Button(root, text="Click Me", command=lambda: var.set(1))
button.place(relx=.5, rely=.5, anchor="c")

print("waiting...")
root.wait_variable(var)
print("done waiting.")