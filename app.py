import json
import os
import random
import secrets
import sqlite3
from flask import  Flask, flash, jsonify, render_template, render_template_string, request, redirect, session, url_for
import io
import base64
import re

import google.generativeai as genai
genai.configure(api_key="AIzaSyDMLJqvtG0YygUdLf49Crz2-DRFE8qII00")


app = Flask(__name__)
app.secret_key = os.urandom(24)
global color
DATABASE = 'interviewresult.db'

app = Flask(__name__)
candidate_id = ""
value0 = ""
value1 = ""
value2 = ""
value3 = ""
value4 = ""
candidate_id = ""
question_id = ""
sql_questions = ""
selected_questions = ""

def get_db():
    """Returns a connection to the SQLite database"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # Allows access to columns by name
    return conn

def init_db():
    """Initialize the database with required table"""
    with get_db() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS candidate (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                candidatename String NOT NULL,
                email String NOT NULL,
                contactnumber String NOT NULL
            )
        ''')
        conn.commit()

 
def init_db1():
    """Initialize the database with required table"""
    with get_db() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS questionlist (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question String NOT NULL,
                skill String NOT NULL,
                complexlevel String NOT NULL,
                status String NOT NULL
            )
        ''')
        conn.commit()  

def init_db2():
    """Initialize the database with required table"""
    with get_db() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS answer (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question_id INTEGER NOT NULL,
                question_name String NOT NULL,
                user_answer String NOT NULL,
                candidate_id INTEGER NOT NULL,
                candidate_name String NOT NULL,
                FOREIGN KEY (question_id) REFERENCES questionlist(id) ON DELETE CASCADE
                FOREIGN KEY (question_name) REFERENCES questionlist(question) ON DELETE CASCADE
                FOREIGN KEY (candidate_id) REFERENCES candidate(id) ON DELETE CASCADE
                FOREIGN KEY (candidate_name) REFERENCES candidate(candidatename) ON DELETE CASCADE   
            )
        ''')
        conn.commit() 

def init_db3():
    """Initialize the database with required table"""
    with get_db() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS score (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question_id INTEGER NOT NULL ,
                question_name String NOT NULL,
                user_answer String NOT NULL,
                user_score String NOT NULL,
                candidate_id INTEGER NOT NULL,
                candidate_name String NOT NULL,
                FOREIGN KEY (question_id) REFERENCES questionlist(id) ON DELETE CASCADE
                FOREIGN KEY (question_name) REFERENCES questionlist(question) ON DELETE CASCADE
                FOREIGN KEY (candidate_id) REFERENCES candidate(id) ON DELETE CASCADE
                FOREIGN KEY (candidate_name) REFERENCES candidate(candidatename) ON DELETE CASCADE   
            )
        ''')
        conn.commit()               

# Route for the main page that has the tabs and forms
@app.route('/l1')
def index():
    global value1
    global value2
    global value3
    global value4
    global value0
    global sql_questions
    global selected_questions
    value1=""
    value2=""
    value3=""
    value4=""
    value0=""
    sql_questions =""
    selected_questions =""


    with get_db() as conn:
        curs = conn.cursor()
        curs.execute("SELECT id,question FROM questionlist WHERE skill like ?", ("%Selenium%",))
        questionarray = curs.fetchall()
        selected_questions = questionarray[0:4]
        curs.execute("SELECT id,question FROM questionlist WHERE skill like ?", ("%SQL%",))
        sqlquestion = curs.fetchall()
        sql_questions = sqlquestion[0:4]
        if selected_questions:
            print(questionarray[0]['id'], questionarray[0]['question'])
        else:
             print("❌ No questions found in selected_questions.")
        
        if sql_questions:
            print(sqlquestion[0]['id'], sqlquestion[0]['question'])
        else:
             print("❌ No questions found in selected_questions.")

    return render_template('L1online_question.html',value0=value0,value1=value1, value2=value2, value3=value3,questionlist=selected_questions,sqllist=sql_questions)


# Route for processing candidate form
@app.route('/submit_candidate', methods=['POST'])
def submit_candidate():
    global value1
    global value2
    global value3
    global value4
    global value0
    if request.method == 'POST':
        value1 = request.form['name']
        value2 = request.form['email']
        value3 = request.form['number']
        value0 = request.form['candidateid']
        with get_db() as conn:
            curs = conn.cursor()
            curs.execute('''
            INSERT INTO candidate (candidatename, email, contactnumber)
            VALUES (?, ?, ?)
        ''', (value1, value2, value3))
            conn.commit()
            value0 = curs.lastrowid

           
            if curs.rowcount > 0:
                value4 = f"Candidate information added successfully! Candidate Name(ID): {value1}-({value0})"
            
            else:
                value4 = 'Record not added. Candidate Name: {value1}'

            with get_db() as conn:
             curs = conn.cursor()
            curs.execute("SELECT id,question FROM questionlist WHERE skill like ?", ("%Selenium%",))
            questionarray = curs.fetchall()

            selected_questions = questionarray[0:4]

            curs.execute("SELECT id,question FROM questionlist WHERE skill like ?", ("%SQL%",))
            questionarray = curs.fetchall()

            sql_questions = questionarray[0:4]
           
            return render_template('L1online_question.html',value0=value0,value1=value1, value2=value2, value3=value3,value4=value4,questionlist=selected_questions,sqllist=sql_questions)
   

@app.route('/admin',methods=['GET', 'POST'])
def admin():
    
    if request.method == 'POST':
    # Retrieve form data
        question = request.form['question']
        skill = request.form['skill']
        complexlevel = request.form['complexlevel']
        status = request.form['status']
        app.logger.warning("A warning message."+question)  
        recorddata = question
    # Insert into database
        with get_db() as conn:
            curs = conn.cursor()
            curs.execute('''
            INSERT INTO questionlist (question, skill, complexlevel, status)
            VALUES (?, ?, ?, ?)
        ''', (question, skill, complexlevel, status))
            conn.commit()
            if curs.rowcount > 0:
                alert_message = f"Record added successfully! Question Name: {recorddata}"
            else:
                alert_message = 'Record not added. Question Name: {recorddata}'
            return redirect(url_for('admin',alert=alert_message))
    else:
        with get_db() as conn:
            curs = conn.cursor()
            curs.execute('SELECT * FROM questionlist')
            questionlist = curs.fetchall()
            return render_template('admin.html',questionlist=questionlist)
        
@app.route('/delete/<int:record_id>', methods=['POST'])
def delete(record_id):
    global recorddata
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT question from questionlist WHERE id = ?", (record_id,))
    recorddata = cur.fetchone()
    # DELETE query to remove the record with the given ID
    cur.execute("DELETE FROM questionlist WHERE id = ?", (record_id,))
    conn.commit()  # Commit the changes to the database
    if cur.rowcount > 0:
            alert_message = f"Record deleted successfully! question Name: {recorddata['question']}"
    else:
            alert_message = 'Record not found or already deleted.'
    conn.close()
    return redirect(url_for('admin',alert=alert_message))


@app.route('/edit', methods=['POST'])
def edit():
    global recorddata
    global recordid
    global newstatus
    if request.method == 'POST':
    # Retrieve form data
        recordid = request.form['questionid']
        question = request.form['question']
        skill = request.form['skill']
        complexlevel = request.form['complexlevel']
        status = request.form['status']
        app.logger.warning("A warning message."+question) 
        newstatus =  request.form['status']
        recorddata = question
    # Insert into database
        with get_db() as conn:
            curs = conn.cursor()
            curs.execute("UPDATE questionlist SET question = ?, skill = ?,complexlevel=?,status=? WHERE id = ?",
            (question, skill, complexlevel, status,recordid))
            conn.commit()
            if curs.rowcount > 0:
                alert_message = f"Record updated successfully! Requirement Name: {recorddata}"
                #email_scheduler(currentstatus,newstatus)
            else:
                alert_message = 'Record not added. Requirement Name: {recorddata}'
               

            return redirect(url_for('admin',alert=alert_message))
    else:
        with get_db() as conn:
            curs = conn.cursor()
            curs.execute('SELECT * FROM questionlist')
            questionlist = curs.fetchall()
            return render_template('admin.html',questionlist=questionlist)

@app.route('/getquestion/<int:record_id>', methods=['GET'])
def getreq(record_id):
            with get_db() as conn:
                curs = conn.cursor()
                curs.execute("SELECT * from questionlist WHERE id = ?", (record_id,))
                questionlist = curs.fetchone()
                if questionlist:
                    global currentstatus 
                    currentstatus = questionlist['status']
                    return jsonify ({"id":questionlist['id'],"question":questionlist['question'],"skill":questionlist['skill'],"complexlevel":questionlist['complexlevel'],"status":questionlist['status']})


@app.route('/getcandidateinfo/<int:record_id>', methods=['GET'])
def getcandidateinfo(record_id):
            with get_db() as conn:
                curs = conn.cursor()
                curs.execute("SELECT * from candidate WHERE id = ?", (record_id,))
                candidateinfo = curs.fetchone()
                curs.execute("SELECT * from answer WHERE id = ?", (record_id,))
                curs.execute("SELECT * FROM answer a JOIN questionlist q ON a.question_id = q.id WHERE q.skill LIKE ? AND a.candidate_id = ?",
                ("%Selenium%", record_id))
                questionarray = curs.fetchall()
                seleniumdata = [dict(row) for row in questionarray]
                curs.execute("SELECT * FROM answer a JOIN questionlist q ON a.question_id = q.id WHERE q.skill LIKE ? AND a.candidate_id = ?",
                 ("%SQL%", candidate_id))
                sql_array = curs.fetchall()
                sqldata = [dict(row) for row in sql_array]
                return jsonify ({'candidateinfo':candidateinfo,'selenium_questions':seleniumdata,'sql_questions':sqldata})


@app.route('/submit_automation',methods=['GET', 'POST'])
def submit_automation():
    global candidatedetails
    global questiondetails
    global candidate_id
    global question_id
    global value4
    global automationquestion
    if request.method == 'POST':
            action_flag = request.form['action_flag']
            for key in request.form:
                value = request.form[key]
                print(f"{key}: {value}")

                if key.startswith('answer_'):
                    question_id = int(key.split('_')[1])
                    candidate_id = int(key.split('_')[2])
                    useranswer = request.form[key].strip()
                    print(question_id, candidate_id,useranswer)
                    with get_db() as conn:
                        curs = conn.cursor()
                        curs.execute("SELECT * from questionlist WHERE id = ?", (question_id,))
                        questiondetails = curs.fetchone()
                        curs.execute("SELECT * from candidate WHERE id = ?", (candidate_id,))
                        candidatedetails = curs.fetchone()
                        if action_flag == 'update':

                            curs.execute('''UPDATE answer SET  user_answer = ?
                           where id = ?''', (useranswer,question_id))
                        
                        else:
                           curs.execute('''
                             INSERT INTO answer (question_id, question_name, user_answer, candidate_id, candidate_name)
                             VALUES (?, ?, ?, ?, ?)
                             ''', (questiondetails['id'], questiondetails['question'], useranswer, candidatedetails['id'], candidatedetails['candidatename']))
                        
                        conn.commit()

    with get_db() as conn:
        curs = conn.cursor()
        valuetest = f'Candidate answer input added successfully {{candidate_id}}'
        print(valuetest)

        curs.execute("SELECT * FROM answer a JOIN questionlist q ON a.question_id = q.id WHERE q.skill LIKE ? AND a.candidate_id = ?",
        ("%Selenium%", candidate_id))
        questionarray = curs.fetchall()
        selected_questions = questionarray[0:4]

        if selected_questions:
            print(questionarray[0]['id'], questionarray[0]['question'])
            value4 = f"Candidate input added successfully!"
            value4 = "Selenium Automation: Candidate input added successfully!"
        
        curs.execute("SELECT * FROM answer a JOIN questionlist q ON a.question_id = q.id WHERE q.skill LIKE ? AND a.candidate_id = ?",
        ("%SQL%", candidate_id))
        sqlquestion = curs.fetchall()
        sql_questions = sqlquestion[0:4]
        if sql_questions:
            print(sql_questions[0]['id'], sql_questions[0]['question'])
        else:
            curs.execute("SELECT id,question FROM questionlist WHERE skill like ?", ("%SQL%",))
            sqlquestion = curs.fetchall()
            sql_questions = sqlquestion[0:4]
    return render_template('L1online_question.html',value0=candidate_id,value1=value1, value2=value2, value3=value3,value4=value4,questionlist=selected_questions,sqllist=sql_questions)

@app.route('/submit_sql',methods=['GET', 'POST'])
def submit_sql():
    global candidatedetails
    global questiondetails
    global candidate_id
    global question_id
    global value4
    if request.method == 'POST':
            action_flag = request.form['action_flag']
            for key in request.form:
                value = request.form[key]
                print(f"{key}: {value}")

                if key.startswith('answer_'):
                    question_id = int(key.split('_')[1])
                    candidate_id = int(key.split('_')[2])
                    useranswer = request.form[key].strip()
                    print(question_id, candidate_id,useranswer)
                    with get_db() as conn:
                        curs = conn.cursor()
                        curs.execute("SELECT * from questionlist WHERE id = ?", (question_id,))
                        questiondetails = curs.fetchone()
                        curs.execute("SELECT * from candidate WHERE id = ?", (candidate_id,))
                        candidatedetails = curs.fetchone()
                        if action_flag == 'update':
                                curs.execute('''UPDATE answer SET  user_answer = ?
                                 where id = ?''', (useranswer,question_id))
                        else:
                                curs.execute('''
                                INSERT INTO answer (question_id, question_name, user_answer, candidate_id, candidate_name)
                                VALUES (?, ?, ?, ?, ?)
                                ''', (questiondetails['id'], questiondetails['question'], useranswer, candidatedetails['id'], candidatedetails['candidatename']))
                    
                        conn.commit()

    with get_db() as conn:
        curs = conn.cursor()
        valuetest = f'Candidate answer input added successfully {{candidate_id}}'
        print(valuetest)

        curs.execute("SELECT * FROM answer a JOIN questionlist q ON a.question_id = q.id WHERE q.skill LIKE ? AND a.candidate_id = ?",
        ("%Selenium%", candidate_id))
        selenium_questions = curs.fetchall()
        selected_questions1 = selenium_questions[0:4]
        if selected_questions1:
            print(selenium_questions[0]['id'], selenium_questions[0]['question'])
            value4 = f"Candidate input added successfully!"
            value4 = "SQL: Candidate input added successfully!"
        else :
            curs.execute("SELECT id,question FROM questionlist WHERE skill like ?", ("%Selenium%",))
            questionarray = curs.fetchall()
            selected_questions1 = questionarray[0:4]
            

        curs.execute("SELECT * FROM answer a JOIN questionlist q ON a.question_id = q.id WHERE q.skill LIKE ? AND a.candidate_id = ?",
        ("%SQL%", candidate_id))
        sql_questions = curs.fetchall()
        selected_questions = sql_questions[0:4]
        if selected_questions:
            print(sql_questions[0]['id'], sql_questions[0]['question'])
            value4 = f"Candidate input added successfully!"
            value4 = "SQL: Candidate input added successfully!"
        curs.execute("SELECT * FROM candidate where id = ?",(candidate_id,))
        candidateinfo = curs.fetchone()

    return render_template('L1online_question.html',value0=candidate_id,value1=candidateinfo['candidatename'], value2=candidateinfo['email'], value3=candidateinfo['contactnumber'],value4=value4,questionlist=selected_questions1,sqllist=selected_questions)

@app.route('/candidate1')
def candidate1():
     with get_db() as conn:
        curs = conn.cursor()
        query = '''
          SELECT c.id, c.candidatename, c.email, c.contactnumber,a.question_id, a.question_name, a.user_answer ,q.skill FROM answer a JOIN candidate c ON a.candidate_id = c.id
          JOIN questionlist q ON a.question_id = q.id'''
        
        curs.execute('SELECT * FROM candidate')
        candidate = curs.fetchall()
        return render_template('candidate.html',candidate=candidate)
     
@app.route('/candidate')
def candidate():
     with get_db() as conn:
        curs = conn.cursor()
        findscore = '''SELECT 
        c.id,c.candidatename,c.email,c.contactnumber,COALESCE(AVG(s.user_score), 0) AS user_score,
        CASE 
        WHEN COUNT(s.user_score) = 0 THEN 'Not Applicable'
        WHEN COALESCE(AVG(s.user_score), 0) < 6 THEN 'Failed'
        ELSE 'Pass'
        END AS status FROM candidate c LEFT JOIN  score s ON c.id = s.candidate_id GROUP BY 
        c.id, c.candidatename, c.email, c.contactnumber;'''
        curs.execute(findscore)
        candidate = curs.fetchall()

     
        return render_template('candidate.html',candidate=candidate)

@app.route('/get_candidate/<int:record_id>')
def get_candidate(record_id):
     with get_db() as conn:
        curs = conn.cursor()
        seleniumquery = '''
          SELECT c.id, a.candidate_id, c.candidatename, c.email, c.contactnumber,a.question_id, a.question_name, a.user_answer ,q.skill FROM answer a JOIN candidate c ON a.candidate_id = c.id
          JOIN questionlist q ON a.question_id = q.id WHERE q.skill = ? and a.candidate_id = ?'''
        curs.execute(seleniumquery,('Selenium Java',record_id))
        selenium = curs.fetchall()
        return render_template('candidate.html',questionlist=selenium)



@app.route('/getdata/<int:record_id>' ,methods=['POST'])
def getdata(record_id):
    with get_db() as conn:
        curs = conn.cursor()
        curs.execute("SELECT * FROM candidate where id = ?",(record_id,))
        candidate = curs.fetchall()

        curs.execute("""
            SELECT * 
            FROM score a 
            JOIN questionlist q ON a.question_id = q.id 
            WHERE q.skill LIKE ? AND a.candidate_id = ?
            """, ('%SQL%', record_id))
        sql_questions = curs.fetchall()
        for row in sql_questions:
            print("prompt score", row['user_score'],"recodid",record_id)

        if not sql_questions:
            curs.execute("""
            SELECT * 
            FROM answer a 
            JOIN questionlist q ON a.question_id = q.id 
            WHERE q.skill LIKE ? AND a.candidate_id = ?
            """, ('%SQL%', record_id))
            sql_questions = curs.fetchall()
            for row in sql_questions:
                print("promptanswer", row['user_score'],"recodid",record_id)

        curs.execute("""
            SELECT * 
            FROM score a 
            JOIN questionlist q ON a.question_id = q.id 
            WHERE q.skill LIKE ? AND a.candidate_id = ?
            """, ('%Selenium%', record_id))
        selenium_questions = curs.fetchall()
        for row in selenium_questions:
            print("promptscore", row['user_score'],"recodid",record_id)

        if not selenium_questions:
            curs.execute("""
            SELECT * 
            FROM answer a 
            JOIN questionlist q ON a.question_id = q.id 
            WHERE q.skill LIKE ? AND a.candidate_id = ?
            """, ('%Selenium%', record_id))
            
            selenium_questions = curs.fetchall()
            for row in selenium_questions:
             print("promptanswer", row['user_score'],"recodid",record_id)

        return render_template('candidate_detail.html',candidate=candidate, questionlist=selenium_questions,sqllist=sql_questions)

@app.route('/deletecandidate/<int:record_id>' ,methods=['POST'])
def deletecandidate(record_id):
    with get_db() as conn:
        curs = conn.cursor()
        curs.execute("SELECT * from candidate WHERE id = ?", (record_id,))
        recorddata = curs.fetchone()

        curs.execute("Delete  FROM answer  WHERE candidate_id = ?",
        (record_id,))

        conn.commit()

        curs.execute("Delete  FROM candidate  WHERE id = ?",
        (record_id,))

        conn.commit()

        if curs.rowcount > 0:
            alert_message = f"Record deleted successfully! Candidate details: Name: {recorddata['candidatename']}--{recorddata['id']}"
        else:
            alert_message = 'Record not found or already deleted.'

        query = '''
          SELECT * from candidate'''
        curs.execute(query)
        candidate = curs.fetchall()

        seleniumquery = '''
          SELECT c.id, a.candidate_id, c.candidatename, c.email, c.contactnumber,a.question_id, a.question_name, a.user_answer ,q.skill FROM answer a JOIN candidate c ON a.candidate_id = c.id
          JOIN questionlist q ON a.question_id = q.id WHERE q.skill = ? '''
        curs.execute(seleniumquery,('Selenium Java',))
        selenium = curs.fetchall()

        sqlquery = '''
          SELECT c.id, a.candidate_id, c.candidatename,  c.email, c.contactnumber,a.question_id, a.question_name, a.user_answer ,q.skill FROM answer a JOIN candidate c ON a.candidate_id = c.id
          JOIN questionlist q ON a.question_id = q.id WHERE q.skill = ?'''
        curs.execute(sqlquery,('SQL',))
        sql = curs.fetchall()

        return redirect(url_for('candidate',candidate=candidate, questionlist=selenium,sqllist=sql,alert=alert_message))


# Route for processing job form
@app.route('/submit_job', methods=['POST'])
def submit_job():
    if request.method == 'POST':
        job_title = request.form['job_title']
        description = request.form['description']
        
        return f"Job Submitted: Job Title: {job_title}, Description: {description}"
    

@app.route('/showdata/<int:selected_id>')
def showdata(selected_id):
     selected = str(selected_id)
     return selected


def evaluate_answer(question, answer):
    print(question)
    print(answer)
    model = genai.GenerativeModel(model_name="models/gemini-1.5-flash")
    prompt = f"""
    Evaluate the answer to the question and respond with a JSON score from 0 to 10 based on correctness and completeness.
    Question: {question}
    Answer: {answer}
    Respond only in this format:{{"score": 10}}"""
    print("prompt",prompt)
    response = model.generate_content(prompt)
    print("Raw Gemini response:", response.text)
    raw = response.text.strip()
    print("🔍 Raw response:", raw)

    try:
    # Try direct load
        score_data = json.loads(raw)
        print("✅ Score:", score_data["score"])
        return score_data["score"]
    except json.JSONDecodeError:
    # Try to extract valid JSON using regex
        match = re.search(r'\{.*?\}', raw, re.DOTALL)
        if match:
            score_data = json.loads(match.group())
            print("✅ Score (fallback):", score_data["score"])
            return score_data["score"]
        else:
            print("❌ Still failed to extract JSON.")



@app.route('/findscore/<int:record_id>' ,methods=['POST'])
def findscore(record_id):
    with get_db() as conn:
        curs = conn.cursor()
        print("score id",record_id)

        curs.execute("SELECT * FROM candidate where id = ?",(record_id,))
        candidate = curs.fetchall()

        curs.execute("SELECT * FROM answer a JOIN questionlist q ON a.question_id = q.id WHERE a.candidate_id = ?",
        (record_id,))
        qalist = curs.fetchall()
        for item in qalist:
            question = item["question_name"]
            answer = item["user_answer"]
            score = evaluate_answer(question, answer)
            questionid = item["question_id"]
            candidate_id = item["candidate_id"]
            candidate_name = item["candidate_name"]
          
            curs.execute('''
                INSERT INTO score (question_id, question_name, user_answer,user_score, candidate_id, candidate_name)
                VALUES (?, ?, ?, ?, ?,?)
                ''', (questionid, question, answer,score,candidate_id, candidate_name))
                        
            conn.commit()
            if curs.rowcount > 0:
                print("Data successfully inserted.")
            else:
                print("Error: Data not inserted.")

        curs.execute("SELECT * FROM score a JOIN questionlist q ON a.question_id = q.id WHERE q.skill LIKE ? AND a.candidate_id = ?",
        ("%SQL%", record_id))
        sql_questions = curs.fetchall()

        curs.execute("SELECT * FROM score a JOIN questionlist q ON a.question_id = q.id WHERE q.skill LIKE ? AND a.candidate_id = ?",
        ("%Selenium%", record_id))
        selenium_questions = curs.fetchall()

        findscore = '''SELECT 
        c.id,c.candidatename,c.email,c.contactnumber,COALESCE(AVG(s.user_score), 0) AS user_score,
        CASE 
        WHEN COALESCE(AVG(s.user_score), 0) = 0 THEN 'Not Applicable'
        WHEN COALESCE(AVG(s.user_score), 0) < 6 THEN 'Failed'
        ELSE 'Pass'
        END AS status FROM candidate c LEFT JOIN  score s ON c.id = s.candidate_id GROUP BY 
        c.id, c.candidatename, c.email, c.contactnumber;'''
        curs.execute(findscore)
        candidate = curs.fetchall()


        return render_template('candidate.html',candidate=candidate)


if __name__ == '__main__':
    init_db()
    init_db1()
    init_db2()
    init_db3()
    app.run(debug=True)
