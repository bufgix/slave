from slave.lib.bots import BotBasic


config = {
    'host': 'chat.freenode.net',
    'port': 6667,
    'channel': "#slavebotpool",
    'boss_name': 'king',
    'bot_prefix': "SLAVEBOT"
}

BotBasic.read_config_from_dict(config)
BotBasic.start()
