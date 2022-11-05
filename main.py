import os


def read_files_quiz(path):
    files_quiz = os.listdir('quiz-questions')
    for file_quiz in files_quiz:
        with open(os.path.join(os.getcwd(), path, file_quiz), 'r', encoding='koi8-r') as file:
            file_contents = file.read()
        print(file_contents)


if __name__ == '__main__':
    PATH_QUIZ = 'quiz-questions'
    read_files_quiz(PATH_QUIZ)
