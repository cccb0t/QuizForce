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

class Question:
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

    @classmethod
    def run_from_file(cls, path: str, numQ=None, shuffle_questions=True, shuffle_answers=True, feedback=True, requiz=True):
        cls.from_file(path).run(numQ=numQ, shuffle_questions=shuffle_questions, shuffle_answers=shuffle_answers, feedback=feedback, requiz=requiz)

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

        def ask_question(question: Question) -> bool:
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

    @classmethod
    def from_string(cls, string: str):
        return cls(list(map(Question.from_string, string.split('\n\n'))))

    @classmethod
    def from_file(cls, path: str):
        with open(path) as file_handle:
            return cls.from_string(file_handle.read().strip())

    def __str__(self):
        return '\n\n'.join(list(map(str, self.questions)))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run a quiz.')
    parser.add_argument('quiz_file', help='Path to the quiz file.')
    parser.add_argument('--numQ', type=int, help='Number of questions to be presented in the quiz.', default=None)
    parser.add_argument('--no-shuffle-questions', action='store_false', dest='shuffle_questions', help='Shuffle questions before quizzing.')
    parser.add_argument('--no-shuffle-answers', action='store_false', dest='shuffle_answers', help='Shuffle answers for each question.')
    parser.add_argument('--no-feedback', action='store_false', dest='feedback', help='Do not provide feedback after each question.')
    parser.add_argument('--no-requiz', action='store_false', dest='requiz', help='Do not requiz on missed questions.')

    args = parser.parse_args()

    Quiz.run_from_file(args.quiz_file, numQ=args.numQ, shuffle_questions=args.shuffle_questions, shuffle_answers=args.shuffle_answers, feedback=args.feedback, requiz=args.requiz)

