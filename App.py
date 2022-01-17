#Module Import
import sqlite3
import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showinfo, askyesno
from os.path import exists
from initiate_db import initiate_db
from initiate_deck import initiate_deck
import pandas as pd
import json
import webbrowser

#For insert and get deck and progress dict
sqlite3.register_adapter(dict, lambda d: json.dumps(d).encode('utf8'))
sqlite3.register_converter("json", lambda d: json.loads(d.decode('utf8')))

class WelcomeFrame(ttk.Frame):
    def __init__(self, parent, connection):
        super().__init__(parent)
        self.connection = connection
        self.parent = parent
        self.student_data = ()

        #Label Instruction
        self.choose_instruction = ttk.Label(self, text="Pilih Siswa :")
        self.choose_instruction.pack(pady=10)

        #Choose Student ComboBox
        self.person_combobox = ttk.Combobox(self, state='readonly')
        self.person_combobox.pack()

        #fetch all student
        self.write_combobox()

        #ComboBox Inside
        self.person_combobox['values'] = [full_name for full_name in self.students_data.keys()]
        self.person_combobox.bind('<<ComboboxSelected>>', self.change_welcome_button_state)
        
        #1st button frame
        self.first_button_frame = ttk.Frame(self)
        self.first_button_frame.pack()
        
        #Choose Student Button
        self.choose_person_button_nd = ttk.Button(self.first_button_frame, text="Mulai Sesi Baru", 
                                                  command=lambda: self.move2deck(self.students_data[self.person_combobox.get()], True))
        self.choose_person_button_nd.pack(padx=10, pady=10, side='right')
        self.choose_person_button_nd["state"] = "disabled"
        self.choose_person_button_od = ttk.Button(self.first_button_frame, text="Mulai Sesi Lama", 
                                                  command=lambda: self.move2deck(self.students_data[self.person_combobox.get()], False))
        self.choose_person_button_od.pack(padx=10, pady=10, side='right')
        self.choose_person_button_od["state"] = "disabled"

        #2nd button frame
        self.second_button_frame = ttk.Frame(self)
        self.second_button_frame.pack()
        
        #student manager and about Button
        self.student_manager_button = ttk.Button(self.second_button_frame, text="Student Manager", 
                                                  command=lambda: self.open_StudentManagerWindow(connection))
        self.student_manager_button.pack(pady=5)
        self.about_button = ttk.Button(self.second_button_frame, text="About", command=lambda: self.open_AboutWindow())
        self.about_button.pack(pady=5)
        
        #Pack frame to window
        self.pack(expand=True) 
    
    #Change button when combobox item selected function
    def change_welcome_button_state(self, event):
        if self.person_combobox.get():
            self.choose_person_button_nd["state"] = "normal"
            self.choose_person_button_od["state"] = "normal"
        else:
            self.choose_person_button_nd["state"] = "disabled"
            self.choose_person_button_od["state"] = "disabled"
        
    #Fetch and write all current student into combobox
    def write_combobox(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM students;")
        self.students_data = cursor.fetchall()
        self.students_data = {self.students_data[i][2]: self.students_data[i] for i in range(len(self.students_data))}
        #self.person_combobox.configure(values=[full_name for full_name in self.students_data.keys()])
        self.person_combobox['values'] = [full_name for full_name in self.students_data.keys()]
    
    #Frame change (Welcome -> Deck) function
    def move2deck(self, student_tuple, decrease_days):
        self.destroy()
        DeckFrame(self.parent, student_tuple, decrease_days, self.connection)
    
    #Open StudentManagerWindow function
    def open_StudentManagerWindow(self, connection):
        window = StudentManagerWindow(self, connection)
    
    #Open DeckEnrollWindow function
    def open_AboutWindow(self):
        window = AboutWindow(self)

class DeckFrame(ttk.Frame):
    def __init__(self, parent, student_tuple, decrease_days, connection):
        super().__init__(parent)
        self.connection = connection
        self.parent = parent
        self.student_tuple = student_tuple
        print(student_tuple)

        self.progress_dict = self.get_progress_dict()
        self.decrease_card_days(decrease_days)
        self.session_info = self.calculate_progress()        

        #Greeting Label
        self.greet = ttk.Label(self, text="Hi {}!".format(student_tuple[1]))
        self.greet.pack(pady=10)

        #Progress Info Frame
        self.progress_info_frame = ttk.Frame(self)
        self.progress_info_frame.pack(pady=10)
        #Progress Info Label
        self.remain_card_label = ttk.Label(self.progress_info_frame, text="Kartu tersisa : ")
        self.remain_card_label.grid(column=0, row=0, padx=5, pady=5)
        self.today_card_label = ttk.Label(self.progress_info_frame, text="Kartu hari ini : ")
        self.today_card_label.grid(column=0, row=1, padx=5, pady=5)
        self.remain_total_label = ttk.Label(self.progress_info_frame, text=self.session_info["remain_card"])
        self.remain_total_label.grid(column=1, row=0, padx=5, pady=5)
        self.today_total_label = ttk.Label(self.progress_info_frame, text=self.session_info["today_card"])
        self.today_total_label.grid(column=1, row=1, padx=5, pady=5)

        #New Card Initiation Frame
        self.nc_set_frame = ttk.Frame(self)
        self.nc_set_frame.pack(pady=5, padx=100)

        self.nc_label = ttk.Label(self.nc_set_frame, text="Jumlah kartu baru:")
        self.nc_label.pack(padx=10, pady=10, side='left')
        
        self.nc_value = tk.StringVar(value=0)
        self.nc_spinbox = ttk.Spinbox(self.nc_set_frame, textvariable=self.nc_value, from_=0, to=self.session_info["remain_card"])
        self.nc_spinbox.pack(padx=10, pady=10, side='left')

        #Button Frame
        self.button_frame = ttk.Frame(self)
        self.button_frame.pack(pady=10)
        
        #Start Session Button
        self.choose_deck_button = ttk.Button(self.button_frame, text="Mulai Sesi", command=lambda: self.start_session(self.nc_value.get()))
        self.choose_deck_button.pack(padx=10, pady=10, side='right')

        #Back to WelcomeFrame Button
        self.back_button = ttk.Button(self.button_frame, text="<< Kembali", command=lambda: self.back2welcome())
        self.back_button.pack(padx=10, pady=10, side='right')
        
        #Pack frame to window
        self.pack(expand=True)

    #get choosed student progress dict function
    def get_progress_dict(self):
        student_id = self.student_tuple[0]
        cursor = self.connection.cursor()
        cursor.execute("SELECT progress FROM progress WHERE student_id=?;",[student_id])
        progress_dict = cursor.fetchall()
        progress_dict = json.loads(progress_dict[0][0])
        print(progress_dict)
        return progress_dict
    
    #decrease cards days counter if user start new session function
    def decrease_card_days(self, decrease_days):
        if decrease_days:
            #decrease cards days counter if user start new session
            for key, item in self.progress_dict.items():
                if item[0] > 0:
                    self.progress_dict[key][0] -= 1
            student_id = self.student_tuple[0]
            cursor = self.connection.cursor()
            cursor.execute("""UPDATE progress SET progress = ? WHERE id = ?;""", [self.progress_dict, student_id])
            self.connection.commit()
    
    #Calculate remain and today cards function
    def calculate_progress(self):
        remain_card = 0
        today_card = 0
        for key, item in self.progress_dict.items():
            if item[0] == 0:
                today_card += 1
            elif item[0] == -2:
                remain_card += 1
        return {"remain_card": remain_card,"today_card": today_card}

    #Session Frame Loop function
    def start_session(self, total_new_card):
        self.destroy()
        #Get new card, change it to -1
        self.prepare_nc(total_new_card)
        print(self.progress_dict)
        #Take card in this session
        looped_list = [(key, item) for key, item in self.progress_dict.items() if item[0] == 0 or item[0] == -1]
        print(looped_list)
        #Session Loop
        for card in looped_list:
            frame = SessionFrame(self.parent, card, self.connection)
            frame.wait_variable(frame.var)
            if card[1][0] == 0:
                looped_list.append(card)
            print(looped_list)
            frame.destroy()
        #put current looped_list into progress_dict
        #self.save2db()
        DeckFrame(self.parent, self.student_tuple, False, self.connection)
    
    #prepare new card function
    def prepare_nc(self, total_new_card):
        total_new_card = int(total_new_card)
        if total_new_card > 0:
            for key, item in self.progress_dict.items():
                if item[0] == -2:
                    self.progress_dict[key][0] = -1
                    self.progress_dict[key][1] = 0
                    total_new_card -= 1
                if total_new_card == 0:
                    break

    #Save progress dict to db function
    def save2db(self):
        student_id = self.student_tuple[0]
        cursor = self.connection.cursor()
        cursor.execute("UPDATE progress SET progress = ? WHERE id = ?;", [self.progress_dict, student_id])
        self.connection.commit()
    
    #Back to welcomeFrame function
    def back2welcome(self):
        self.destroy()
        self.save2db()
        WelcomeFrame(self.parent, self.connection)

class SessionFrame(ttk.Frame):
    def __init__(self, parent, card, connection):
        super().__init__(parent)
        self.card = card
        self.connection = connection

        self.front_card, self.back_card = self.get_card_text()
        print(self.front_card)

        #front card
        self.front_frame = ttk.Frame(self)
        self.front_frame.pack(expand=True, fill='both')
        self.front_text_frame = ttk.Frame(self.front_frame)
        self.front_text_frame.pack(expand=True, fill='both')
        self.front_card_label = ttk.Label(self.front_text_frame, text=self.front_card, font=("Helvetica", 20))
        self.front_card_label.pack(expand=True, padx=10, pady=10)

        self.front_button_frame = ttk.Frame(self.front_frame)
        self.front_button_frame.pack()
        self.button = tk.Button(self.front_button_frame, text="Lihat Jawaban", command=lambda: self.show_back_card())
        self.button.pack(padx=10, pady=10)
        
        #back card
        self.back_frame = ttk.Frame(self)
        self.back_text_frame = ttk.Frame(self.back_frame)
        self.back_text_frame.pack(expand=True, fill='both')
        self.front_card_label = ttk.Label(self.back_text_frame, text=self.front_card, font=("Helvetica", 20))
        self.front_card_label.pack(expand=True, pady=5)
        self.back_card_label = ttk.Label(self.back_text_frame, text=self.back_card, font=("Helvetica", 14))
        self.back_card_label.pack(expand=True)

        self.back_button_frame = ttk.Frame(self.back_frame)
        self.back_button_frame.pack()
        self.var = tk.IntVar()
        if self.card[1][0] == -1: #New Card
            self.button0 = tk.Button(self.back_button_frame, text="Mudah", command=lambda: self.fibonacci_change(3))
            self.button0.pack(padx=10, pady=10, side='right')
            self.button1 = tk.Button(self.back_button_frame, text="Ulangi", command=lambda: self.fibonacci_change(1))
            self.button1.pack(padx=10, pady=10, side='right')
        elif self.card[1][0] == 0: #Today/Again Card
            self.button0 = tk.Button(self.back_button_frame, text="Mudah", command=lambda: self.fibonacci_change(3))
            self.button0.pack(padx=10, pady=10, side='right')
            self.button1 = tk.Button(self.back_button_frame, text="Lumayan", command=lambda: self.fibonacci_change(2))
            self.button1.pack(padx=10, pady=10, side='right')
            self.button2 = tk.Button(self.back_button_frame, text="Ulangi", command=lambda: self.fibonacci_change(1))
            self.button2.pack(padx=10, pady=10, side='right')
        print("test")

        #Pack frame to window
        self.pack(expand=True, fill='both')

    def get_card_text(self):
        card_id = self.card[0]
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM cards WHERE id=?;", [card_id])
        card_text = cursor.fetchall()
        print(card_text)
        front_card = card_text[0][1]
        back_card = card_text[0][2]
        return front_card, back_card

    def show_back_card(self):
        self.front_frame.destroy()
        self.back_frame.pack(expand=True, fill='both')

    def fibonacci(self,n):
        if n == 0:
            return 1
        elif n == 1:
            return 1
        else:
            return self.fibonacci(n-1) + self.fibonacci(n-2)

    def fibonacci_change(self, remember_level):
        if remember_level == 1:
            self.card[1][1] = 0
            self.card[1][0] = 0
        elif remember_level > 1:
            if remember_level == 2:
                self.card[1][1] += 1
            elif remember_level == 3:
                self.card[1][1] += 2
            self.card[1][0] = self.fibonacci(self.card[1][1])
        self.var.set(1)
        
class StudentManagerWindow(tk.Toplevel):
    def __init__(self, parent, connection):
        super().__init__(parent)
        self.grab_set()
        self.connection = connection
        self.parent = parent
        self.student_data = []        

        #Window setting
        self.title('Student Manager')
        self.resizable(False, False)

        #Window Frame
        self.windowFrame = ttk.Frame(self)
        self.windowFrame.pack(expand=True)
        
        #Button Frame
        self.button_frame = ttk.Frame(self.windowFrame)
        self.button_frame.grid(row=0, column=0)

        #Delete Student Button
        self.del_student_button = ttk.Button(self.button_frame, text="Hapus Siswa", command=lambda: self.delete_student())
        self.del_student_button.pack(padx=10, pady=10, side='right')
        self.del_student_button["state"] = "disabled"

        #Edit Student Button
        self.edit_student_button = ttk.Button(self.button_frame, text="Edit Siswa", command=lambda: self.open_student_form(False))
        self.edit_student_button.pack(padx=10, pady=10, side='right')
        self.edit_student_button["state"] = "disabled"

        #New Student Button
        self.new_student_button = ttk.Button(self.button_frame, text="Tambah Siswa", command=lambda: self.open_student_form(True))
        self.new_student_button.pack(padx=10, pady=10, side='right')
        
        #Treeview Frame
        #Button Frame
        self.treeview_frame = ttk.Frame(self.windowFrame)
        self.treeview_frame.grid(row=1, column=0)

        #Student Treeview
        self.columns = ("student_id", "nick_name", "full_name", "group_name", "join_date")
        self.student_tree = ttk.Treeview(self.treeview_frame, columns=self.columns, show='headings', height=10)
        self.student_tree.heading("student_id", text="No. Siswa")
        self.student_tree.column("student_id", width="80")
        self.student_tree.heading("nick_name", text="Nama Panggil")
        self.student_tree.heading("full_name", text="Nama Lengkap")
        self.student_tree.heading("group_name", text="Kelompok")
        self.student_tree.column("group_name", width="100")
        self.student_tree.heading("join_date", text="Tanggal Masuk")
        self.student_tree.column("join_date", width="130")
        self.student_tree.grid(row=0, column=0)
        self.student_tree.bind('<Button-1>', self.handle_manual_column_resize)
        self.student_tree.bind('<Motion>', self.handle_manual_column_resize)
        self.student_tree.bind('<<TreeviewSelect>>', self.change_student_manager_button_state)

        # add a scrollbar
        self.scrollbar = ttk.Scrollbar(self.treeview_frame, orient=tk.VERTICAL, command=self.student_tree.yview)
        self.student_tree.configure(yscroll=self.scrollbar.set)
        self.scrollbar.grid(row=0, column=1, sticky='ns')

        #fetch and write all student into treeview
        self.write_treeview()   
        
        #Warn if no student
        self.warn_no_student()

    #Disable manual column resizing function
    def handle_manual_column_resize(self, event):
        if self.student_tree.identify_region(event.x, event.y) == "separator":
            return "break"

    #No student popup function
    def warn_no_student(self):
        if self.student_data == []:
            showinfo(title="Peringatan", parent=self, 
                    message='Tidak ada murid terdaftar pada sistem, daftar siswa pada menu "Tambah Siswa"')

    #Fetch and write all current student into treeview
    def write_treeview(self):
        studentManager_cursor = self.connection.cursor()
        studentManager_cursor.execute("SELECT * FROM students;")
        self.student_data = studentManager_cursor.fetchall()
        for item in self.student_tree.get_children():
            self.student_tree.delete(item)
        for row in self.student_data:
            self.student_tree.insert("", tk.END, values=row)
        self.parent.write_combobox()
    
    #Change button when combobox item selected function
    def change_student_manager_button_state(self, event):
        if self.student_tree.selection():
            if len(self.student_tree.selection()) == 1:
                self.edit_student_button["state"] = "normal"
                self.del_student_button["state"] = "normal"
            else:
                self.edit_student_button["state"] = "disabled"
                self.del_student_button["state"] = "normal"
        else:
            self.edit_student_button["state"] = "disabled"
            self.del_student_button["state"] = "disabled"
    
    #Delete selected student in treeview function
    def delete_student(self):
        answer = askyesno(title='Konfirmasi', parent=self,
                    message='Apakah anda yakin menghapus siswa?\nsemua rekaman pencapaian juga akan terhapus.')
        if answer:
            cursor = self.connection.cursor()
            for selected_student in self.student_tree.selection():
                student_row = self.student_tree.item(selected_student)
                student_id = [student_row['values'][0]]
                cursor.execute("DELETE FROM students WHERE id = ?;", student_id)
            self.connection.commit()
            self.write_treeview()

    #Open DeckEnrollWindow function
    def open_student_form(self, new):
        if new:
            initial_form = ["","","",""]
        else:
            initial_form = self.student_tree.item(self.student_tree.selection()[0])['values'][1:]
        window = StudentFormWindow(self, self.connection, new, initial_form)

class StudentFormWindow(tk.Toplevel):
    def __init__(self, parent, connection, new, initial_form):
        super().__init__(parent)
        self.grab_set()
        self.connection = connection

        #Window setting
        self.title(self.formsetting(new)["title"])
        self.resizable(False, False)

        #Window Frame
        self.windowFrame = ttk.Frame(self)
        self.windowFrame.pack(expand=True)
        self.windowFrame.columnconfigure(0, weight=0)
        self.windowFrame.columnconfigure(1, weight=5)

        #Form
        #Nick Name
        self.nickName_label = ttk.Label(self.windowFrame, text="Nama Pendek: *")
        self.nickName_label.grid(column=0, row=0, sticky=tk.W, padx=5, pady=5)

        self.nickName_text = tk.StringVar(value=initial_form[0])
        self.nickName_text.trace("w", self.change_ok_button_state)
        self.nickName_entry = ttk.Entry(self.windowFrame, textvariable=self.nickName_text)
        self.nickName_entry.grid(column=1, row=0, sticky=tk.E, padx=5, pady=5)

        #Full Name
        self.fullName_label = ttk.Label(self.windowFrame, text="Nama Panjang: *")
        self.fullName_label.grid(column=0, row=1, sticky=tk.W, padx=5, pady=5)

        self.fullName_text = tk.StringVar(value=initial_form[1])
        self.fullName_text.trace("w", self.change_ok_button_state)
        self.fullName_entry = ttk.Entry(self.windowFrame, textvariable=self.fullName_text)
        self.fullName_entry.grid(column=1, row=1, sticky=tk.E, padx=5, pady=5)

        #Group Name
        self.groupName_label = ttk.Label(self.windowFrame, text="Nama Kelompok:")
        self.groupName_label.grid(column=0, row=2, sticky=tk.W, padx=5, pady=5)

        self.groupName_text = tk.StringVar(value=initial_form[2])
        self.groupName_entry = ttk.Entry(self.windowFrame, textvariable=self.groupName_text)
        self.groupName_entry.grid(column=1, row=2, sticky=tk.E, padx=5, pady=5)

        #Join Date
        self.joinDate_label = ttk.Label(self.windowFrame, text="Tanggal Masuk: *")
        self.joinDate_label.grid(column=0, row=3, sticky=tk.W, padx=5, pady=5)

        self.joinDate_text = tk.StringVar(value=initial_form[3])
        self.joinDate_text.trace("w", self.change_ok_button_state)
        self.joinDate_entry = ttk.Entry(self.windowFrame, textvariable=self.joinDate_text)
        self.joinDate_entry.grid(column=1, row=3, sticky=tk.E, padx=5, pady=5)

        #Button Frame
        self.button_frame = ttk.Frame(self.windowFrame)
        self.button_frame.grid(row=4, column=1, sticky=tk.E)

        #Ok Button
        self.ok_button = ttk.Button(self.button_frame, text=self.formsetting(new)["done_button"], command=lambda: self.done_handle(new, parent))
        self.ok_button["state"] = "disabled"
        self.ok_button.pack(padx=10, pady=10, side='right')
    
    #Open DeckEnrollWindow function
    def formsetting(self, new):
        if new:
            return {"title": "Tambah Siswa Baru", "done_button": "Tambah"}
        else:
            return {"title": "Edit Siswa", "done_button": "Simpan"}

    #Done button handle for add and edit student window function
    def done_handle(self, new, parent):
        if new:
            self.add_student(parent)
        else:
            self.edit_student(parent)
    
    #Change done button when required form filled function
    def change_ok_button_state(self, *args):
        if self.nickName_text.get() and self.fullName_text.get() and self.joinDate_text.get():
            self.ok_button["state"] = "normal"
        else:
            self.ok_button["state"] = "disabled"
    
    #add student function
    def add_student(self, parent):
        entry = [self.nickName_text.get(),
                 self.fullName_text.get(),
                 self.groupName_text.get(),
                 self.joinDate_text.get()]
        cursor = self.connection.cursor()
        #insert students data
        cursor.execute("INSERT INTO students (nick_name, full_name, group_name, join_date) VALUES (?, ?, ?, ?);", entry)
        #make progress dict based on cards table
        cursor.execute("SELECT id FROM cards;")
        cards_id_list = cursor.fetchall()
        new_progress_dict = {tuple_id[0]:(-2,-2) for tuple_id in cards_id_list}
        #get new student id
        cursor.execute("SELECT id FROM students ORDER BY id DESC LIMIT 1;")
        new_student_id = cursor.fetchall()[0][0]
        #make progresss for new student
        cursor.execute("INSERT INTO progress (student_id, progress) VALUES (?, ?);", [new_student_id, new_progress_dict])
        #save changes
        self.connection.commit()
        parent.write_treeview()
        self.destroy()

    #edit student function
    def edit_student(self, parent):
        selected_student = parent.student_tree.item(parent.student_tree.selection()[0])
        student_id = selected_student['values'][0]
        entry = [self.nickName_text.get(),
                 self.fullName_text.get(),
                 self.groupName_text.get(),
                 self.joinDate_text.get(),
                 student_id]
        studentManager_cursor = self.connection.cursor()
        studentManager_cursor.execute("""UPDATE students
                                        SET nick_name = ?, full_name = ?, group_name = ?, join_date = ?
                                        WHERE id = ?;""", entry)
        self.connection.commit()
        parent.write_treeview()
        self.destroy()

class AboutWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.grab_set()

        #Window setting
        self.title('About')
        self.geometry('500x300')
        self.resizable(False, False)

        #Window Frame
        self.AboutFrame = ttk.Frame(self)

        #App Logo
        self.photo = tk.PhotoImage(file='./assets/logo_50.png')
        self.app_logo = ttk.Label(self.AboutFrame, image=self.photo, padding=5)
        self.app_logo.pack(pady=10)

        self.app_name = ttk.Label(self.AboutFrame, text='SRIGS', font=('bold', 20))
        self.app_name.pack()
        
        self.app_name2 = ttk.Label(self.AboutFrame, text='Spaced Repetition In Group Software (SA version)')
        self.app_name2.pack()

        self.app_desc = ttk.Label(self.AboutFrame, text='SRIGS is a spaced repetition deck manager for group/school use.')
        self.app_desc.pack(pady=10)
        
        self.author = ttk.Label(self.AboutFrame, text='SRIGS (SA version) is derivated from SRIGS by N. Zia Akmal, 2021')
        self.author.pack()
        
        self.github = ttk.Label(self.AboutFrame, text='go to SRIGS github repo', foreground='blue')
        self.github.pack(pady=10)
        self.github.bind("<Button-1>", lambda e: self.callback("https://github.com/akmlzia/SRIGS"))

        #expand window to get widget centered
        self.AboutFrame.pack(expand=True)
    
    def callback(self, url):
        webbrowser.open_new_tab(url)

class App(tk.Tk):
    def __init__(self, connection):
        super().__init__()

        #Window setting
        self.title('SRIG4SA')
        self.geometry('400x400')
        self.resizable(False, False)
        self.iconphoto(True, tk.PhotoImage(file='./assets/logo.png'))

        WelcomeFrame(self, connection)

if __name__ == "__main__":
    if not exists('data.db'):
        initiate_db()
        initiate_deck()
    connection = sqlite3.connect('data.db')
    connection.execute("PRAGMA foreign_keys = 1")
    app = App(connection)
    app.mainloop()
    connection.close()