CREATE TABLE IF NOT EXISTS candidate (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    candidatename String NOT NULL,
    email String NOT NULL , unique=True ,
    contactnumber String NOT NULL, unique=True,
);

CREATE TABLE IF NOT EXISTS questionbank (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question String NOT NULL,
    skill String NOT NULL,
    complexlevel String NOT NULL,
);

CREATE TABLE IF NOT EXISTS answer (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question String NOT NULL,
    answer String NOT NULL,
    contactnumber String NOT NULL, db.ForeignKey('candidate.id'),
);

class InterviewAnswer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(200), nullable=False)
    answer = db.Column(db.Text, nullable=False)
    candidate_id = db.Column(db.Integer, db.ForeignKey('candidate.id'), nullable=False)
