import os
import re
from pprint import pprint


def create_quiz_questions(path):
    quiz = {}
    files_quiz = os.listdir(path)
    next_answer = False
    number = 0
    pattern = re.compile(r'^(Вопрос|Ответ)\s?(\d*):\n([\s\S]+)')

    for file_quiz in files_quiz:
        with open(os.path.join(os.getcwd(), path, file_quiz), 'r', encoding='koi8-r') as f:
            file = f.read()
        for block in re.split(r'\n{2}', file):
            info = pattern.search(block)
            if info:
                if info.group(2).isdigit():
                    question = info.group(3)
                    next_answer = True
                elif next_answer:
                    next_answer = False
                    number += 1
                    answer = info.group(3)
                    quiz.update({
                        number: {
                            'question': question,
                            'answer': answer,
                        }
                    })
    return quiz


if __name__ == '__main__':
    PATH_QUIZ = 'quiz-questions'
    pprint(create_quiz_questions(PATH_QUIZ))
