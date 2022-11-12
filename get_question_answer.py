import difflib
import json
import os
import re
import random


def create_quiz_from_files_to_json(path, new_path, count_questions_in_file, max_count_files=None):
    """
    Создание файлов json из текстовых фалов в директории path и запись их в директорию new_path
    count_questions_in_file - количество вопросов в одном файле json
    max_count_files - максимальное количество создаваемых файлов
    """
    path_save = os.path.join(os.getcwd(), new_path)
    if not os.path.exists(path_save):
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
                        if max_count_files and max_count_files == number_file:
                            return
    # дописываем остаток вопросов:
    if quiz:
        number_file += 1
        save_data_to_json(quiz, path_save, number_file, 'quiz-questions.json')


def save_data_to_json(data, path_save, number_file, name_file):
    with open(
            os.path.join(path_save, f'{number_file}_{name_file}'), 'w'
    ) as file:
        json.dump(data, file, ensure_ascii=False, indent=5)


def compare_strings(seq1, seq2):
    return difflib.SequenceMatcher(a=seq1.lower(), b=seq2.lower()).ratio() > 0.85


def get_random_quiz(quiz_dir_name='quiz-questions-json'):
    """Загрузка словаря с вопросами из случайного файла"""
    quiz_file_name = random.choice(os.listdir(quiz_dir_name))
    path_quiz_file = os.path.join(os.getcwd(), quiz_dir_name, quiz_file_name)
    with open(path_quiz_file, 'r') as file:
        quiz = json.load(file)
    return quiz


if __name__ == '__main__':
    create_quiz_from_files_to_json(
        path='quiz-questions-original',
        new_path='quiz-questions-json',
        count_questions_in_file=1000,
        max_count_files=5
    )
