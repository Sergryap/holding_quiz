import json
import os
import re
import random


def create_dir(new_dir):
    if not os.path.exists(os.path.join(os.getcwd(), new_dir)):
        os.makedirs(os.path.join(os.getcwd(), new_dir))
    return os.path.join(os.getcwd(), new_dir)


def create_quiz_from_files_to_json(path, new_path, count_questions_in_file):
    path_save = create_dir(new_path)
    files_quiz = os.listdir(path)
    next_answer = False
    pattern = re.compile(r'^(Вопрос|Ответ)\s*(\d*):?\n+([\s\S]+)')
    number_question = 0
    quiz = []

    for file_quiz in files_quiz:
        with open(os.path.join(os.getcwd(), path, file_quiz), 'r', encoding='koi8-r') as file_content:
            file_text = file_content.read()

        for block in re.split(r'\n{2}\n*', file_text):
            info = pattern.search(block)
            if info:
                if info.group(2).isdigit():
                    number_question += 1
                    question = info.group(3)
                    next_answer = True
                elif next_answer:
                    next_answer = False
                    answer = info.group(3)
                    quiz.append({
                        'question': question,
                        'answer': answer,
                        'number': number_question,
                    })

                    if number_question % count_questions_in_file == 0:
                        number_file = number_question / count_questions_in_file
                        with open(
                                os.path.join(path_save, f'{number_file}_quiz-questions.json'), 'w'
                        ) as file:
                            json.dump(quiz, file, ensure_ascii=False, indent=5)
                        quiz = []


def get_random_question(path_name='quiz-questions-json'):
    files_quiz = os.listdir(path_name)
    file_random = random.choice(files_quiz)
    file_random_path = os.path.join(os.getcwd(), path_name, file_random)
    with open(file_random_path, 'r') as file:
        questions = json.load(file)
    question_random = random.choice(questions)
    return question_random['question'], question_random['answer'], question_random['number']


if __name__ == '__main__':
    create_quiz_from_files_to_json('quiz-questions-original', 'quiz-questions-json', 50)
