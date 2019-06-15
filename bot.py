from slave.lib.bots import BotBasic

config = {
    'host': 'chat.freenode.net',
    'port': 6667,
    'channel': "#slavebotpool666",
    'boss_name': 'boss666',
    'bot_prefix': "SLAVEBOT"
}
BotBasic.read_config_from_dict(config)

## Write custom commands here


BotBasic.start()
