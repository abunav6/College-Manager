from functools import partial

import mysql.connector as mysql
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.button import Button
from kivy.uix.checkbox import CheckBox
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput


def check_if_exists(name):
    sql = "select subject_name from Subject_Data"
    cur.execute(sql)
    names = [k[0] for k in cur.fetchall()]
    return name in names


class CheckAttendance(App):
    def __init__(self, name, **kwargs):
        super().__init__(**kwargs)
        self.attendance_display = Label()
        self.subject = name.text
        self.layout = GridLayout(cols=2, row_force_default=True, row_default_height=50,
                                 pos_hint={'center_x': .5})
        Window.size = (800, 200)
        self.missed = 0
        self.total = 0
        self.popup = Popup(title="Clear Data")

    def build(self):
        sql = f"select missed, total from Attendance_Data where subject_name = \"{self.subject}\""
        cur.execute(sql)
        data = cur.fetchall()
        if data:
            data = data[0]
            self.total = data[-1]
            self.missed = data[0]
        else:
            sql = f"insert into Attendance_Data (subject_name, missed, total) values(\"{self.subject}\",0,0)"
            cur.execute(sql)
        if self.total:
            percentage = 100 * round(((self.total - self.missed) / self.total), 4)
            string = f"{self.total - self.missed} / {self.total}          {percentage}%"
        else:
            string = "0/0          0%"

        self.attendance_display.text = string
        self.attendance_display.bold = True

        subject_display = Label(text=self.subject + "        ")
        subject_display.bold = True

        missed_class = Button(text="Missed a Class", on_press=self.missed_class)
        attended_class = Button(text="Attended a class", on_press=self.attended_class)

        close = Button(text="Close", on_press=self.go_home)
        clear_all = Button(text="Clear All Data", on_press=self.reset)

        self.layout.add_widget(subject_display)
        self.layout.add_widget(self.attendance_display)
        self.layout.add_widget(missed_class)
        self.layout.add_widget(attended_class)

        self.layout.add_widget(close)
        self.layout.add_widget(clear_all)
        return self.layout

    def go_home(self, instance):
        self.layout.clear_widgets()
        MakeList(1).run()

    def reset(self, instance):
        sql = f"update Attendance_Data set missed=0,total=0 where subject_name=\"{self.subject}\""
        cur.execute(sql)
        layout = GridLayout(rows=2, row_force_default=True, row_default_height=50,
                            pos_hint={'center_x': .5})
        layout.add_widget(Label(text=f"Reset {self.subject} data!"))
        btn = Button(text="Close")
        layout.add_widget(btn)
        self.popup.content = layout
        self.popup.open()
        btn.bind(on_press=self.home)

    def home(self, instance):
        self.popup.dismiss()
        self.layout.clear_widgets()
        MakeList(1).run()

    def missed_class(self, instance):
        self.missed += 1
        self.total += 1
        percentage = 100 * round(((self.total - self.missed) / self.total), 4)
        string = f"{self.total - self.missed} / {self.total}          {percentage}%"
        sql = f"update Attendance_Data set missed = {self.missed}, total={self.total} where subject_name=\"{self.subject}\""
        cur.execute(sql)
        self.attendance_display.text = string
        return

    def attended_class(self, instance):
        self.total += 1
        percentage = 100 * round(((self.total - self.missed) / self.total), 4)
        string = f"{self.total - self.missed} / {self.total}          {percentage}%"
        sql = f"update Attendance_Data set total={self.total} where subject_name=\"{self.subject}\""
        cur.execute(sql)
        self.attendance_display.text = string


class MakeList(App):
    def __init__(self, code, **kwargs):
        super().__init__(**kwargs)
        Window.size = (800, 400)
        self.code = code
        self.layout = GridLayout(cols=1, row_force_default=True, row_default_height=50,
                                 pos_hint={'center_x': .5})
        if self.code == 2:
            self.popup = Popup(title="Deleting subject", auto_dismiss=False)

    def home(self, instance):
        self.popup.dismiss()
        self.layout.clear_widgets()
        MainApp().run()

    def build(self):
        sql = "select subject_name from Subject_Data"
        cur.execute(sql)
        data = [k[0] for k in cur.fetchall()]
        size = len(data)
        self.layout.rows = size + 1
        for s in range(size):
            btn = Button(text=data[s])
            if self.code == 2:
                btn.bind(on_press=partial(self.remove_subject, data[s]))
            elif self.code == 1:
                btn.bind(on_press=partial(self.check_attend, data[s]))
            else:
                print("welp")
            self.layout.add_widget(btn)
        self.layout.add_widget(Button(text="Close", on_press=self.go_to_main))
        return self.layout

    def go_to_main(self, instance):
        self.layout.clear_widgets()
        MainApp().run()

    def remove_subject(self, instance, name):
        sql = f"delete from Subject_Data where subject_name = \"{name.text}\""
        layout = GridLayout(rows=2, row_force_default=True, row_default_height=50,
                            pos_hint={'center_x': .5})
        layout.add_widget(Label(text=f"Deleted {name.text} from the DB!"))
        btn = Button(text="Close")
        layout.add_widget(btn)
        self.popup.content = layout
        self.popup.open()
        btn.bind(on_press=self.home)

        try:
            cur.execute(sql)
        except Exception as e:
            print(e)

    def check_attend(self, instance, name):
        self.layout.clear_widgets()
        CheckAttendance(name).run()


class AddSubject(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.size = (1000, 250)

        self.layout = GridLayout(rows=4, cols=2, row_force_default=True, row_default_height=50,
                                 pos_hint={'center_x': .5})

        self.name_prompt = Label(text="Enter the name of the subject")
        self.sub_name = TextInput()

        self.cred_prompt = Label(text="Enter the number of credits")
        self.credits = TextInput()

        self.lab_prompt = Label(text="Check this box if lab subject")
        self.lab = CheckBox()

        self.submit = Button(text="Submit", on_press=self.insert_and_home)
        self.cancel = Button(text="Cancel", on_press=self.home)
        self.popup = Popup(title="Adding subject to DB")

    def home(self, instance):
        self.layout.clear_widgets()
        MainApp().run()

    def build(self):

        self.layout.add_widget(self.name_prompt)
        self.layout.add_widget(self.sub_name)
        self.layout.add_widget(self.cred_prompt)
        self.layout.add_widget(self.credits)
        self.layout.add_widget(self.lab_prompt)
        self.layout.add_widget(self.lab)
        self.layout.add_widget(self.submit)
        self.layout.add_widget(self.cancel)
        return self.layout

    def insert_and_home(self, instance):
        state = 1 if self.lab.state == 'down' else 0
        try:
            cred = int(self.credits.text)

            if 1 <= cred <= 5:
                layout = GridLayout(rows=2, row_force_default=True, row_default_height=50,
                                    pos_hint={'center_x': .5})
                if not check_if_exists(self.sub_name.text):
                    sql = f"insert into Subject_Data (subject_name,credits,lab) values(" \
                          f"\"{self.sub_name.text}\",{cred},{state})"
                    cur.execute(sql)
                    layout.add_widget(Label(text=f"{self.sub_name.text} has been added to the DB!"))
                else:
                    layout.add_widget(Label(text=f"{self.sub_name.text} already exists in the DB!"))

                btn = Button(text="Close")
                layout.add_widget(btn)
                self.popup.content = layout
                self.popup.open()
                btn.bind(on_press=self.home)

        except Exception as e:
            print(str(e).split(':')[-1].strip())

    def home(self, instance):
        self.popup.dismiss()
        self.layout.clear_widgets()
        MainApp().run()


class MainApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.size = (400, 100)
        self.title = "College Manager"
        self.del_sub = Button(text="Delete Subject", on_press=self.del_subject)
        self.add_sub = Button(text="Add Subject", on_press=self.add_subject)
        self.check_marks = Button(text="Check Marks", on_press=self.check_mark)
        self.check_attendance = Button(text="Check Attendance", on_press=self.check_att)
        self.layout = GridLayout(cols=2, row_force_default=True, row_default_height=40, spacing=[10, 10])

    def build(self):
        self.layout.add_widget(self.check_attendance)
        self.layout.add_widget(self.check_marks)
        self.layout.add_widget(self.add_sub)
        self.layout.add_widget(self.del_sub)
        return self.layout

    def check_att(self, instance):
        self.layout.clear_widgets()
        MakeList(1).run()

    def check_mark(self, instance):
        self.layout.clear_widgets()
        print("Marks")

    def add_subject(self, instance):
        self.layout.clear_widgets()
        AddSubject().run()

    def del_subject(self, instance):
        self.layout.clear_widgets()
        MakeList(2).run()


if __name__ == '__main__':
    CALL_CODE = -1
    app = MainApp()
    cnx = mysql.connect(user="anubhavdinkar", password="&Anubhav2699", host="localhost")
    cur = cnx.cursor()
    cur.execute("create database if not exists College_Manager")
    cur.execute("use College_Manager")
    cur.execute("create table if not exists Subject_Data (subject_name LONGTEXT, credits INT, lab INT)")
    cur.execute("create table if not exists Attendance_Data (subject_name LONGTEXT, missed INT, total INT)")
    cnx.autocommit = True
    app.run()
