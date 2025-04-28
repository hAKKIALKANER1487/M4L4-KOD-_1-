import discord
from discord.ext import commands, tasks
from config import TOKEN, DATABASE 
from logic import DB_Manager

# Botun mesajları alabilmesi için bir intents nesnesi oluşturun
intents = discord.Intents.default()
intents.message_content = True

# '!' öneki ile komutlar için bir bot nesnesi oluşturun
bot = commands.Bot(command_prefix='!', intents=intents)

# Abonelikleri ve haberleri saklamak için sözlükler
subscriptions = {}
news_cache = {}

manager = DB_Manager(DATABASE)

# Önceden tanımlanmış bir kaynaktan haberleri göstermek için komut
@bot.command()
async def news(ctx):
    news = manager.get_news()
    if not news:
        await ctx.send("Belirtilen kaynaktan haberler alınamadı.")
        return
    response = "\n".join([f"{entry['title']} - {entry['link']}" for entry in news[:5]])
    if response:
        await ctx.send(response)
    else:
        await ctx.send("Mevcut haber yok.")

# Anahtar kelimeyle bildirimlere abone olmak için komut
@bot.command()
async def subscribe(ctx, keyword):
    user_id = ctx.author.id
    if user_id not in subscriptions:
        subscriptions[user_id] = []
    if keyword not in subscriptions[user_id]:
        subscriptions[user_id].append(keyword)
        await ctx.send(f"Anahtar kelime için bildirimlere abone oldunuz: {keyword}")
    else:
        await ctx.send(f"Zaten şu anahtar kelime için bildirimlere abonesiniz: {keyword}")

# Anahtar kelimeyle bildirim aboneliğinden çıkmak için komut
@bot.command()
async def unsubscribe(ctx, keyword):
    user_id = ctx.author.id
    if user_id in subscriptions and keyword in subscriptions[user_id]:
        subscriptions[user_id].remove(keyword)
        await ctx.send(f"Anahtar kelime için bildirim aboneliğiniz kaldırıldı: {keyword}")
    else:
        await ctx.send(f"Bu anahtar kelime için bildirimlere abone değilsiniz: {keyword}")

# Mevcut abonelikleri göstermek için komut
@bot.command()
async def notifications(ctx):
    user_id = ctx.author.id
    if user_id in subscriptions and subscriptions[user_id]:
        response = "Aşağıdaki anahtar kelimelere abonesiniz:\n" + "\n".join(subscriptions[user_id])
    else:
        response = "Hiçbir anahtar kelimeye abone değilsiniz."
    await ctx.send(response)

# Tüm abonelikler için en son haberleri göstermek için komut
@bot.command()
async def latest(ctx):
    user_id = ctx.author.id
    if user_id in subscriptions and subscriptions[user_id]:
        user_news = []
        for keyword in subscriptions[user_id]:
            if keyword in news_cache:
                user_news.extend(news_cache[keyword])
        response = "\n".join([f"{entry['title']} - {entry['link']}" for entry in user_news[:5]])
        if response:
            await ctx.send(response)
        else:
            await ctx.send("Abonelikleriniz için haber bulunamadı.")
    else:
        await ctx.send("Abonelikleriniz için haber bulunamadı.")

# Her 10 dakikada bir haberleri güncelleyen arka plan görevi
@tasks.loop(minutes=10)
async def update_news():
    news = manager.get_news()
    for entry in news:
        for keyword in subscriptions.values():
            if any(word.lower() in entry['title'].lower() for word in keyword):
                if keyword not in news_cache:
                    news_cache[keyword] = []
                news_cache[keyword].append(entry)

# Mevcut komutlar hakkında bilgi görüntülemek için komut
@bot.command()
async def info(ctx):
    response = (
        "Mevcut komutlar:\n"
        "!news - Belirtilen kaynaktan en son haberleri gösterir.\n"
        "!subscribe <anahtar kelime> - Bir anahtar kelime için bildirimlere abone olun.\n"
        "!unsubscribe <anahtar kelime> - Bir anahtar kelime için abonelikten çıkın.\n"
        "!notifications - Mevcut aboneliklerinizi gösterir.\n"
        "!latest - Tüm abonelikleriniz için en son haberleri gösterir.\n"
        "!info - Bu yardım bilgilerini görüntüler."
    )
    await ctx.send(response)

# Bot başladığında arka plan görevini başlat
@bot.event
async def on_ready():
    update_news.start()
    print(f'{bot.user} olarak giriş yapıldı.')

# Botu config.py'den alınan token ile çalıştır
bot.run("")


import discord
from discord.ext import commands

# "YOUR_BOT_TOKEN" yerine botunuzun token değerini yazın
TOKEN = ''

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

# Komut önekini tanımlama
bot = commands.Bot(command_prefix='!')

# Bot hazır olduğunda tetiklenen bir olay
@bot.event
async def on_ready():
    print(f'{bot.user.name} botu çalışmaya hazır!')

# Yeni bir üye katıldığında tetiklenen bir olay
@bot.event
async def on_member_join(member):
    channel = discord.utils.get(member.guild.text_channels, name='ortak')
    if channel:
        await channel.send(f'Sunucuya hoş geldin, {member.mention}!')

# !ping komutuna basit bir yanıt
@bot.command()
async def ping(ctx):
    await ctx.send('Pong!')

# Kullanıcıyı adıyla selamlayan !hello komutu
@bot.command()
async def hello(ctx):
    await ctx.send(f'Merhaba, {ctx.author.mention}!')

# Kullanıcının mesajını tekrarlayan !echo komutu
@bot.command()
async def echo(ctx, *, message: str):
    await ctx.send(message)

# Komut hata işleme
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Lütfen gerekli tüm argümanları sağlayın')
    elif isinstance(error, commands.CommandNotFound):
        await ctx.send('Komut bulunamadı!')
    else:
        await ctx.send('Komut çalıştırılırken bir hata oluştu.')

# Botu çalıştırma
bot.run("")
