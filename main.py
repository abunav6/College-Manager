import re
from functools import partial

from kivy.app import App
from kivy.core.window import Window
from kivy.uix.button import Button
from kivy.uix.checkbox import CheckBox
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput

from sql_conf import Login


def check_if_exists(name, table):
    sql = f"select subject_name from {table}"
    cur.execute(sql)
    names = [k[0] for k in cur.fetchall()]
    return name in names


def get_gpa(grades, max_creds):
    grade_points = {'S': 10, 'A': 9, 'B': 8, 'C': 7, 'D': 6, 'E': 5, 'F': 0}
    if None not in grades and len(grades) == len(max_creds):
        score = 0
        for k in range(len(grades)):
            score += grade_points[grades[k]] * max_creds[k]

        return round(score / sum(max_creds), 2)

    return "not enough data"


class CheckMarks(App):

    def __init__(self, name, **kwargs):
        super().__init__(**kwargs)
        self.max_marks = []
        self.ss_field = TextInput()
        self.inputs_test, self.inputs_quiz = [], []
        self.layout = GridLayout(rows=12, cols=2, row_force_default=True, row_default_height=50,
                                 pos_hint={'center_x': .5})
        self.subject_name = name.text
        self.title = self.subject_name
        Window.size = (850, 470)

    def build(self):
        regex = "(.*):\s+(.*)"
        with open("/Users/anubhavdinkar/Desktop/CollegeManager/subject_data.txt", "r") as file:
            lines = file.readlines()
            flag = False
            for line in lines:
                x = re.findall(regex, line)[0]
                if x[0] == self.subject_name:
                    flag = True
                    max_marks = x[-1]
                    break

        if flag:
            try:
                sql = f"select *from Test_Data where subject_name = \"{self.subject_name}\""
                cur.execute(sql)
                data = cur.fetchall()
                test = [None] * 3
                quiz = [None] * 3
                ss_mark = None

                if not data:
                    sql = f"insert into Test_Data (subject_name,t1,q1,t2,q2,t3,q3,ss,grade,percentage) values(\"{self.subject_name}\",NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL) "
                    cur.execute(sql)


                else:
                    t1, q1, t2, q2, t3, q3, ss_mark = data[0][1:-2]
                    test = [t1, t2, t3]
                    quiz = [q1, q2, q3]
                    existing_grade = data[0][-2]
                    existing_percentage = data[0][-1]
                    print(existing_grade, existing_percentage)
                    if existing_percentage and existing_grade:
                        self.layout.add_widget(Label(text=f"Grade: {existing_grade}", bold=True))
                        self.layout.add_widget(Label(text=f"Percentage: {existing_percentage}%", bold=True))
                    Window.size = (850, 510)


            except Exception as e:
                print(e)

            self.max_marks = [int(k) for k in max_marks.split("+")]

            for i in range(3):
                lbl = Label(text=f"Test {i + 1}")
                lbl2 = Label(text=f"Quiz {i + 1}")
                field = TextInput()

                field2 = TextInput()
                field.text = str(test[i]) if test[i] else ""
                self.inputs_test.append(field)
                field2.text = str(quiz[i]) if quiz[i] else ""
                self.inputs_quiz.append(field2)

                self.layout.add_widget(lbl)
                self.layout.add_widget(field)

                self.layout.add_widget(lbl2)
                self.layout.add_widget(field2)

            ss = Label(text="Self Study")
            self.layout.add_widget(ss)
            self.layout.add_widget(self.ss_field)
            self.ss_field.text = str(ss_mark) if ss_mark else ""
            if len(self.max_marks) == 4:
                lab_btn = Button(text="Lab", on_press=self.launch_lab)
                self.layout.add_widget(lab_btn)

            self.layout.add_widget(Button(text="Submit", on_press=self.submit))
            self.layout.add_widget(Button(text="Clear all Data", on_press=self.clear_all))
            self.layout.add_widget(Button(text="Close", on_press=self.home))

            return self.layout

    @staticmethod
    def launch_lab(instance):
        print("LAB")

    def home(self, instance):
        self.layout.clear_widgets()
        self.stop()
        MakeList(3).run()

    def submit(self, instance):
        if self.max_marks[0] == 30:
            self.MT = 25  # change the MT after TEST 1 (as it could be out of 30 too)
        else:
            self.MT = 50

        reduction_factor = self.max_marks[0] / (3 * self.MT)
        qrf = self.max_marks[1] / (3 * 10)
        test_marks = []
        quiz_marks = []
        for i in range(3):
            test_marks.append(float(self.inputs_test[i].text) if self.inputs_test[i].text else None)
            quiz_marks.append(float(self.inputs_quiz[i].text) if self.inputs_quiz[i].text else None)
        self_study = float(self.ss_field.text) if self.ss_field.text else None

        test_count = self.attempts(test_marks)
        quiz_count = self.attempts(quiz_marks)

        score, max_score = self.calc_score(test_marks, quiz_marks, reduction_factor, self_study, qrf, test_count,
                                           quiz_count)

        grade, percentage = self.get_grade(score, max_score)

        sql = f"update Test_Data set grade = \"{grade}\", percentage = {percentage} where subject_name = \"{self.subject_name}\""
        cur.execute(sql)

        for i in range(len(test_marks)):
            self.update(test_marks[i], f"t{i + 1}")
            self.update(quiz_marks[i], f"q{i + 1}")
        self.update(self_study, "ss")

        self.layout.clear_widgets()
        self.stop()
        MakeList(3).run()

    def clear_all(self, instance):
        sql = f"delete from Test_Data where subject_name=\"{self.subject_name}\""
        cur.execute(sql)
        self.layout.clear_widgets()
        self.stop()
        MakeList(3).run()

    def attempts(self, marks):
        count = 0
        for k in marks:
            if k:
                count += 1
        return count

    def calc_score(self, t, q, rf, ss, qrf, tc, qc):
        score = 0
        max_score = 0
        for test in t:

            if test:
                print(test)
                score += test * rf

        for quiz in q:
            if quiz:
                print(quiz)
                score += quiz * qrf
        if ss:
            print(ss)
            max_score += self.max_marks[2]
            score += ss

        max_score += (tc * self.MT * rf) + (qc * 10 * qrf)
        return score, max_score

    @staticmethod
    def get_grade(sc, ma):
        perc = round(100 * round(sc / ma, 4))
        if 90 <= perc <= 100:
            grade = "S"
        elif 80 <= perc < 90:
            grade = "A"

        elif 70 <= perc < 80:
            grade = "B"

        elif 60 <= perc < 70:
            grade = "C"

        elif 50 <= perc < 60:
            grade = "D"

        elif 40 <= perc < 50:
            grade = "E"

        else:
            grade = "F"

        return grade, perc

    def update(self, element, column):
        if element:
            sql = f"update Test_Data set {column} ={element} where subject_name = \"{self.subject_name}\""
        else:
            sql = f"update Test_Data set {column} = NULL where subject_name = \"{self.subject_name}\""
        cur.execute(sql)


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
        self.stop()
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
        self.stop()
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
            self.title = "Delete Subject Data"
        if self.code == 1:
            self.title = "Check Attendance"
            self.popup = Popup(title="Deleting subject", auto_dismiss=False)

        if self.code == 3:
            self.title = "Check Marks"

        sql = "select grade from Test_Data"
        cur.execute(sql)
        data = cur.fetchall()

        sql = "select credits from Subject_Data"
        cur.execute(sql)
        creds = [k[0] for k in cur.fetchall()]

        self.result = get_gpa([k[0] for k in data], creds)

    def home(self, instance):
        self.popup.dismiss()
        self.layout.clear_widgets()
        self.stop()
        MainApp().run()

    def build(self):
        sql = "select subject_name from Subject_Data"
        cur.execute(sql)
        data = [k[0] for k in cur.fetchall()]
        size = len(data)
        self.layout.rows = size + 3
        if type(self.result) == float:
            self.layout.add_widget(Label(text=f"Current SGPA:", bold=True))
            self.layout.add_widget(Label(text=f"{self.result}", bold=True))
            Window.size = (800, 510)
        for s in range(size):
            btn = Button(text=data[s])
            if self.code == 2:
                btn.bind(on_press=partial(self.remove_subject, data[s]))
            elif self.code == 1:
                btn.bind(on_press=partial(self.check_attend, data[s]))
            elif self.code == 3:
                btn.bind(on_press=partial(self.check_marks, data[s]))
            else:
                print("welp")
            self.layout.add_widget(btn)
        self.layout.add_widget(Button(text="Close", on_press=self.go_to_main))
        return self.layout

    def go_to_main(self, instance):
        self.layout.clear_widgets()
        self.stop()
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
        self.stop()
        CheckAttendance(name).run()

    def check_marks(self, instance, name):
        self.layout.clear_widgets()
        self.stop()
        CheckMarks(name).run()


class AddSubject(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.size = (1000, 250)
        self.title = "Add Subject Data"
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
        self.stop()
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
                if not check_if_exists(self.sub_name.text, "Subject_Data"):
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
        self.stop()
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
        self.stop()
        MakeList(1).run()

    def check_mark(self, instance):
        self.layout.clear_widgets()
        self.stop()
        MakeList(3).run()

    def add_subject(self, instance):
        self.layout.clear_widgets()
        self.stop()
        AddSubject().run()

    def del_subject(self, instance):
        self.layout.clear_widgets()
        self.stop()
        MakeList(2).run()


if __name__ == '__main__':
    app = MainApp()
    cnx, cur = Login().connect()
    app.run()
