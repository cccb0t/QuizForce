from flask import Flask, render_template, request, session, redirect, url_for, flash
from flask_session import Session
import os
from quizforce import Quiz, Answer, Question
import glob
import random
import tempfile
import string

app = Flask(__name__)

# Configure Flask-Session with filesystem storage
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = os.path.join(tempfile.gettempdir(), 'flask_session')
Session(app)

def get_available_quizzes():
    quiz_files = glob.glob('quizdata/*.txt')
    return [os.path.basename(f) for f in quiz_files]

@app.route('/')
def index():
    session.clear()
    quizzes = get_available_quizzes()
    return render_template('index.html', quizzes=quizzes)

@app.route('/configure', methods=['POST'])
def configure():
    quiz_file = request.form.get('quiz_file')
    session['quiz_file'] = quiz_file
    return render_template('configure.html')

@app.route('/start_quiz', methods=['POST'])
def start_quiz():
    # Get configuration from form
    numQ = request.form.get('numQ', type=int)
    shuffle_questions = request.form.get('shuffle_questions') == 'on'
    shuffle_answers = request.form.get('shuffle_answers') == 'on'
    feedback = request.form.get('feedback') == 'on'
    requiz = request.form.get('requiz') == 'on'

    # Load quiz
    quiz = Quiz.from_file(f"quizdata/{session['quiz_file']}")
    questions = quiz.questions
    
    if shuffle_questions:
        random.shuffle(questions)
    
    if numQ and numQ < len(questions):
        questions = questions[:numQ]
    
    # Instead of storing full question strings, store indices and answers
    question_data = []
    for q in questions:
        answers = [{'text': a.answer, 'correct': a.correct} for a in q.answers]
        question_data.append({
            'question': q.question,
            'answers': answers,
            'explanation': q.explanation
        })
    
    # Store minimal quiz state in session
    session['quiz_state'] = {
        'question_data': question_data,
        'current_question': 0,
        'correct_count': 0,
        'total_questions': len(question_data),
        'shuffle_answers': shuffle_answers,
        'feedback': feedback,
        'requiz': requiz,
        'answered_questions': []  # Track answered questions
    }
    
    return redirect(url_for('question'))

@app.route('/question', methods=['GET', 'POST'])
def question():
    if 'quiz_state' not in session:
        return redirect(url_for('index'))
    
    state = session['quiz_state']
    
    # Initialize answered_questions list if needed
    if len(state['answered_questions']) < state['total_questions']:
        state['answered_questions'].extend([None] * (state['total_questions'] - len(state['answered_questions'])))
    
    if request.method == 'POST':
        action = request.form.get('action', 'next')
        
        if action == 'prev' and state['current_question'] > 0:
            state['current_question'] -= 1
            session['quiz_state'] = state
            return redirect(url_for('question'))
            
        if action == 'next' and state['current_question'] < state['total_questions'] - 1:
            state['current_question'] += 1
            session['quiz_state'] = state
            return redirect(url_for('question'))
            
        if action == 'submit':
            # Process answer
            user_answer = request.form.get('answer', '').upper()
            current_q = state['question_data'][state['current_question']]
            
            # Get the current answers (either shuffled or original)
            current_answers = current_q['answers']
            if state['shuffle_answers']:
                if 'shuffled_answers' not in state:
                    state['shuffled_answers'] = {}
                if str(state['current_question']) not in state['shuffled_answers']:
                    state['shuffled_answers'][str(state['current_question'])] = random.sample(current_answers, len(current_answers))
                current_answers = state['shuffled_answers'][str(state['current_question'])]
            
            try:
                if user_answer.isdigit():
                    answer_index = int(user_answer) - 1
                else:
                    answer_index = ord(user_answer) - ord('A')
                
                # Check if answer is correct using the current answer arrangement
                is_correct = current_answers[answer_index]['correct']
                
                # If this is a new answer or changed answer
                old_answer = state['answered_questions'][state['current_question']]
                if old_answer is not None and old_answer != is_correct:
                    if old_answer:  # If the old answer was correct
                        state['correct_count'] -= 1
                    if is_correct:  # If the new answer is correct
                        state['correct_count'] += 1
                elif old_answer is None and is_correct:
                    state['correct_count'] += 1
                
                state['answered_questions'][state['current_question']] = is_correct
                
                if state['feedback']:
                    if is_correct:
                        flash("That's right!", 'success')
                    else:
                        # Get correct answers from current arrangement
                        correct_indices = [i for i, ans in enumerate(current_answers) if ans['correct']]
                        correct_letters = [string.ascii_uppercase[i] for i in correct_indices]
                        flash(f"Incorrect. The correct answer was: {', '.join(correct_letters)}", 'error')
                    
                    if current_q['explanation']:
                        flash(f"Explanation: {current_q['explanation']}", 'info')
                
            except (ValueError, IndexError):
                flash('Invalid answer format', 'error')
            
            session['quiz_state'] = state
    
    # Get current question
    current_q = state['question_data'][state['current_question']]
    
    # If shuffle_answers is enabled, use stored shuffled answers or create new ones
    answers = current_q['answers']
    if state['shuffle_answers']:
        if 'shuffled_answers' not in state:
            state['shuffled_answers'] = {}
        if str(state['current_question']) not in state['shuffled_answers']:
            state['shuffled_answers'][str(state['current_question'])] = random.sample(answers, len(answers))
        answers = state['shuffled_answers'][str(state['current_question'])]
    
    # Create answer choices with labels
    labeled_answers = [
        {
            'label': string.ascii_uppercase[i],
            'text': answer['text'],
            'correct': answer['correct'],
            'selected': state['answered_questions'][state['current_question']] is not None and 
                       ((answer['correct'] and state['answered_questions'][state['current_question']]) or
                        (not answer['correct'] and not state['answered_questions'][state['current_question']]))
        }
        for i, answer in enumerate(answers)
    ]
    
    # Calculate progress
    answered_count = sum(1 for x in state['answered_questions'] if x is not None)
    progress = {
        'current': state['current_question'] + 1,
        'total': state['total_questions'],
        'percentage': (state['correct_count'] / answered_count * 100) if answered_count > 0 else 0
    }
    
    return render_template('question.html', 
                         question=current_q['question'],
                         answers=labeled_answers,
                         progress=progress)

@app.route('/results')
def results():
    if 'quiz_state' not in session:
        return redirect(url_for('index'))
    
    state = session['quiz_state']
    score = (state['correct_count'] / state['total_questions']) * 100
    
    return render_template('results.html', score=score)

if __name__ == '__main__':
    app.run(debug=True) 