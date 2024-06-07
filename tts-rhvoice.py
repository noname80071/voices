#!/usr/bin/env python3.9

import requests
import shlex
import subprocess
import os
from sys import argv
import string
from random import choice


class Error(Exception):
    def __init__(self, code, msg):
        self.code = code
        self.msg = msg


def generate_file_name():
    symbols = list(string.digits)
    file_name = ''

    for i in range(0, 8):
        random_symbol = choice(symbols)
        file_name += random_symbol
    return file_name


class TTS:
    TTS_URL = "{}/say"

    def __init__(self, voice_text, url='http://192.168.2.22:8080', voice='anna', format_='mp3'):
        self._url = self.TTS_URL.format(url)
        self.__params = {
            'text': voice_text,
            'voice': voice,
            'format': format_
        }
        self._data = None
        self._generate()

    def _generate(self):
        try:
            rq = requests.get(self._url, params=self.__params, stream=False)
        except (requests.exceptions.HTTPError, requests.exceptions.RequestException) as e:
            raise Error(code=1, msg=str(e))

        code = rq.status_code
        if code != 200:
            raise Error(code=code, msg='http code != 200')
        self._data = rq.iter_content()

    def save(self, file_path):
        if self._data is None:
            raise Exception('There\'s nothing to save')

        with open(file_path, 'wb') as f:
            for d in self._data:
                f.write(d)
            f.close()
        return file_path


def main(file):
    with open(file, 'r') as f:
        text = f.read()
        f.close()
    tts = TTS(voice_text=text)
    file_name = generate_file_name()
    voice_path = tts.save(f'/var/spool/asterisk/tmp/{file_name}.mp3')
    devnull = open(os.devnull, 'w')
    subprocess.run(shlex.split(f'ffmpeg -y -i /var/spool/asterisk/tmp/{file_name}.mp3 -acodec pcm_s16le -ac 1 -ar 8000 '
                               f'/var/spool/asterisk/tmp/{file_name}.wav'), stdout=devnull, stderr=devnull)
    os.remove(f'/var/spool/asterisk/tmp/{file_name}.mp3')

    print(voice_path.strip('.mp3'))


if __name__ == '__main__':
    text_file = argv[1]
    main(text_file)
