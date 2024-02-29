Run a quiz based on a question/answer .txt data file.

Data File Last Updates:
q_datacloud.txt        2/29/2024

Quiz File format supports multiple choice with multiple selections.  Correct answers indicated by "*".

usage: python3 quizforce.py [-h] [--numQ NUMQ] [--no-shuffle-questions] [--no-shuffle-answers] [--no-feedback] [--no-requiz] quiz_file.txt

ex: python3 quizforce.py --numQ 20 --no-requiz quizdata/q_datacloud.txt

positional arguments:
  quiz_file             Path to the .txt quiz file.

options:
  -h, --help            show this help message and exit

  --analyze             Run analysis on quiz file, looks for duplicates

  --numQ NUMQ           Number of questions to be presented in the quiz.

  --no-shuffle-questions
                        Do Not Shuffle Questions before quizzing.

  --no-shuffle-answers  Do Not Shuffle Answers for each question.

  --no-feedback         Do not provide feedback after each question.

  --no-requiz           Do not requiz on missed questions.
