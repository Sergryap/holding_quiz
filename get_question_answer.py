import json
import os
import re
import random


def create_quiz_from_files_to_json(path, new_path, count_questions_in_file):
    """
    Создание файлов json из текстовых фалов в директории path и запись их в дирректрию new_path
    count_questions_in_file - количество вопросов в одном файле json
    """
    path_save = os.path.join(os.getcwd(), new_path)
    os.makedirs(path_save)
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
                        number_file = int(number_question / count_questions_in_file)
                        save_data_to_json(quiz, path_save, number_file, 'quiz-questions.json')
                        quiz = []
    # дописываем остаток вопросов:
    if quiz:
        number_file += 1
        save_data_to_json(quiz, path_save, number_file, 'quiz-questions.json')


def save_data_to_json(data, path_save, number_file, name_file):
    with open(
            os.path.join(path_save, f'{number_file}_{name_file}'), 'w'
    ) as file:
        json.dump(data, file, ensure_ascii=False, indent=5)


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
