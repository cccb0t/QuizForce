#!/usr/bin/env python3

import argparse
import sys
import random
import string

class Answer:
    def __init__(self, answer: str, correct: bool):
        self.answer = answer
        self.correct = correct

    @classmethod
    def from_string(cls, string: str):
        correct = string.startswith('*')
        answer = string[1:] if correct else string
        return cls(answer, correct)

    def __str__(self):
        return ('*' if self.correct else '') + self.answer

class QAE:
    def __init__(self, question: str, answers: list, explanation: str = None):
        self.question = question
        self.answers = answers
        self.explanation = explanation

    @classmethod
    def from_string(cls, string: str):
        parts = string.split('\nExplanation: ')
        lines = parts[0].split('\n')
        question = lines[0]
        answers = list(map(Answer.from_string, lines[1:]))
        explanation = parts[1] if len(parts) > 1 else None
        return cls(question, answers, explanation)

    def __str__(self):
        base = '\n'.join([self.question] + list(map(str, self.answers)))
        return base + ('\nExplanation: ' + self.explanation if self.explanation else '')

class Quiz:
    def __init__(self, questions: list):
        self.questions = questions

    def __str__(self):
        return '\n\n'.join(list(map(str, self.questions)))

    @classmethod
    def run_from_file(cls, path: str, numQ=None, shuffle_questions=True, shuffle_answers=True, feedback=True, requiz=True):
        cls.from_file(path).run(numQ=numQ, shuffle_questions=shuffle_questions, shuffle_answers=shuffle_answers, feedback=feedback, requiz=requiz)

    @classmethod
    def from_string(cls, string: str):
        return cls(list(map(QAE.from_string, string.split('\n\n'))))

    @classmethod
    def from_file(cls, path: str):
        with open(path) as file_handle:
            return cls.from_string(file_handle.read().strip())


    def run(self, numQ=None, shuffle_questions=True, shuffle_answers=True, feedback=True, requiz=True):
        questions = self.questions
        if shuffle_questions:
            random.shuffle(questions)
        if numQ is not None and numQ < len(questions):
            questions = questions[:numQ]

        print(f'Beginning quiz with {len(questions)} questions.')
        question_counter = 0

        def read_answer_indices(num_answers: int) -> list:
            answers = list(filter(lambda x: not x.isspace(), input('Enter all of your answers: ').upper()))
            for answer in answers:
                if answer not in list(string.ascii_uppercase[:num_answers]):
                    print(f'{answer} is not a valid choice. Try again.')
                    return read_answer_indices(num_answers)
            return [string.ascii_uppercase.index(key) for key in answers]

        def ask_question(question: QAE) -> bool:
            nonlocal question_counter
            question_counter += 1
            print(f'Question {question_counter}/{len(questions)}:')
            print(question.question)
            print()
            answers = random.sample(question.answers, len(question.answers)) if shuffle_answers else question.answers
            for key, answer in zip(string.ascii_uppercase, answers):
                print(f'({key}) {answer.answer}')
            answer_indices = set(read_answer_indices(len(answers)))
            correct_indices = set(filter(lambda i: answers[i].correct, range(len(answers))))
            correct = answer_indices == correct_indices
            if feedback:
                if correct:
                    print("\nThat's right!")
                else:
                    correct_answer_string = ', '.join([string.ascii_uppercase[i] for i in correct_indices])
                    print(f'\nNope. The correct answer was {correct_answer_string}.')
            if question.explanation:
                print('\nExplanation:', question.explanation)
            print()
            return correct

        results = list(map(ask_question, questions))
        num_correct = results.count(True)
        num_questions = len(results)
        score = num_correct / num_questions
        print(f'Your score is {num_correct}/{num_questions} ({score * 100:.2f}%)')

        if requiz and num_correct < num_questions:
            print("Now I'll quiz you on the ones you got wrong!")
            wrong_questions = [questions[i] for i, correct in enumerate(results) if not correct]
            Quiz(wrong_questions).run(len(wrong_questions), shuffle_questions, shuffle_answers, feedback, False)

    def analyze(self, path: str):
        with open(path, 'r') as file:
            content = file.read().strip()

        # Split content into QAE units based on \n\n separator
        qae_units = content.split('\n\n')
        correct_options_distribution = {}
        duplicates = {}
        line_number = 1

        for unit in qae_units:
            # Split unit into lines for more detailed analysis
            lines = unit.split('\n')
            question = lines[0]
            answers = lines[1:]
            explanation_index = next((i for i, line in enumerate(answers) if line.startswith('Explanation: ')), None)
            if explanation_index is not None:
                answers = answers[:explanation_index]

            # Calculate correct answers distribution
            correct_answers_count = sum(1 for answer in answers if answer.startswith('*'))
            correct_options_distribution[correct_answers_count] = correct_options_distribution.get(correct_answers_count, 0) + 1

            # Check for and record duplicates
            if question in duplicates:
                duplicates[question].append(line_number)
            else:
                duplicates[question] = [line_number]

            # Update line_number for the next unit
            line_number += len(lines) + 2  # +2 for the separation between QAE units

        # Print correct options distribution
        print("Correct options distribution per question:")
        for count, num_questions in correct_options_distribution.items():
            print(f"{count} correct answer(s): {num_questions} question(s)")

        # Print duplicate questions
        print("\nDuplicate Questions:")
        dup_index = 1
        duplicate_questions = {k: v for k, v in duplicates.items() if len(v) > 1}
        if not duplicate_questions:
            print("None found.")
        else:
            for question, lines in duplicate_questions.items():
                print(f'{dup_index}) found on line(s): {", ".join(map(str, lines))}\n{question}\n')
                dup_index += 1

    def analyze_old(self):
        # Identifying duplicate questions
        seen_questions = {}
        duplicates = []
        correct_answers_distribution = {}

        for question in self.questions:
            if question.question in seen_questions:
                duplicates.append(question.question)
            else:
                seen_questions[question.question] = True
            correct_answers = sum(answer.correct for answer in question.answers)
            correct_answers_distribution[correct_answers] = correct_answers_distribution.get(correct_answers, 0) + 1

        # Printing statistics
        print(f"Total Questions: {len(self.questions)}")
        print(f"Total Unique Questions: {len(seen_questions)}")
        print(f"Total Duplicate Questions: {len(duplicates)}")
        
        for num_correct, count in sorted(correct_answers_distribution.items()):
            print(f"Questions with {num_correct} correct answer{'s' if num_correct != 1 else ''}: {count}")

        if duplicates:
            qcount = 1
            print("\nDuplicate Questions:")
            for dup in set(duplicates):
                print(f"{qcount}) {dup}")
                print()
                qcount=qcount+1

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run a quiz.')
    parser.add_argument('quiz_file', help='Path to the quiz file.')
    parser.add_argument('--numQ', type=int, help='Number of questions to be presented in the quiz.', default=None)
    parser.add_argument('--no-shuffle-questions', action='store_false', dest='shuffle_questions', help='Shuffle questions before quizzing.')
    parser.add_argument('--no-shuffle-answers', action='store_false', dest='shuffle_answers', help='Shuffle answers for each question.')
    parser.add_argument('--no-feedback', action='store_false', dest='feedback', help='Do not provide feedback after each question.')
    parser.add_argument('--no-requiz', action='store_false', dest='requiz', help='Do not requiz on missed questions.')
    parser.add_argument('--analyze', action='store_true', help='Analyze the quiz file for duplicates and statistics instead of running the quiz.')

    args = parser.parse_args()

    if args.analyze:
        quiz = Quiz.from_file(args.quiz_file)
        quiz.analyze(args.quiz_file)
    else:
        Quiz.run_from_file(args.quiz_file, numQ=args.numQ, shuffle_questions=args.shuffle_questions, shuffle_answers=args.shuffle_answers, feedback=args.feedback, requiz=args.requiz)

