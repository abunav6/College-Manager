import smtplib


class SMTP:
    def __init__(self):
        self.from_mail = 'anubhavdinkar05@gmail.com'
        self.app_pwd = 'fpgbbzlnajnnxwhv'
        self.to_mail = 'anubhavdinkar.ec17@rvce.edu.in'
        self.body = 'Subject: Update your Attendance.\nIt has been 2 days since you were last reminded to update your ' \
                    'attendance in the app! You should probably do so now.\nSent by you, to you.'

    def send_email(self):
        smtp_obj = smtplib.SMTP('smtp.gmail.com', 587)
        print(smtp_obj.ehlo())
        smtp_obj.starttls()
        print(smtp_obj.login(self.from_mail, self.app_pwd))
        print(smtp_obj.sendmail(self.from_mail, self.to_mail, self.body))
        smtp_obj.quit()


if __name__ == '__main__':
    SMTP().send_email()
