import json
import os
import re
import random


def create_quiz_from_files_to_json(path):
    quiz = {
        'questions': {},
        'count': None
    }
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
                    quiz['questions'].update({
                        number: {
                            'question': question,
                            'answer': answer,
                        }
                    })
    quiz['count'] = number

    with open('quiz-questions.json', 'w') as file:
        json.dump(quiz, file, ensure_ascii=False, indent=5)


def get_random_question():
    if not os.path.isfile('quiz-questions.json'):
        create_quiz_from_files_to_json('quiz-questions')
    with open('quiz-questions.json', 'r') as file:
        questions = json.load(file)
    number_question = str(random.randint(1, questions['count']))
    return (
        questions['questions'][number_question]['question'],
        questions['questions'][number_question]['answer']
    )


if __name__ == '__main__':
    create_quiz_from_files_to_json('quiz-questions')
