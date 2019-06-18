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

@BotInformation.register('test')
def test(bot, args):
    a = [1,2]
    bot.send_text(str(a[3]))

BotInformation.use_other_bot_commands(BotV2)
BotInformation.start(safe=True)