Run a quiz based on a question/answer .txt data file.

Quiz File format supports multiple choice with multiple selections

usage: python3 quizforce.py [-h] [--numQ NUMQ] [--no-shuffle-questions] [--no-shuffle-answers] [--no-feedback] [--no-requiz] quiz_file

ex: python3 quizforce.py --numQ 20 --no-requiz quizdata/q_datacloud.txt

positional arguments:
  quiz_file             Path to the .txt quiz file.

options:
  -h, --help            show this help message and exit
  --numQ NUMQ           Number of questions to be presented in the quiz.
  --no-shuffle-questions
                        Do Not Shuffle Questions before quizzing.
  --no-shuffle-answers  Do Not Shuffle Answers for each question.
  --no-feedback         Do not provide feedback after each question.
  --no-requiz           Do not requiz on missed questions.

--start quiz file example--
How can attribute names be modified to match a naming convention in Cloud File Storage target?
Update attribute names in the data stream configuration
*Update field names in the data model
Set preferred attribute names when configuring activation
Use a formula field to update the field name in an activation

To import campaign members into a campaign in CRM a user wants to export the segment to Amazon S3. The resulting file needs to include CRM Campaign ID in the name. How can this outcome be achieved?
Include campaign identifier into the activation name
Hard-code the campaign identifier as a new attribute in the campaign activation
*Include campaign identifier into the filename specification
Include campaign identifier into the segment name

Which two applications automatically create activation targets at the time the application is connected to Data Cloud? (Choose 2)
*Personalization powered by Interaction Studio
Amazon S3
*B2C Commerce
Marketing Cloud Engagement
--end quiz file example--
