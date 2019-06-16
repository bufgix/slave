from slave.lib.bots import BotV2

config = {
    'host': 'chat.freenode.net',
    'port': 6667,
    'channel': "#slavebotpool666",
    'boss_name': 'boss666',
    'bot_prefix': "SLAVEBOT"
}
BotV2.read_config_from_dict(config)

## Write custom commands here


BotV2.start()
