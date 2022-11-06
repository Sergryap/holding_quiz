import json
import os
import re
import random


def create_dir(new_dir):
    if not os.path.exists(os.path.join(os.getcwd(), new_dir)):
        os.makedirs(os.path.join(os.getcwd(), new_dir))
    return os.path.join(os.getcwd(), new_dir)


def create_quiz_from_files_to_json(path, new_path):
    path_save = create_dir(new_path)
    files_quiz = os.listdir(path)
    next_answer = False
    pattern = re.compile(r'^(Вопрос|Ответ)\s?(\d*):\n([\s\S]+)')
    for number, file_quiz in enumerate(files_quiz, start=1):
        print(number)
        quiz = []
        with open(os.path.join(os.getcwd(), path, file_quiz), 'r', encoding='koi8-r') as f:
            file = f.read()
        for number_block, block in enumerate(re.split(r'\n{2}', file), start=1):
            info = pattern.search(block)
            if info:
                if info.group(2).isdigit():
                    question = info.group(3)
                    next_answer = True
                elif next_answer:
                    next_answer = False
                    answer = info.group(3)
                    quiz.append({'question': question, 'answer': answer})
        with open(os.path.join(path_save, f'{number}_quiz-questions.json'), 'w') as file:
            json.dump(quiz, file, ensure_ascii=False, indent=5)


def get_random_question():
    path = 'quiz-questions-json'
    files_quiz = os.listdir(path)
    file_random = random.choice(files_quiz)
    file_random_path = os.path.join(os.getcwd(), path, file_random)
    with open(file_random_path, 'r') as file:
        questions = json.load(file)
    question_random = random.choice(questions)
    return question_random['question'], question_random['answer']


if __name__ == '__main__':
    create_quiz_from_files_to_json('quiz-questions_original', 'quiz-questions-json')
