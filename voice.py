#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from subprocess import call
from argparse import ArgumentParser
from re import sub


class voice:

    def __init__(self):

        """
        :param  text             : файл(путь/имя), начальная страница, финальная страница
        :type   text             : text
        :param  reading          : переключатель чтения файла
        :type   reading          : bool
        :method reading_file_pdf : чтение pdf страниц
        :method cyrillic_filter  : фильтрация латинских символов
        :method to_voice         : синтез голоса
        """

        self.text = ""
        self.reading = False
        self.parameters()
        self.install_utility()

        if self.reading:
            self.reading_file_pdf()
            self.cyrillic_filter()
            print(self.text)
            self.to_voice()

    def parameters(self):

        """ установка параметров в файле """

        parser = ArgumentParser()
        parser.add_argument("-s", "--speed", help="Регулировка скорости воспроизведения. Целое число. Запускать с правами администратора. Пример: 25000")
        parser.add_argument("-r", "--read", help="Читать файл. Файл:начало:конец")
        args = parser.parse_args()

        if args.speed:
            self.replace_line_in_file('/etc/festival.scm', 'Audio_Command "aplay',
                                      '(Parameter.set \'Audio_Command "aplay -q -c 1 -t raw -f s16 -r %s $FILE")\n' % args.speed)
        if args.read:
            self.text = args.read
            self.reading = True


    @staticmethod
    def replace_line_in_file(file_name, source_text, replace_text):

        """
        изменение строки в файле
        :param source_text : отрывок текста из строки для поиска в файле
        :type  source_text : str
        :param replace_text: заменяющая строка
        :type  replace_text: str
        """

        word = source_text
        inp = open(file_name).readlines()
        for i in iter(inp):
            if word in i:
                source_text = i

        fileObj = open(file_name, 'r')
        text = fileObj.read()
        fileObj.close()

        fileObj = open(file_name, 'w')
        fileObj.write(text.replace(source_text, replace_text))
        fileObj.close()

    @staticmethod
    def install_utility():

        """
        проверка наличия программы - нет, устанавливаем
        :var  festival: программа синтезирования голоса
        :type festival: str
        """

        try:
            print('Проверка наличия программы festival')
            call(['festival','-v'])
            call('clear')
        except OSError as e:
            print('NO  "festival", начало установки')
            call('sudo apt-get install festival festvox-ru', shell=True)
            call('clear')

        try:
            print('Проверка наличия программы pdftotext')
            call(['pdftotext','-v'])
            call('clear')
        except OSError as e:
            print('NO  "pdftotext", начало установки')
            call('sudo apt-get install poppler-utils', shell=True)
            call('clear')

    def reading_file_pdf(self):

        """
        чтение pdf страниц
        :param  param   : раскладываем ввод на параметры
        :type   param   : array
        :param  command : команда на распаковку pdf
        :type   command : str
        :return text    : текст из файла
        :type   text    : str
        """

        param = self.text.split(":")
        file = param[0]
        start_page = param[1]
        final_page = param[2]
        command = 'pdftotext'
        if start_page:
            command += ' -f ' + start_page
        if final_page:
            command += ' -l ' + final_page
        if file:
            command += ' "%s"' % file
        command += ' temp.txt'
        if file:
            call([command], shell=True)

            textObj = open("temp.txt")
            self.text = []
            for line in textObj.readlines():
                self.text.append(line)
            textObj.close()
            call(['rm temp.txt'], shell=True)

    def cyrillic_filter(self):

        """
        оставляем кирилицу, числа, пробелы, enters
        :return text        : отфильтрованное значение, введенное пользователем
        :type   text        : text
        """

        final_text = ''
        for line in self.text:
            line = sub('[^а-яёА-ЯЁ0-9 \n]', '', line)
            final_text += line

        self.text = final_text

    def to_voice(self):

        """ озвучивание """

        # call('clear')
        print('Чтение...')
        if self.text: call(['echo "%s" | festival --tts --language russian'%self.text], shell=True)
        call('clear')


if __name__ == '__main__':
    obj = voice()
