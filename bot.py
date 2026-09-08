from collections import defaultdict, deque
import json
import random as random_module
import asyncio
import math
import discord
import requests

from datetime import datetime
from discord.ext import commands

# =========================================================
# ⚙️ CẤU HÌNH
# =========================================================

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents,
    help_command=None
)

CONFIG_FILE = "config.json"
ECONOMY_FILE = "economy.json"
TEAM_FILE = "teams.json"

HELP_GIF = "https://media.giphy.com/media/26BRuo6sLetdllPAQ/giphy.gif"

# =========================================================
# 💾 DATABASE
# =========================================================

def load_json(filename, default):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default

def save_json(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

config = load_json(CONFIG_FILE, {})
economy = load_json(ECONOMY_FILE, {})
teams = load_json(TEAM_FILE, {})

def get_user(user_id):
    uid = str(user_id)
    if uid not in economy:
        economy[uid] = {
            "money": 1000,
            "bank": 0,
            "level": 1,
            "xp": 0,
            "hp": 100,
            "wins": 0,
            "losses": 0
        }
        save_json(ECONOMY_FILE, economy)
    return economy[uid]

# =========================================================
# 🔒 KÊNH BOT
# =========================================================

def check_channel(ctx):
    if ctx.guild is None:
        return True
    gid = str(ctx.guild.id)
    if gid not in config:
        return True
    return ctx.channel.id == config[gid]

@bot.check
async def global_check(ctx):
    return check_channel(ctx)

# =========================================================
# 🚀 READY
# =========================================================

@bot.event
async def on_ready():
    print("=" * 55)
    print(f"🤖 Bot đã đăng nhập: {bot.user}")
    print(f"🆔 ID: {bot.user.id}")
    print(f"🌐 Server: {len(bot.guilds)}")
    print(f"📚 Commands: {len(bot.commands)}")
    print("=" * 55)

    await bot.change_presence(
        activity=discord.Game(name=f"!help | {len(bot.guilds)} server")
    )

# =========================================================
# ✨ HELP MENU
# =========================================================

HELP_DATA = {
    "home": {
        "title": "✨ BẢNG TRỢ GIÚP - 「 ✦ Aziron war ✦ 」",
        "description": (
            "Chào mừng bạn đến với **Aziron war**!\n\n"
            "👉 **Chọn danh mục để mở menu...**\n\n"
            "Bot tổng hợp Game • Fun • RPG • Economy • Team • AI • Music."
        ),
        "fields": []
    },
    "basic": {
        "title": "🛠️ CƠ BẢN",
        "description": "Những lệnh cơ bản.",
        "fields": [
            ("👋 Hello", "`!hello`"), ("🏓 Ping", "`!ping`"),
            ("🤖 Bot Info", "`!botinfo`"), ("👤 User Info", "`!userinfo @user`"),
            ("🖼️ Avatar", "`!avatar @user`"), ("🏰 Server Icon", "`!servericon`"),
            ("📊 Server Info", "`!serverinfo`"), ("🎲 Random", "`!random 1 100`"),
            ("🎯 Roll", "`!roll 100`"), ("🔮 8Ball", "`!8ball câu hỏi`"),
            ("📢 Say", "`!say nội dung`"), ("🆘 Help", "`!help`")
        ]
    },
    "mod": {
        "title": "🔨 QUẢN LÝ",
        "description": "Lệnh quản trị server.",
        "fields": [
            ("🧹 Clear", "`!clear 10`"), ("👢 Kick", "`!kick @user lý do`"),
            ("🔨 Ban", "`!ban @user lý do`"), ("🔓 Unban", "`!unban ID`"),
            ("🔇 Mute", "`!mute @user`"), ("🔊 Unmute", "`!unmute @user`"),
            ("🐌 Slowmode", "`!slowmode 10`"), ("🔒 Lock", "`!lock`"),
            ("🔓 Unlock", "`!unlock`"), ("⚠️ Warn", "`!warn @user lý do`"),
            ("📢 Set Channel", "`!setchannel`"), ("🚫 Block Bot", "`!blockbot`"),
            ("📣 Spam giới hạn", "`!spam 5 nội dung`"),
            ("🛡️ Anti-Nuke", "`!antinuke on/off/status`"),
            ("🚨 Anti-Raid", "`!antiraid on/off/status`"),
            ("🔐 Anti Server Cao", "`!antihigh`"),
            ("📋 Anti Log", "`!antilog`")
        ]
    },
    "utility": {
        "title": "🔧 TIỆN ÍCH",
        "description": "Công cụ hữu ích.",
        "fields": [
            ("🌤️ Weather", "`!weather Hà Nội`"), ("🗳️ Poll", "`!poll câu hỏi`"),
            ("🔄 Reverse", "`!reverse Hello`"), ("⏱️ Uptime", "`!uptime`"),
            ("🧮 Calc", "`!calc 12*5+3`"), ("🎨 Meme", "`!meme`"),
            ("🎨 Tạo meme", "`!memetext trên | dưới`"),
            ("🎬 Hoạt hình", "`!anime`"), ("🤡 Xiếc", "`!circus`")
        ]
    },
    "game": {
        "title": "🎮 GAME",
        "description": "Các trò chơi.",
        "fields": [
            ("🪙 Coin", "`!coin`"), ("🎲 Dice", "`!dice`"),
            ("✊ RPS", "`!rps búa`"), ("🎰 Slots", "`!slots`"),
            ("🔢 Guess", "`!guessnumber`"), ("⬆️⬇️ HighLow", "`!highlow`"),
            ("♠️ Blackjack", "`!blackjack 100`"), ("💣 Mines", "`!mines 100`"),
            ("⚔️ Duel", "`!duel @user 100`"), ("🎯 Bet", "`!bet 100`")
        ]
    },
    "fun": {
        "title": "😂 FUN",
        "description": "Giải trí và tương tác.",
        "fields": [
            ("😂 Joke", "`!joke`"), ("💘 Love", "`!love @user`"),
            ("💯 Rate", "`!rate @user`"), ("🚢 Ship", "`!ship @a @b`"),
            ("🔥 Roast", "`!roast @user`"), ("💖 Compliment", "`!compliment @user`"),
            ("🤗 Hug", "`!hug @user`"), ("💋 Kiss", "`!kiss @user`"),
            ("👋 Slap", "`!slap @user`"), ("🐾 Pat", "`!pat @user`"),
            ("🙌 Highfive", "`!highfive @user`"), ("💃 Dance", "`!dance`"),
            ("😊 Mood", "`!mood`"), ("🧠 IQ", "`!iq @user`"),
            ("🍀 Luck", "`!luck`"), ("🎲 Choose", "`!choose A | B | C`"),
            ("😈 Dare", "`!dare @user`"), ("😂 Mock", "`!mock nội dung`")
        ]
    },
    "rpg": {
        "title": "⚔️ RPG",
        "description": "Hệ thống RPG.",
        "fields": [
            ("👤 Profile", "`!profile`"), ("❤️ HP", "`!hp`"),
            ("⚔️ Attack", "`!attack @user`"), ("🛡️ Defend", "`!defend`"),
            ("💊 Heal", "`!heal`"), ("🐺 Hunt", "`!hunt`"),
            ("☠️ Die", "`!die`"), ("✨ Revive", "`!revive @user`"),
            ("🎒 Inventory", "`!inventory`"), ("⚔️ Battle", "`!battle @user`")
        ]
    },
    "economy": {
        "title": "💰 KINH TẾ",
        "description": "Tiền dùng cho game và hệ thống team.",
        "fields": [
            ("💵 Balance", "`!balance`"), ("🎁 Daily", "`!daily`"),
            ("💼 Work", "`!work`"), ("🏦 Deposit", "`!deposit 100`"),
            ("💸 Withdraw", "`!withdraw 100`"), ("🎁 Give", "`!give @user 100`"),
            ("🏆 Leaderboard", "`!leaderboard`"), ("🎰 Bet", "`!bet 100`"),
            ("🛒 Shop", "`!shop`"), ("🛍️ Buy", "`!buy item`")
        ]
    },
    "team": {
        "title": "👥 TEAM",
        "description": "Tạo team và chơi team battle.",
        "fields": [
            ("➕ Create", "`!teamcreate TênTeam`"),
            ("📨 Invite", "`!teaminvite @user`"),
            ("✅ Join", "`!teamjoin TênTeam`"),
            ("🚪 Leave", "`!teamleave`"),
            ("ℹ️ Info", "`!teaminfo`"),
            ("👥 Members", "`!teammembers`"),
            ("🦵 Kick", "`!teamkick @user`"),
            ("⚔️ Team Game", "`!teambattle`")
        ]
    },
    "ai": {
        "title": "🤖 AI / MEDIA",
        "description": "Các tính năng AI và media.",
        "fields": [
            ("🤖 ChatGPT", "`!chatgpt câu hỏi`"),
            ("🎨 Design", "`!design áo màu đen | số 21`"),
            ("👕 Shirt", "`!shirt mô tả`"),
            ("🧥 Hoodie", "`!hoodie mô tả`"),
            ("🎬 Anime", "`!anime`"), ("😂 Meme", "`!meme`"),
            ("🎪 Circus", "`!circus`")
        ]
    },
    "music": {
        "title": "🎵 MUSIC",
        "description": "Điều khiển music bot.",
        "fields": [
            ("🎤 Join", "`!join`"), ("🚪 Leave", "`!leave`"),
            ("▶️ Play", "`!play tên bài / link`"), ("⏸️ Pause", "`!pause`"),
            ("▶️ Resume", "`!resume`"), ("⏭️ Skip", "`!skip`"),
            ("📜 Queue", "`!queue`"), ("⏹️ Stop", "`!stop`")
        ]
    }
}

def make_help_embed(category="home"):
    data = HELP_DATA.get(category, HELP_DATA["home"])
    embed = discord.Embed(
        title=data["title"],
        description=data["description"],
        color=discord.Color.blurple(),
        timestamp=discord.utils.utcnow()
    )

    if bot.user:
        embed.set_thumbnail(url=bot.user.display_avatar.url)

    embed.set_image(url=HELP_GIF)

    for name, value in data["fields"]:
        embed.add_field(name=name, value=value, inline=True)

    embed.set_footer(text="「 ✦ Aziron war ✦ 」 • Chọn danh mục bên dưới")
    return embed

class HelpSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Cơ bản", value="basic", emoji="🛠️"),
            discord.SelectOption(label="Quản lý", value="mod", emoji="🔨"),
            discord.SelectOption(label="Tiện ích", value="utility", emoji="🔧"),
            discord.SelectOption(label="Game", value="game", emoji="🎮"),
            discord.SelectOption(label="Fun", value="fun", emoji="😂"),
            discord.SelectOption(label="RPG", value="rpg", emoji="⚔️"),
            discord.SelectOption(label="Kinh tế", value="economy", emoji="💰"),
            discord.SelectOption(label="Team", value="team", emoji="👥"),
            discord.SelectOption(label="AI / Media", value="ai", emoji="🤖"),
            discord.SelectOption(label="Music", value="music", emoji="🎵")
        ]
        super().__init__(
            placeholder="👉 Chọn danh mục để mở menu...",
            options=options
        )

    async def callback(self, interaction):
        await interaction.response.edit_message(
            embed=make_help_embed(self.values[0]),
            view=HelpView()
        )

class HomeButton(discord.ui.Button):
    def __init__(self):
        super().__init__(
            label="Trang chủ",
            emoji="🏠",
            style=discord.ButtonStyle.primary
        )

    async def callback(self, interaction):
        await interaction.response.edit_message(
            embed=make_help_embed("home"),
            view=HelpView()
        )

class HelpView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=180)
        self.add_item(HelpSelect())
        self.add_item(HomeButton())

@bot.command(name="help")
async def help_command(ctx):
    await ctx.send(embed=make_help_embed(), view=HelpView())

# =========================================================
# 🛠️ CƠ BẢN
# =========================================================

@bot.command()
async def hello(ctx):
    await ctx.send(f"👋 Xin chào {ctx.author.mention}!")

@bot.command()
async def ping(ctx):
    await ctx.send(f"🏓 Pong! `{round(bot.latency * 1000)}ms`")

@bot.command()
async def botinfo(ctx):
    embed = discord.Embed(title="🤖 Thông tin Bot", color=discord.Color.blurple())
    embed.add_field(name="Bot", value=str(bot.user), inline=False)
    embed.add_field(name="Server", value=len(bot.guilds))
    embed.add_field(name="Commands", value=len(bot.commands))
    embed.set_thumbnail(url=bot.user.display_avatar.url)
    await ctx.send(embed=embed)

@bot.command()
async def avatar(ctx, member: discord.Member = None):
    member = member or ctx.author
    embed = discord.Embed(title=f"🖼️ Avatar của {member.display_name}")
    embed.set_image(url=member.display_avatar.url)
    await ctx.send(embed=embed)

@bot.command()
async def servericon(ctx):
    if not ctx.guild.icon:
        return await ctx.send("❌ Server chưa có icon.")
    embed = discord.Embed(title=f"🏰 Icon - {ctx.guild.name}")
    embed.set_image(url=ctx.guild.icon.url)
    await ctx.send(embed=embed)

@bot.command()
async def serverinfo(ctx):
    g = ctx.guild
    embed = discord.Embed(title=f"🏰 {g.name}", color=discord.Color.blurple())
    embed.add_field(name="👥 Thành viên", value=g.member_count)
    embed.add_field(name="💬 Kênh", value=len(g.channels))
    embed.add_field(name="🎭 Role", value=len(g.roles))
    embed.add_field(name="🆔 ID", value=g.id)
    if g.icon:
        embed.set_thumbnail(url=g.icon.url)
    await ctx.send(embed=embed)

@bot.command()
async def userinfo(ctx, member: discord.Member = None):
    member = member or ctx.author
    embed = discord.Embed(title=f"👤 {member.display_name}", color=member.color)
    embed.add_field(name="Tên", value=str(member), inline=False)
    embed.add_field(name="ID", value=member.id, inline=False)
    if member.joined_at:
        embed.add_field(
            name="Tham gia server",
            value=discord.utils.format_dt(member.joined_at, style="D")
        )
    embed.set_thumbnail(url=member.display_avatar.url)
    await ctx.send(embed=embed)

@bot.command(name="random")
async def random_command(ctx, minimum: int = 1, maximum: int = 100):
    if minimum > maximum:
        minimum, maximum = maximum, minimum
    await ctx.send(
        f"🎯 Random `{minimum} → {maximum}`: "
        f"**{random_module.randint(minimum, maximum)}**"
    )

@bot.command()
async def roll(ctx, maximum: int = 100):
    maximum = max(1, min(maximum, 1000000))
    await ctx.send(f"🎲 Bạn roll được: **{random_module.randint(1, maximum)}**")

@bot.command(name="8ball")
async def eightball(ctx, *, question=None):
    if not question:
        return await ctx.send("🔮 Ví dụ: `!8ball hôm nay có may không?`")
    answers = [
        "✨ Chắc chắn!", "🔥 Có!", "😎 Khả năng rất cao.",
        "🤔 Có thể.", "🎲 Khó nói.", "❌ Không.",
        "💀 Chắc chắn không.", "🌚 Hỏi lại sau."
    ]
    await ctx.send(f"🔮 **8Ball:** {random_module.choice(answers)}")

@bot.command()
@commands.has_permissions(manage_messages=True)
async def say(ctx, *, message):
    try:
        await ctx.message.delete()
    except discord.HTTPException:
        pass
    await ctx.send(message)

# =========================================================
# 🔧 TIỆN ÍCH
# =========================================================

@bot.command()
async def reverse(ctx, *, text):
    await ctx.send(f"🔄 `{text[::-1]}`")

@bot.command()
async def poll(ctx, *, question):
    embed = discord.Embed(title="🗳️ POLL", description=question)
    msg = await ctx.send(embed=embed)
    await msg.add_reaction("👍")
    await msg.add_reaction("👎")

@bot.command()
async def uptime(ctx):
    await ctx.send("🟢 Bot đang hoạt động bình thường!")

@bot.command()
async def calc(ctx, *, expression):
    # Máy tính an toàn: chỉ cho phép số và các phép + - * / % ( )
    allowed = set("0123456789+-*/%.() ")
    if len(expression) > 100 or any(c not in allowed for c in expression):
        return await ctx.send("❌ Biểu thức không hợp lệ.")
    try:
        result = eval(expression, {"__builtins__": {}}, {})
        if isinstance(result, (int, float)) and math.isfinite(result):
            await ctx.send(f"🧮 `{expression}` = **{result}**")
        else:
            await ctx.send("❌ Kết quả không hợp lệ.")
    except Exception:
        await ctx.send("❌ Không thể tính biểu thức.")

@bot.command()
async def weather(ctx, *, city):
    try:
        geo = requests.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={"name": city, "count": 1, "language": "vi", "format": "json"},
            timeout=10
        ).json()
        if not geo.get("results"):
            return await ctx.send("❌ Không tìm thấy địa điểm.")
        loc = geo["results"][0]
        data = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": loc["latitude"],
                "longitude": loc["longitude"],
                "current": "temperature_2m,weather_code,wind_speed_10m"
            },
            timeout=10
        ).json()["current"]
        await ctx.send(
            f"🌤️ **{loc['name']}**\n"
            f"🌡️ Nhiệt độ: **{data['temperature_2m']}°C**\n"
            f"💨 Gió: **{data['wind_speed_10m']} km/h**"
        )
    except Exception:
        await ctx.send("❌ Không lấy được dữ liệu thời tiết.")

# =========================================================
# 🔨 QUẢN LÝ
# =========================================================

@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int = 10):
    amount = max(1, min(amount, 100))
    deleted = await ctx.channel.purge(limit=amount + 1)
    msg = await ctx.send(f"🧹 Đã xóa **{max(0, len(deleted)-1)}** tin nhắn.")
    await asyncio.sleep(3)
    try:
        await msg.delete()
    except discord.HTTPException:
        pass

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason="Không có lý do"):
    await member.kick(reason=reason)
    await ctx.send(f"👢 Đã kick {member.mention}\n📝 {reason}")

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason="Không có lý do"):
    await member.ban(reason=reason)
    await ctx.send(f"🔨 Đã ban {member.mention}\n📝 {reason}")

@bot.command()
@commands.has_permissions(manage_channels=True)
async def slowmode(ctx, seconds: int = 5):
    seconds = max(0, min(seconds, 21600))
    await ctx.channel.edit(slowmode_delay=seconds)
    await ctx.send(f"🐌 Slowmode: **{seconds}s**")

@bot.command()
@commands.has_permissions(manage_channels=True)
async def lock(ctx):
    overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
    overwrite.send_messages = False
    await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
    await ctx.send("🔒 Đã khóa kênh.")

@bot.command()
@commands.has_permissions(manage_channels=True)
async def unlock(ctx):
    overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
    overwrite.send_messages = None
    await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
    await ctx.send("🔓 Đã mở khóa kênh.")

@bot.command()
@commands.has_permissions(kick_members=True)
async def warn(ctx, member: discord.Member, *, reason="Không có lý do"):
    await ctx.send(f"⚠️ {member.mention} đã nhận cảnh cáo!\n📝 {reason}")

@bot.command()
@commands.has_permissions(administrator=True)
async def setchannel(ctx):
    config[str(ctx.guild.id)] = ctx.channel.id
    save_json(CONFIG_FILE, config)
    await ctx.send(f"✅ Bot sẽ hoạt động tại {ctx.channel.mention}")

@bot.command()
@commands.has_permissions(manage_messages=True)
async def spam(ctx, amount: int = 3, *, message="Spam test"):
    # Có giới hạn để tránh flood server.
    amount = max(1, min(amount, 10))
    for _ in range(amount):
        await ctx.send(message)
        await asyncio.sleep(0.6)

@bot.command()
@commands.has_permissions(manage_guild=True)
async def blockbot(ctx):
    await ctx.send("🚫 Chức năng block bot mẫu. Có thể mở rộng thành hệ thống anti-bot.")

# =========================================================
# 🎮 GAME
# =========================================================

@bot.command()
async def coin(ctx):
    await ctx.send(random_module.choice(["🪙 **MẶT NGỬA**", "🪙 **MẶT SẤP**"]))

@bot.command()
async def dice(ctx):
    await ctx.send(f"🎲 Xúc xắc: **{random_module.randint(1, 6)}**")

@bot.command()
async def rps(ctx, choice=None):
    choices = {"búa": "✊", "bao": "✋", "kéo": "✌️"}
    if not choice or choice.lower() not in choices:
        return await ctx.send("✊ `búa` | ✋ `bao` | ✌️ `kéo`")
    choice = choice.lower()
    bot_choice = random_module.choice(list(choices))
    win = (
        (choice == "búa" and bot_choice == "kéo") or
        (choice == "bao" and bot_choice == "búa") or
        (choice == "kéo" and bot_choice == "bao")
    )
    result = "🤝 Hòa!" if choice == bot_choice else ("🎉 Bạn thắng!" if win else "😂 Bạn thua!")
    await ctx.send(
        f"Bạn: {choices[choice]} | Bot: {choices[bot_choice]}\n**{result}**"
    )

@bot.command()
async def slots(ctx):
    emojis = ["🍒", "🍋", "🍉", "⭐", "💎", "7️⃣"]
    result = [random_module.choice(emojis) for _ in range(3)]
    if result[0] == result[1] == result[2]:
        text = "🎉 **JACKPOT!**"
    elif result[0] == result[1] or result[1] == result[2]:
        text = "✨ Hai biểu tượng giống nhau!"
    else:
        text = "😢 Chúc may mắn lần sau!"
    await ctx.send(f"🎰 **{' | '.join(result)}**\n{text}")

@bot.command()
async def highlow(ctx):
    number = random_module.randint(1, 100)
    await ctx.send(
        f"⬆️⬇️ Số bí mật nằm trong **1-100**.\n"
        f"Đoán thử đi! 😏 (Demo gợi ý: `{number}`)"
    )

@bot.command()
async def guess(ctx):
    await guessnumber(ctx)

@bot.command()
async def guessnumber(ctx):
    secret = random_module.randint(1, 20)
    await ctx.send("🔢 Đoán một số từ **1 đến 20** trong 20 giây!")
    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel and m.content.isdigit()
    try:
        m = await bot.wait_for("message", timeout=20, check=check)
        value = int(m.content)
        if value == secret:
            await ctx.send("🎉 Chính xác!")
        elif value < secret:
            await ctx.send(f"📈 Sai! Số đúng lớn hơn **{value}**.")
        else:
            await ctx.send(f"📉 Sai! Số đúng nhỏ hơn **{value}**.")
    except asyncio.TimeoutError:
        await ctx.send(f"⏰ Hết giờ! Đáp án: **{secret}**")

@bot.command()
async def blackjack(ctx, bet: int = 100):
    user = get_user(ctx.author.id)
    bet = max(10, bet)
    if user["money"] < bet:
        return await ctx.send("❌ Bạn không đủ tiền.")
    player = [random_module.randint(2, 11), random_module.randint(2, 11)]
    dealer = [random_module.randint(2, 11), random_module.randint(2, 11)]
    ps = sum(player)
    ds = sum(dealer)
    if ps > ds:
        user["money"] += bet
        result = f"🎉 Thắng **+{bet:,}**"
        user["wins"] += 1
    elif ps == ds:
        result = "🤝 Hòa."
    else:
        user["money"] -= bet
        result = f"💀 Thua **-{bet:,}**"
        user["losses"] += 1
    save_json(ECONOMY_FILE, economy)
    await ctx.send(
        f"♠️ **BLACKJACK**\n"
        f"Bạn: `{player}` = **{ps}**\n"
        f"Bot: `{dealer}` = **{ds}**\n{result}"
    )

@bot.command()
async def mines(ctx, bet: int = 100):
    user = get_user(ctx.author.id)
    bet = max(10, bet)
    if user["money"] < bet:
        return await ctx.send("❌ Bạn không đủ tiền.")
    if random_module.random() < 0.35:
        user["money"] -= bet
        result = f"💣 BOOM! Bạn mất **{bet:,}** coins."
    else:
        reward = bet * 2
        user["money"] += reward
        result = f"💎 Bạn tìm thấy kho báu! **+{reward:,}** coins."
    save_json(ECONOMY_FILE, economy)
    await ctx.send(f"💣 **MINES**\n{result}")

@bot.command()
async def gamehelp(ctx):
    await ctx.send(
        "🎮 **GAME**\n"
        "`!coin` `!dice` `!rps` `!slots` `!guessnumber`\n"
        "`!blackjack 100` `!mines 100` `!bet 100`"
    )

# =========================================================
# 😂 FUN
# =========================================================

@bot.command()
async def joke(ctx):
    jokes = [
        "😂 Tại sao máy tính lạnh? Vì nó mở quá nhiều Windows!",
        "🤣 Code không bug thì lập trình viên lấy gì làm?",
        "😎 Tôi không lười, tôi đang tiết kiệm năng lượng.",
        "🐛 Bug không biến mất, nó chỉ đang trốn."
    ]
    await ctx.send(random_module.choice(jokes))

@bot.command()
async def love(ctx, member: discord.Member = None):
    member = member or ctx.author
    await ctx.send(
        f"💘 {ctx.author.mention} ❤️ {member.mention}: "
        f"**{random_module.randint(0,100)}%**"
    )

@bot.command()
async def rate(ctx, member: discord.Member = None):
    member = member or ctx.author
    await ctx.send(f"⭐ {member.mention}: **{random_module.randint(0,100)}/100**")

@bot.command()
async def ship(ctx, member1: discord.Member, member2: discord.Member):
    await ctx.send(
        f"🚢 {member1.mention} ❤️ {member2.mention}\n"
        f"💘 Hợp nhau: **{random_module.randint(0,100)}%**"
    )

@bot.command()
async def roast(ctx, member: discord.Member = None):
    member = member or ctx.author
    await ctx.send(f"🔥 {member.mention} {random_module.choice(['Não bạn đang loading...','Bạn không lag, bạn chỉ đang ở server khác.','Tôi roast nhẹ thôi nhé 😂'])}")

@bot.command()
async def compliment(ctx, member: discord.Member = None):
    member = member or ctx.author
    await ctx.send(f"💖 {member.mention} {random_module.choice(['Hôm nay bạn rất tuyệt!','Bạn có năng lượng rất tích cực!','Có bạn trong server vui hơn hẳn!'])}")

@bot.command()
async def hug(ctx, member: discord.Member = None):
    member = member or ctx.author
    await ctx.send(f"🤗 {ctx.author.mention} ôm {member.mention}!")

@bot.command()
async def kiss(ctx, member: discord.Member = None):
    member = member or ctx.author
    await ctx.send(f"💋 {ctx.author.mention} gửi một nụ hôn cho {member.mention}!")

@bot.command()
async def slap(ctx, member: discord.Member = None):
    member = member or ctx.author
    await ctx.send(f"👋 {ctx.author.mention} tát nhẹ {member.mention}!")

@bot.command()
async def pat(ctx, member: discord.Member = None):
    member = member or ctx.author
    await ctx.send(f"🐾 {ctx.author.mention} xoa đầu {member.mention}!")

@bot.command()
async def highfive(ctx, member: discord.Member = None):
    member = member or ctx.author
    await ctx.send(f"🙌 {ctx.author.mention} đập tay với {member.mention}!")

@bot.command()
async def dance(ctx):
    await ctx.send("💃🕺 **DANCE TIME!** 🕺💃")

@bot.command()
async def mood(ctx):
    await ctx.send(f"😊 Mood: **{random_module.choice(['Tuyệt vời!','Đang vui!','Hơi buồn ngủ 😴','Tràn đầy năng lượng!'])}**")

@bot.command()
async def iq(ctx, member: discord.Member = None):
    member = member or ctx.author
    await ctx.send(f"🧠 IQ của {member.mention}: **{random_module.randint(1,200)}**")

@bot.command()
async def luck(ctx):
    await ctx.send(f"🍀 May mắn hôm nay: **{random_module.randint(0,100)}%**")

@bot.command()
async def choose(ctx, *, choices):
    items = [x.strip() for x in choices.split("|") if x.strip()]
    if len(items) < 2:
        return await ctx.send("❌ Ví dụ: `!choose ăn | ngủ | chơi game`")
    await ctx.send(f"🎯 Tôi chọn: **{random_module.choice(items)}**")

@bot.command()
async def dare(ctx, member: discord.Member = None):
    member = member or ctx.author
    dares = [
        "Gửi một emoji ngẫu nhiên.",
        "Nói 'Tôi là huyền thoại' 3 lần.",
        "Đổi nickname trong 1 phút.",
        "Tag một người bạn."
    ]
    await ctx.send(f"😈 {member.mention}: **{random_module.choice(dares)}**")

@bot.command()
async def mock(ctx, *, text):
    # Chỉ dùng cho vui, không nên dùng để bắt nạt người khác.
    result = "".join(
        c.upper() if i % 2 == 0 else c.lower()
        for i, c in enumerate(text)
    )
    await ctx.send(f"😂 {result}")

# =========================================================
# 🎨 MEME / MEDIA / DESIGN
# =========================================================

@bot.command()
async def meme(ctx, *, topic=None):
    # Dùng meme ngẫu nhiên từ API công khai.
    try:
        data = requests.get(
            "https://meme-api.com/gimme",
            params={"subreddit": "memes"},
            timeout=10
        ).json()
        url = data.get("url")
        title = data.get("title", "Meme")
        if not url:
            raise ValueError()
        embed = discord.Embed(title=f"😂 {title}", color=discord.Color.orange())
        embed.set_image(url=url)
        if topic:
            embed.set_footer(text=f"Chủ đề yêu cầu: {topic}")
        await ctx.send(embed=embed)
    except Exception:
        await ctx.send("❌ Không lấy được meme lúc này.")

@bot.command(name="memetext")
async def memetext(ctx, *, text):
    # Tạo meme dạng text đẹp trong Discord, không cần thư viện ảnh.
    parts = [x.strip() for x in text.split("|", 1)]
    if len(parts) != 2:
        return await ctx.send("❌ Dùng: `!memetext chữ trên | chữ dưới`")
    embed = discord.Embed(
        title="😂 MEME",
        description=f"**{parts[0].upper()}**\n\n━━━━━━━━━━━━\n\n**{parts[1].upper()}**",
        color=discord.Color.orange()
    )
    await ctx.send(embed=embed)

@bot.command()
async def anime(ctx):
    await ctx.send(
        "🎬 **Anime/hoạt hình**\n"
        "Bạn có thể gửi tên bộ muốn tìm. Ví dụ: `!watch Naruto`.\n"
        "Bot hiện chỉ trả thông tin/link tìm kiếm, không phát nội dung bản quyền."
    )

@bot.command()
async def watch(ctx, *, title):
    query = requests.utils.quote(title)
    await ctx.send(
        f"🎬 Tìm **{title}** trên YouTube:\n"
        f"https://www.youtube.com/results?search_query={query}"
    )

@bot.command()
async def circus(ctx):
    await ctx.send("🎪 🤹 🎪 **SHOW XIẾC BẮT ĐẦU!** 🎪 🤹 🎪")

@bot.command()
async def video(ctx):
    await ctx.send("🎬 Dùng `!watch <tên video>` để tìm video.")

@bot.command()
async def design(ctx, *, description):
    await ctx.send(
        "🎨 **THIẾT KẾ ÁO**\n"
        f"📝 Ý tưởng: **{description}**\n\n"
        "💡 Đây là bản mô tả thiết kế. Muốn tạo ảnh thật, có thể dùng AI image generator."
    )

@bot.command()
async def shirt(ctx, *, description):
    await ctx.send(f"👕 **SHIRT DESIGN**\n🎨 {description}")

@bot.command()
async def hoodie(ctx, *, description):
    await ctx.send(f"🧥 **HOODIE DESIGN**\n🎨 {description}")

# =========================================================
# 🤖 CHATGPT
# =========================================================

@bot.command()
async def chatgpt(ctx, *, question):
    # Cần thêm OPENAI_API_KEY trong biến môi trường nếu muốn bật.
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return await ctx.send(
            "🤖 Chưa bật ChatGPT API.\n"
            "Thêm biến môi trường `OPENAI_API_KEY` rồi khởi động lại bot."
        )

    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "gpt-5.6",
            "input": question
        }
        response = requests.post(
            "https://api.openai.com/v1/responses",
            headers=headers,
            json=payload,
            timeout=60
        )
        data = response.json()

        if response.status_code >= 400:
            return await ctx.send("❌ OpenAI API báo lỗi. Kiểm tra API key/model.")

        answer = data.get("output_text")
        if not answer:
            answer = "🤖 Không nhận được câu trả lời."
        await ctx.send(answer[:1900])

    except Exception:
        await ctx.send("❌ Không thể kết nối AI lúc này.")

# =========================================================
# 🎵 MUSIC
# =========================================================
# Các lệnh dưới đây là bộ điều khiển. Để phát nhạc thật cần
# cài thêm yt-dlp + PyNaCl + FFmpeg. Bản này không tự tải nhạc
# có bản quyền.

@bot.command()
async def join(ctx):
    if not ctx.author.voice:
        return await ctx.send("❌ Bạn phải vào voice trước.")
    channel = ctx.author.voice.channel
    if ctx.voice_client:
        await ctx.voice_client.move_to(channel)
    else:
        await channel.connect()
    await ctx.send(f"🎵 Đã vào **{channel.name}**.")

@bot.command()
async def leave(ctx):
    if not ctx.voice_client:
        return await ctx.send("❌ Bot không ở voice.")
    await ctx.voice_client.disconnect()
    await ctx.send("🚪 Đã rời voice.")

@bot.command()
async def play(ctx, *, query):
    await ctx.send(
        f"🎵 **Music:** `{query}`\n"
        "ℹ️ Bộ điều khiển đã nhận yêu cầu. Muốn phát audio thật cần cấu hình FFmpeg/yt-dlp."
    )

@bot.command()
async def pause(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.pause()
        return await ctx.send("⏸️ Đã pause.")
    await ctx.send("❌ Không có nhạc đang phát.")

@bot.command()
async def resume(ctx):
    if ctx.voice_client and ctx.voice_client.is_paused():
        ctx.voice_client.resume()
        return await ctx.send("▶️ Đã resume.")
    await ctx.send("❌ Không có nhạc đang pause.")

@bot.command()
async def skip(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        return await ctx.send("⏭️ Đã skip.")
    await ctx.send("❌ Không có nhạc đang phát.")

@bot.command()
async def queue(ctx):
    await ctx.send("📜 Queue hiện đang trống.")

@bot.command()
async def stop(ctx):
    if ctx.voice_client and (ctx.voice_client.is_playing() or ctx.voice_client.is_paused()):
        ctx.voice_client.stop()
    await ctx.send("⏹️ Đã dừng nhạc.")

# =========================================================
# ⚔️ RPG
# =========================================================

@bot.command()
async def profile(ctx):
    u = get_user(ctx.author.id)
    embed = discord.Embed(
        title=f"⚔️ PROFILE - {ctx.author.display_name}",
        color=discord.Color.gold()
    )
    for name, value in [
        ("💰 Money", f"{u['money']:,}"),
        ("🏦 Bank", f"{u['bank']:,}"),
        ("⭐ Level", u["level"]),
        ("❤️ HP", f"{u['hp']}/100"),
        ("🏆 Wins", u["wins"]),
        ("💀 Losses", u["losses"])
    ]:
        embed.add_field(name=name, value=value, inline=True)
    embed.set_thumbnail(url=ctx.author.display_avatar.url)
    await ctx.send(embed=embed)

@bot.command()
async def hp(ctx):
    await ctx.send(f"❤️ HP: **{get_user(ctx.author.id)['hp']}/100**")

@bot.command()
async def heal(ctx):
    u = get_user(ctx.author.id)
    u["hp"] = min(100, u["hp"] + 25)
    save_json(ECONOMY_FILE, economy)
    await ctx.send(f"💊 Hồi máu! ❤️ **{u['hp']}/100**")

@bot.command()
async def attack(ctx, member: discord.Member = None):
    member = member or ctx.author
    damage = random_module.randint(5, 30)
    await ctx.send(f"⚔️ {ctx.author.mention} tấn công {member.mention}: **{damage} damage**")

@bot.command()
async def defend(ctx):
    await ctx.send("🛡️ Bạn dựng khiên phòng thủ!")

@bot.command()
async def hunt(ctx):
    u = get_user(ctx.author.id)
    monster, reward = random_module.choice([
        ("🐺 Sói", 50), ("👹 Goblin", 80), ("🐉 Rồng", 250),
        ("👻 Ma", 120), ("🧟 Zombie", 100)
    ])
    earned = random_module.randint(reward // 2, reward)
    u["money"] += earned
    u["xp"] += random_module.randint(5, 20)
    save_json(ECONOMY_FILE, economy)
    await ctx.send(f"⚔️ Gặp **{monster}**!\n💰 +**{earned:,} coins**")

@bot.command()
async def die(ctx):
    u = get_user(ctx.author.id)
    u["hp"] = 0
    save_json(ECONOMY_FILE, economy)
    await ctx.send(f"💀 {ctx.author.mention} đã chết!")

@bot.command()
async def revive(ctx, member: discord.Member = None):
    member = member or ctx.author
    u = get_user(member.id)
    u["hp"] = 100
    save_json(ECONOMY_FILE, economy)
    await ctx.send(f"✨ {member.mention} đã hồi sinh!")

@bot.command()
async def inventory(ctx):
    await ctx.send("🎒 **INVENTORY**\n🗡️ Kiếm gỗ\n🛡️ Khiên gỗ\n❤️ Bình máu x3\n💎 Đá quý x1")

@bot.command()
async def battle(ctx, member: discord.Member):
    if member.bot or member == ctx.author:
        return await ctx.send("❌ Không thể battle người này.")
    winner = random_module.choice([ctx.author, member])
    await ctx.send(f"⚔️ **BATTLE!**\n🏆 Người thắng: {winner.mention}")

# =========================================================
# 💰 ECONOMY
# =========================================================

@bot.command()
async def balance(ctx):
    u = get_user(ctx.author.id)
    await ctx.send(
        f"💰 Ví: `{u['money']:,}`\n"
        f"🏦 Bank: `{u['bank']:,}`\n"
        f"💎 Tổng: `{u['money'] + u['bank']:,}`"
    )

@bot.command()
async def daily(ctx):
    u = get_user(ctx.author.id)
    reward = random_module.randint(500, 1500)
    u["money"] += reward
    save_json(ECONOMY_FILE, economy)
    await ctx.send(f"🎁 Daily: **+{reward:,} coins**")

@bot.command()
async def work(ctx):
    u = get_user(ctx.author.id)
    reward = random_module.randint(100, 700)
    job = random_module.choice(["👨‍💻 Lập trình viên", "🍔 Bán đồ ăn", "🚚 Shipper", "🎮 Streamer"])
    u["money"] += reward
    save_json(ECONOMY_FILE, economy)
    await ctx.send(f"💼 {job}\n💰 +**{reward:,} coins**")

@bot.command()
async def deposit(ctx, amount: int):
    u = get_user(ctx.author.id)
    if amount <= 0 or amount > u["money"]:
        return await ctx.send("❌ Số tiền không hợp lệ.")
    u["money"] -= amount
    u["bank"] += amount
    save_json(ECONOMY_FILE, economy)
    await ctx.send(f"🏦 Đã gửi **{amount:,} coins**.")

@bot.command()
async def withdraw(ctx, amount: int):
    u = get_user(ctx.author.id)
    if amount <= 0 or amount > u["bank"]:
        return await ctx.send("❌ Bank không đủ tiền.")
    u["bank"] -= amount
    u["money"] += amount
    save_json(ECONOMY_FILE, economy)
    await ctx.send(f"💸 Đã rút **{amount:,} coins**.")

@bot.command()
async def give(ctx, member: discord.Member, amount: int):
    sender = get_user(ctx.author.id)
    receiver = get_user(member.id)
    if amount <= 0 or amount > sender["money"]:
        return await ctx.send("❌ Bạn không đủ tiền.")
    sender["money"] -= amount
    receiver["money"] += amount
    save_json(ECONOMY_FILE, economy)
    await ctx.send(f"🎁 Đã chuyển **{amount:,} coins** cho {member.mention}.")

@bot.command()
async def leaderboard(ctx):
    ranking = sorted(
        economy.items(),
        key=lambda x: x[1]["money"] + x[1]["bank"],
        reverse=True
    )
    text = ""
    for i, (uid, data) in enumerate(ranking[:10], 1):
        member = ctx.guild.get_member(int(uid))
        name = member.display_name if member else f"User {uid}"
        total = data["money"] + data["bank"]
        text += f"**{i}.** {name} — 💰 `{total:,}`\n"
    await ctx.send(embed=discord.Embed(
        title="🏆 BẢNG XẾP HẠNG",
        description=text or "Chưa có dữ liệu.",
        color=discord.Color.gold()
    ))

@bot.command()
async def bet(ctx, amount: int = 100):
    u = get_user(ctx.author.id)
    amount = max(10, amount)
    if u["money"] < amount:
        return await ctx.send("❌ Bạn không đủ tiền.")
    if random_module.random() < 0.5:
        u["money"] += amount
        result = f"🎉 Thắng **+{amount:,}**"
    else:
        u["money"] -= amount
        result = f"💀 Thua **-{amount:,}**"
    save_json(ECONOMY_FILE, economy)
    await ctx.send(f"🎲 BET\n{result}")

@bot.command()
async def shop(ctx):
    await ctx.send(
        "🛒 **SHOP**\n"
        "⚔️ `sword` — 500 coins\n"
        "🛡️ `shield` — 700 coins\n"
        "❤️ `potion` — 250 coins\n"
        "Dùng `!buy sword`"
    )

@bot.command()
async def buy(ctx, item):
    prices = {"sword": 500, "shield": 700, "potion": 250}
    item = item.lower()
    if item not in prices:
        return await ctx.send("❌ Không có item này.")
    u = get_user(ctx.author.id)
    if u["money"] < prices[item]:
        return await ctx.send("❌ Không đủ tiền.")
    u["money"] -= prices[item]
    save_json(ECONOMY_FILE, economy)
    await ctx.send(f"🛍️ Đã mua **{item}** với `{prices[item]:,}` coins.")

# =========================================================
# 👥 TEAM
# =========================================================

def find_team_by_member(user_id):
    uid = str(user_id)
    for name, team in teams.items():
        if uid in team.get("members", []):
            return name, team
    return None, None

@bot.command()
async def teamcreate(ctx, *, name):
    name = name.strip()
    if not name or len(name) > 30:
        return await ctx.send("❌ Tên team không hợp lệ.")
    old_name, _ = find_team_by_member(ctx.author.id)
    if old_name:
        return await ctx.send("❌ Bạn đã ở trong một team.")
    if name in teams:
        return await ctx.send("❌ Team đã tồn tại.")
    teams[name] = {
        "owner": str(ctx.author.id),
        "members": [str(ctx.author.id)],
        "invites": []
    }
    save_json(TEAM_FILE, teams)
    await ctx.send(f"👥 Đã tạo team **{name}**!")

@bot.command()
async def teaminvite(ctx, member: discord.Member):
    name, team = find_team_by_member(ctx.author.id)
    if not name:
        return await ctx.send("❌ Bạn chưa có team.")
    if team["owner"] != str(ctx.author.id):
        return await ctx.send("❌ Chỉ đội trưởng mới mời được.")
    if str(member.id) in team["members"]:
        return await ctx.send("❌ Người này đã ở trong team.")
    if str(member.id) not in team["invites"]:
        team["invites"].append(str(member.id))
    save_json(TEAM_FILE, teams)
    await ctx.send(f"📨 Đã mời {member.mention} vào **{name}**.")

@bot.command()
async def teamjoin(ctx, *, name):
    if name not in teams:
        return await ctx.send("❌ Không tìm thấy team.")
    old_name, _ = find_team_by_member(ctx.author.id)
    if old_name:
        return await ctx.send("❌ Bạn đã ở trong team.")
    team = teams[name]
    if str(ctx.author.id) not in team["invites"]:
        return await ctx.send("❌ Bạn chưa được mời vào team.")
    team["members"].append(str(ctx.author.id))
    team["invites"].remove(str(ctx.author.id))
    save_json(TEAM_FILE, teams)
    await ctx.send(f"✅ Bạn đã vào team **{name}**.")

@bot.command()
async def teamleave(ctx):
    name, team = find_team_by_member(ctx.author.id)
    if not name:
        return await ctx.send("❌ Bạn chưa ở trong team.")
    if team["owner"] == str(ctx.author.id):
        return await ctx.send("❌ Đội trưởng không thể rời. Hãy tạo team mới hoặc chuyển owner.")
    team["members"].remove(str(ctx.author.id))
    save_json(TEAM_FILE, teams)
    await ctx.send(f"🚪 Đã rời team **{name}**.")

@bot.command()
async def teaminfo(ctx):
    name, team = find_team_by_member(ctx.author.id)
    if not name:
        return await ctx.send("❌ Bạn chưa có team.")
    await ctx.send(
        f"👥 **TEAM: {name}**\n"
        f"👑 Owner: <@{team['owner']}>\n"
        f"👥 Thành viên: **{len(team['members'])}**"
    )

@bot.command()
async def teammembers(ctx):
    name, team = find_team_by_member(ctx.author.id)
    if not name:
        return await ctx.send("❌ Bạn chưa có team.")
    members = "\n".join(f"• <@{uid}>" for uid in team["members"])
    await ctx.send(f"👥 **{name}**\n{members}")

@bot.command()
async def teamkick(ctx, member: discord.Member):
    name, team = find_team_by_member(ctx.author.id)
    if not name:
        return await ctx.send("❌ Bạn chưa có team.")
    if team["owner"] != str(ctx.author.id):
        return await ctx.send("❌ Chỉ đội trưởng.")
    uid = str(member.id)
    if uid not in team["members"] or uid == team["owner"]:
        return await ctx.send("❌ Người này không thể bị kick.")
    team["members"].remove(uid)
    save_json(TEAM_FILE, teams)
    await ctx.send(f"🦵 Đã kick {member.mention} khỏi **{name}**.")

@bot.command()
async def teambattle(ctx):
    name, team = find_team_by_member(ctx.author.id)
    if not name:
        return await ctx.send("❌ Bạn chưa có team.")
    team_size = len(team["members"])
    if team_size < 2:
        return await ctx.send("❌ Team cần ít nhất 2 thành viên.")
    reward = random_module.randint(200, 600) * team_size
    each = reward // team_size
    for uid in team["members"]:
        get_user(int(uid))["money"] += each
    save_json(ECONOMY_FILE, economy)
    await ctx.send(
        f"⚔️ **TEAM BATTLE**\n"
        f"👥 Team: **{name}**\n"
        f"🏆 Thắng trận!\n"
        f"💰 Mỗi thành viên nhận **{each:,} coins**"
    )

# Alias team ngắn gọn
@bot.command(name="team")
async def team_help(ctx):
    await ctx.send(
        "👥 `!teamcreate tên` | `!teaminvite @user` | `!teamjoin tên`\n"
        "`!teamleave` | `!teaminfo` | `!teammembers` | `!teambattle`"
    )

# =========================================================
# 🧩 ALIAS CŨ
# =========================================================

@bot.command()
async def buax(ctx):
    await ctx.send("✊ Búa!")

@bot.command()
async def xui(ctx):
    await ctx.send(f"🍀 Độ xui: **{random_module.randint(0,100)}%**")

@bot.command()
async def phat(ctx):
    await ctx.send("💥 Phạt: Hôm nay phải vui vẻ!")

@bot.command()
async def ai_bua(ctx):
    await ctx.send("🤖 AI chọn: **✊ BÚA**")

@bot.command()
async def xam(ctx):
    await ctx.send("🌚 Xàm vừa thôi nhé 😂")

@bot.command()
async def batngo(ctx):
    await ctx.send(random_module.choice(["🎁 Bất ngờ!", "💥 BOOM!", "😂 Bạn bị troll!"]))


# =========================================================
# 🛡️ ANTI SERVER - CHỈ CHỦ SERVER
# =========================================================

ANTI_NUKE_FILE = "antinuke.json"

def load_antinuke():
    try:
        with open(ANTI_NUKE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_antinuke(data):
    with open(ANTI_NUKE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

antinuke_data = load_antinuke()

ANTI_NUKE_LIMITS = {
    "channel_delete": 2,
    "channel_create": 8,
    "role_delete": 2,
    "role_create": 8,
    "ban": 3,
    "kick": 5,
    "webhook_create": 3,
    "bot_add": 3,
}

def get_anti_settings(guild_id):
    gid = str(guild_id)
    if gid not in antinuke_data:
        antinuke_data[gid] = {
            "antinuke": False,
            "antiraid": False,
            "log_channel": None,
            "actions": {}
        }
        save_antinuke(antinuke_data)
    return antinuke_data[gid]

def owner_only():
    async def predicate(ctx):
        if ctx.guild is None:
            await ctx.send("❌ Lệnh này chỉ dùng trong server.")
            return False
        if ctx.author.id == ctx.guild.owner_id:
            return True
        await ctx.send("🚫 Chỉ **CHỦ SERVER (Server Owner)** mới được dùng lệnh Anti.")
        return False
    return commands.check(predicate)

async def anti_log(guild, message):
    settings = get_anti_settings(guild.id)
    channel_id = settings.get("log_channel")
    if not channel_id:
        return
    channel = guild.get_channel(channel_id)
    if not channel:
        return
    try:
        embed = discord.Embed(
            title="🛡️ ANTI SERVER LOG",
            description=message,
            color=discord.Color.red(),
            timestamp=discord.utils.utcnow()
        )
        await channel.send(embed=embed)
    except Exception as e:
        print("Anti log error:", e)

async def punish_nuker(guild, member, reason):
    if member is None or member == guild.owner:
        return
    # Không tự động xử lý Admin để tránh bot gây xung đột quyền.
    if member.guild_permissions.administrator:
        await anti_log(
            guild,
            f"⚠️ Phát hiện hành động đáng ngờ từ Admin {member.mention}.\n"
            f"**Lý do:** {reason}\n"
            f"Bot không tự ban Admin."
        )
        return
    try:
        await member.ban(
            reason=f"Anti-Nuke: {reason}",
            delete_message_days=0
        )
        await anti_log(
            guild,
            f"🚨 Đã **BAN** {member.mention}\n**Lý do:** {reason}"
        )
    except discord.Forbidden:
        await anti_log(
            guild,
            f"⚠️ Không thể ban {member.mention}. "
            f"Kiểm tra quyền **Ban Members** và role của bot."
        )
    except Exception as e:
        print("Punish error:", e)

async def record_anti_action(guild, member, action):
    if member is None:
        return
    settings = get_anti_settings(guild.id)
    actions = settings.setdefault("actions", {})
    uid = str(member.id)

    if uid not in actions:
        actions[uid] = {}
    if action not in actions[uid]:
        actions[uid][action] = []

    now = time.time()
    actions[uid][action] = [
        t for t in actions[uid][action]
        if now - t <= 10
    ]
    actions[uid][action].append(now)

    limit = ANTI_NUKE_LIMITS.get(action, 999)
    if len(actions[uid][action]) >= limit:
        await punish_nuker(
            guild,
            member,
            f"{action}: {len(actions[uid][action])} lần trong 10 giây"
        )
        actions[uid][action] = []

    save_antinuke(antinuke_data)

@bot.event
async def on_audit_log_entry_create(entry):
    guild = entry.guild
    if guild is None:
        return

    settings = get_anti_settings(guild.id)
    if not settings.get("antinuke"):
        return

    actor = entry.user
    if actor is None or actor.id == guild.owner_id:
        return
    if actor.guild_permissions.administrator:
        return

    action_map = {
        discord.AuditLogAction.channel_delete: "channel_delete",
        discord.AuditLogAction.channel_create: "channel_create",
        discord.AuditLogAction.role_delete: "role_delete",
        discord.AuditLogAction.role_create: "role_create",
        discord.AuditLogAction.ban: "ban",
        discord.AuditLogAction.kick: "kick",
        discord.AuditLogAction.webhook_create: "webhook_create",
        discord.AuditLogAction.bot_add: "bot_add",
    }
    action_name = action_map.get(entry.action)
    if action_name:
        await record_anti_action(guild, actor, action_name)

raid_joins = defaultdict(deque)

@bot.event
async def on_member_join(member):
    settings = get_anti_settings(member.guild.id)
    if not settings.get("antiraid"):
        return

    now = time.time()
    joins = raid_joins[member.guild.id]
    joins.append(now)

    while joins and now - joins[0] > 10:
        joins.popleft()

    if len(joins) >= 8:
        try:
            await member.timeout(
                timedelta(minutes=10),
                reason="Anti-Raid"
            )
            await anti_log(
                member.guild,
                f"🚨 Phát hiện **RAID**!\n"
                f"👤 Thành viên: {member.mention}\n"
                f"📊 {len(joins)} lượt tham gia trong 10 giây\n"
                f"🔒 Đã timeout thành viên 10 phút."
            )
        except discord.Forbidden:
            await anti_log(
                member.guild,
                "⚠️ Phát hiện raid nhưng bot thiếu quyền "
                "**Moderate Members**."
            )
        except Exception as e:
            print("Anti-Raid error:", e)

@bot.command()
@owner_only()
async def antinuke(ctx, mode=None):
    settings = get_anti_settings(ctx.guild.id)

    if mode is None:
        return await ctx.send(
            "🛡️ **ANTI-NUKE**\n\n"
            "`!antinuke on` → Bật\n"
            "`!antinuke off` → Tắt\n"
            "`!antinuke status` → Kiểm tra"
        )

    mode = mode.lower()
    if mode == "on":
        settings["antinuke"] = True
        save_antinuke(antinuke_data)
        await ctx.send("🛡️ **ANTI-NUKE ĐÃ BẬT!**")
    elif mode == "off":
        settings["antinuke"] = False
        save_antinuke(antinuke_data)
        await ctx.send("🔓 **Anti-Nuke đã tắt.**")
    elif mode == "status":
        status = "🟢 BẬT" if settings.get("antinuke") else "🔴 TẮT"
        await ctx.send(f"🛡️ **Anti-Nuke:** {status}")
    else:
        await ctx.send(
            "❌ Dùng: `!antinuke on`, `!antinuke off`, "
            "hoặc `!antinuke status`"
        )

@bot.command()
@owner_only()
async def antiraid(ctx, mode=None):
    settings = get_anti_settings(ctx.guild.id)

    if mode is None:
        return await ctx.send(
            "🚨 **ANTI-RAID**\n\n"
            "`!antiraid on` → Bật\n"
            "`!antiraid off` → Tắt\n"
            "`!antiraid status` → Kiểm tra"
        )

    mode = mode.lower()
    if mode == "on":
        settings["antiraid"] = True
        save_antinuke(antinuke_data)
        await ctx.send("🚨 **ANTI-RAID ĐÃ BẬT!**")
    elif mode == "off":
        settings["antiraid"] = False
        save_antinuke(antinuke_data)
        await ctx.send("🔓 **Anti-Raid đã tắt.**")
    elif mode == "status":
        status = "🟢 BẬT" if settings.get("antiraid") else "🔴 TẮT"
        await ctx.send(f"🚨 **Anti-Raid:** {status}")
    else:
        await ctx.send(
            "❌ Dùng: `!antiraid on`, `!antiraid off`, "
            "hoặc `!antiraid status`"
        )

@bot.command()
@owner_only()
async def antihigh(ctx):
    settings = get_anti_settings(ctx.guild.id)
    settings["antinuke"] = True
    settings["antiraid"] = True
    save_antinuke(antinuke_data)
    await ctx.send(
        "🔐 **ANTI SERVER CAO ĐÃ BẬT!**\n\n"
        "🛡️ Anti-Nuke: 🟢\n"
        "🚨 Anti-Raid: 🟢\n\n"
        "Server đang được bảo vệ."
    )

@bot.command()
@owner_only()
async def antilog(ctx):
    settings = get_anti_settings(ctx.guild.id)
    settings["log_channel"] = ctx.channel.id
    save_antinuke(antinuke_data)
    await ctx.send(
        f"📋 Đã đặt {ctx.channel.mention} làm kênh Anti Log."
    )

# =========================================================
# ❌ ERROR
# =========================================================

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        return
    if isinstance(error, commands.CommandNotFound):
        return
    if isinstance(error, commands.MissingPermissions):
        return await ctx.send("🚫 Bạn không có quyền dùng lệnh này.")
    if isinstance(error, commands.MissingRequiredArgument):
        return await ctx.send("❌ Thiếu thông tin. Dùng `!help`.")
    if isinstance(error, commands.MemberNotFound):
        return await ctx.send("❌ Không tìm thấy thành viên.")
    if isinstance(error, commands.BadArgument):
        return await ctx.send("❌ Sai định dạng lệnh.")
    if isinstance(error, commands.CommandInvokeError):
        print(f"[ERROR] {error.original}")
        return await ctx.send("❌ Lệnh gặp lỗi khi chạy.")
    print(f"[ERROR] {type(error).__name__}: {error}")

# =========================================================
# 🌐 RENDER HEALTH SERVER + CHẠY BOT
# =========================================================

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"Bot is online!")

    def log_message(self, format, *args):
        pass

def start_server():
    port = int(os.getenv("PORT", "10000"))
    server = HTTPServer(("0.0.0.0", port), HealthHandler)
    print(f"Web server running on port {port}")
    server.serve_forever()

if os.getenv("PORT"):
    threading.Thread(target=start_server, daemon=True).start()

token = os.getenv("DISCORD_TOKEN")
if not token:
    raise RuntimeError("❌ Thiếu biến môi trường DISCORD_TOKEN")

bot.run(token)
