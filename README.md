<h1 align="center">College Manager App</h1>

This is a GUI developed in Kivy to manage my college details- both attendance and marks.
- Add a subject by giving name, number of credits, and test/quiz/lab marks breakup in a separate ```subject_data.txt``` file
- Based on the entered marks, grade and percentage is also calculated  
- Attendance status can be monitored by manually selecting if class was attended or not
- Connected to a MySQL database to keep track of this data. 
- ```sql_conf.py``` is used to create/connnect to a database, create tables, etc., based on the details present in ```sql_data.txt``` (MySQL login credentials and the host)

 
