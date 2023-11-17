import requests
import os
from json import loads
from LoggerClass import Logger
from flask import Flask, request
from AlgorithmTestClass import Test
from threading import Thread


class Bot:
    """
    Bot class for connect to mediator and play tic-tac-toe game
    """
    def __init__(self):
        self._logger = Logger('bot')
        self._session_id = self._get_session_id()
        self._bot_url = self._get_bot_url()
        self._host, self._port = self.get_host_and_port()
        self._mediator_url = self._get_mediator_url()
        self._bot_id = 'resTeam'
        self._bot_password = '(ys#5?e@'
        self._figure = self._registration_request()
        self._logger.send_message(f"BOT_URL: {self._bot_url}", "info")
        self._current_game_field = '_' * 361
        self._thread = None
        self._app = Flask(__name__)

        @self._app.route('/bot/turn', methods=["POST"])
        def make_turn():
            current_game_field = request.json.get("game_field")
            server_response = Test.make_algo_move(current_game_field, self._figure, self._opposite_figure())
            self._logger.send_message(f"Запрос {request} был принят! Ответ сервера: {server_response}", "info")
            return {"game_field": server_response}

    def _opposite_figure(self):
        return 'x' if self._figure == 'o' else 'o'

    def _registration_request(self):
        """
        Registration request to mediator. Response is a Figure to play.
        :return: figure
        """
        request_data = {"bot_id": self._bot_id,
                        "password": self._bot_password,
                        "bot_url": self._bot_url}
        extension = f'/sessions/{self._session_id}/registration'
        self._logger.send_message(request_data, 'info')
        self._logger.send_message(self._mediator_url + extension, 'info')
        figure_response = requests.post(self._mediator_url + extension, json=request_data)
        if not figure_response.ok:
            raise requests.RequestException(f'Registration request failed: {figure_response}')
        raw_response = loads(figure_response.content)
        figure = raw_response['figure']
        self._logger.send_message(f'Бот {self._bot_id} успешно зарегистрирован за фигуру {figure}', 'info')
        return figure

    def listen(self):
        """
        Start listening turn requests from mediator.
        :return:
        """
        try:
            print(self._host, int(self._port))
            self._thread = Thread(target=self._app.run, kwargs={'host': self._host, 'port': self._port})
            self._thread.start()
            self._logger.send_message("Слушатель запущен успешно!", "info")
        except Exception as e:
            self._logger.send_message(f"Ошибка запуска потока: {e}", "error")

    @staticmethod
    def _get_session_id():
        """
        Get session_id from env SESSION_ID
        :return: session_id
        """
        session_id = os.getenv('SESSION_ID')
        if session_id is None:
            raise ValueError('SESSION_ID is not set')
        return session_id

    @staticmethod
    def _get_bot_url():
        """
        Get bot_url from env BOT_URL
        :return: bot_url
        """
        bot_url = os.getenv('BOT_URL')
        if bot_url is None:
            raise ValueError('BOT_URL is not set')
        return bot_url

    def get_host_and_port(self):
        """
        Get host and port from BOT_URL for flask.Flask _app.run()
        :return: host, port
        """
        host = self._bot_url.split(':')[1][2:]
        if host is None:
            raise ValueError('HOST is not set')
        port = self._bot_url.split(':')[2]
        if port is None:
            raise ValueError('PORT is not set')
        return host, port

    @staticmethod
    def _get_mediator_url():
        """
        Get mediator_url from env MEDIATOR_URL
        :return: mediator_url
        """
        mediator_id = os.getenv('MEDIATOR_URL')
        if mediator_id is None:
            raise ValueError('MEDIATOR_URL is not set')
        return mediator_id
