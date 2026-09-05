import discord
from discord.ext import commands
import random
import requests
import json
import os


# =========================
# CÀI ĐẶT BOT
# =========================

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)

# Bỏ help mặc định
bot.remove_command("help")


# =========================
# LƯU KÊNH BOT
# =========================

CONFIG_FILE = "config.json"


def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}

    return {}


def save_config(config):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4)


config = load_config()


# =========================
# BOT ONLINE
# =========================

@bot.event
async def on_ready():
    print(f"Bot đã đăng nhập: {bot.user}")
    print("Bot đang hoạt động!")


# =========================
# CHỈ CHO PHÉP DÙNG BOT Ở 1 KÊNH
# =========================

@bot.check
async def check_channel(ctx):

    # !setchannel luôn được phép sử dụng
    if ctx.command and ctx.command.name == "setchannel":
        return True

    # Nếu chưa cài kênh thì cho phép dùng bình thường
    if "channel_id" not in config:
        return True

    # Chỉ cho phép lệnh ở kênh đã cài
    return ctx.channel.id == config["channel_id"]


@bot.command()
@commands.has_permissions(administrator=True)
async def setchannel(ctx):

    config["channel_id"] = ctx.channel.id
    save_config(config)

    await ctx.send(
        "✅ **Đã đặt kênh này làm kênh sử dụng bot!**\n"
        "🔒 Bot sẽ nhớ kênh này kể cả khi khởi động lại."
    )


# =========================
# CHẶN BOT KHÁC NHẮN TIN
# =========================

@bot.command()
@commands.has_permissions(manage_channels=True)
async def blockbot(ctx, member: discord.Member):

    if not member.bot:
        await ctx.send("❌ Người này không phải bot!")
        return

    try:
        await ctx.channel.set_permissions(
            member,
            send_messages=False
        )

        await ctx.send(
            f"✅ Đã chặn {member.mention} nhắn tin trong kênh này!"
        )

    except discord.Forbidden:
        await ctx.send(
            "❌ Bot của mình không có quyền **Manage Channels**!"
        )


# =========================
# LỆNH CƠ BẢN
# =========================

@bot.command()
async def hello(ctx):
    await ctx.send(
        f"👋 Xin chào {ctx.author.mention}!"
    )


@bot.command()
async def ping(ctx):
    await ctx.send("🏓 Pong!")


@bot.command()
async def help(ctx):

    embed = discord.Embed(
        title="📚 MENU LỆNH BOT",
        description=(
            "━━━━━━━━━━━━━━━━━━━━\n"
            "✨ **Danh sách lệnh bot**\n"
            "━━━━━━━━━━━━━━━━━━━━"
        ),
        color=discord.Color.blue()
    )

    embed.add_field(
        name="🛠️ ┃ LỆNH CƠ BẢN",
        value=(
            "`!ping` → Kiểm tra bot\n"
            "`!hello` → Bot chào bạn\n"
            "`!serverinfo` → Thông tin server\n"
            "`!userinfo` → Thông tin thành viên\n"
            "`!clear <số>` → Xóa tin nhắn\n"
        ),
        inline=False
    )

    embed.add_field(
        name="🔧 ┃ QUẢN LÝ BOT",
        value=(
            "`!setchannel` → Đặt kênh sử dụng bot\n"
            "`!blockbot @bot` → Chặn bot khác nhắn tin"
        ),
        inline=False
    )

    embed.add_field(
        name="🔧 ┃ TIỆN ÍCH",
        value=(
            "`!weather <địa điểm>` → Xem thời tiết\n"
            "`!tiktok <link>` → Gửi link TikTok\n"
            "`!myrole` → Tạo role riêng\n"
            "`!mention @người` → Nhắc thành viên\n"
        ),
        inline=False
    )

    embed.add_field(
        name="🎮 ┃ TRÒ CHƠI",
        value=(
            "`!gamehelp` → Danh sách game\n"
            "`!coinflip` → Tung đồng xu\n"
            "`!dice` → Gieo xúc xắc\n"
            "`!taixiu` → Tài / Xỉu\n"
            "`!rps <kéo/búa/bao>` → Kéo búa bao\n"
            "`!guess` → Bắt đầu đoán số\n"
            "`!guessnumber <số>` → Đoán số\n"
        ),
        inline=False
    )

    embed.add_field(
        name="😂 ┃ FUN",
        value=(
            "`!buax` → Lệnh bựa\n"
            "`!iq` → Đo IQ\n"
            "`!xui` → Độ xui\n"
            "`!phat @người` → Phạt vui\n"
            "`!ai_bua` → Chọn người bựa\n"
            "`!xam` → Lệnh xàm\n"
            "`!batngo` → Bất ngờ\n"
            "`!joke` → Kể chuyện cười\n"
        ),
        inline=False
    )

    embed.add_field(
        name="❤️ ┃ TƯƠNG TÁC",
        value=(
            "`!love @người` → Độ hợp nhau\n"
            "`!luck` → Độ may mắn\n"
            "`!choose A | B | C` → Chọn ngẫu nhiên\n"
            "`!dare @người` → Thử thách\n"
            "`!roast @người` → Cà khịa vui\n"
            "`!compliment @người` → Khen\n"
            "`!hug @người` → Ôm\n"
            "`!dance` → Nhảy\n"
            "`!mood` → Tâm trạng\n"
        ),
        inline=False
    )

    embed.add_field(
        name="⚔️ ┃ RPG",
        value=(
            "`!die` → Chết trong game\n"
            "`!kill @người` → Hạ trong game\n"
            "`!revive @người` → Hồi sinh\n"
            "`!hp` → Kiểm tra HP\n"
        ),
        inline=False
    )

    embed.set_footer(
        text="🤖 Bot của bạn"
    )

    await ctx.send(embed=embed)


# =========================
# SERVER INFO
# =========================

@bot.command()
async def serverinfo(ctx):

    guild = ctx.guild

    embed = discord.Embed(
        title="📊 Thông tin server",
        color=discord.Color.green()
    )

    embed.add_field(
        name="🏠 Tên",
        value=guild.name,
        inline=False
    )

    embed.add_field(
        name="👥 Thành viên",
        value=guild.member_count,
        inline=True
    )

    embed.add_field(
        name="🆔 ID",
        value=guild.id,
        inline=True
    )

    await ctx.send(embed=embed)


# =========================
# USER INFO
# =========================

@bot.command()
async def userinfo(ctx, member: discord.Member = None):

    member = member or ctx.author

    embed = discord.Embed(
        title="👤 Thông tin thành viên",
        color=discord.Color.purple()
    )

    embed.add_field(
        name="Tên",
        value=str(member),
        inline=False
    )

    embed.add_field(
        name="ID",
        value=member.id,
        inline=False
    )

    await ctx.send(embed=embed)


# =========================
# CLEAR
# =========================

@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int):

    if amount < 1:
        await ctx.send("❌ Số lượng phải lớn hơn 0!")
        return

    await ctx.channel.purge(limit=amount + 1)

    msg = await ctx.send(
        f"🗑️ Đã xóa **{amount}** tin nhắn!"
    )

    await msg.delete(delay=3)


# =========================
# TIKTOK
# =========================

@bot.command()
async def tiktok(ctx, link=None):

    if link is None:
        await ctx.send(
            "❌ Hãy nhập link TikTok!\n"
            "Ví dụ: `!tiktok https://www.tiktok.com/...`"
        )
        return

    await ctx.send(
        f"🎵 TikTok của bạn: {link}"
    )


# =========================
# MY ROLE
# =========================

@bot.command()
async def myrole(ctx):

    if ctx.guild is None:
        await ctx.send("❌ Lệnh này chỉ dùng trong server!")
        return

    if not ctx.guild.me.guild_permissions.manage_roles:
        await ctx.send(
            "❌ Bot chưa có quyền **Manage Roles**!"
        )
        return

    role_name = f"Role của {ctx.author.display_name}"

    role = await ctx.guild.create_role(
        name=role_name,
        permissions=discord.Permissions.none(),
        reason=f"Tạo role riêng cho {ctx.author}"
    )

    try:
        await ctx.author.add_roles(role)

    except discord.Forbidden:
        await ctx.send(
            "❌ Bot không thể thêm role này. "
            "Hãy đưa role của bot lên cao hơn."
        )
        return

    await ctx.send(
        f"✅ Đã tạo **{role.name}** "
        f"và thêm role cho {ctx.author.mention}!"
    )


# =========================
# MENTION
# =========================

@bot.command()
@commands.has_permissions(manage_messages=True)
async def mention(ctx, member: discord.Member):

    await ctx.send(
        f"📢 Xin chào {member.mention}!"
    )


# =========================
# GAME
# =========================

@bot.command()
async def coinflip(ctx):

    result = random.choice(
        ["🪙 Ngửa", "🪙 Sấp"]
    )

    await ctx.send(
        f"{ctx.author.mention} tung đồng xu: **{result}**"
    )


@bot.command()
async def dice(ctx):

    number = random.randint(1, 6)

    await ctx.send(
        f"🎲 {ctx.author.mention} gieo xúc xắc: **{number}**"
    )


@bot.command()
async def taixiu(ctx):

    a = random.randint(1, 6)
    b = random.randint(1, 6)
    c = random.randint(1, 6)

    total = a + b + c

    result = "TÀI 🔥" if total >= 11 else "XỈU ❄️"

    await ctx.send(
        f"🎲 {a} + {b} + {c} = **{total}**\n"
        f"👉 Kết quả: **{result}**"
    )


@bot.command()
async def rps(ctx, choice=None):

    choices = ["kéo", "búa", "bao"]

    if choice is None or choice.lower() not in choices:

        await ctx.send(
            "❌ Dùng:\n"
            "`!rps kéo`\n"
            "`!rps búa`\n"
            "`!rps bao`"
        )

        return

    bot_choice = random.choice(choices)
    choice = choice.lower()

    if choice == bot_choice:

        result = "🤝 Hòa!"

    elif (
        (choice == "kéo" and bot_choice == "bao")
        or
        (choice == "búa" and bot_choice == "kéo")
        or
        (choice == "bao" and bot_choice == "búa")
    ):

        result = "🎉 Bạn thắng!"

    else:

        result = "😂 Bot thắng!"

    await ctx.send(
        f"Bạn chọn: **{choice}**\n"
        f"Bot chọn: **{bot_choice}**\n"
        f"**{result}**"
    )


# =========================
# ĐOÁN SỐ
# =========================

@bot.command()
async def guess(ctx):

    number = random.randint(1, 10)

    ctx.bot.guess_number = number

    await ctx.send(
        f"🔢 {ctx.author.mention}, mình đã chọn một số "
        f"từ **1 đến 10**!\n"
        f"👉 Bạn đoán bằng `!guessnumber số`"
    )


@bot.command()
async def guessnumber(ctx, number: int = None):

    if not hasattr(ctx.bot, "guess_number"):

        await ctx.send(
            "❌ Hãy dùng `!guess` trước!"
        )

        return

    if number is None or number < 1 or number > 10:

        await ctx.send(
            "❌ Hãy nhập số từ 1 đến 10!"
        )

        return

    answer = ctx.bot.guess_number

    if number == answer:

        await ctx.send(
            "🎉 Chính xác! Bạn đoán đúng!"
        )

        del ctx.bot.guess_number

    else:

        await ctx.send(
            f"❌ Sai rồi! Số mình chọn là **{answer}**."
        )


@bot.command()
async def gamehelp(ctx):

    embed = discord.Embed(
        title="🎮 TRÒ CHƠI BOT 🎮",
        description="━━━━━━━━━━━━━━━━━━━━",
        color=discord.Color.gold()
    )

    embed.add_field(
        name="🪙 GAME MAY RỦI",
        value=(
            "`!coinflip` → Tung đồng xu\n"
            "`!dice` → Gieo xúc xắc\n"
            "`!taixiu` → Tài / Xỉu"
        ),
        inline=False
    )

    embed.add_field(
        name="✊ ĐỐI KHÁNG",
        value=(
            "`!rps kéo` → Kéo búa bao\n"
            "`!rps búa` → Kéo búa bao\n"
            "`!rps bao` → Kéo búa bao"
        ),
        inline=False
    )

    embed.add_field(
        name="🔢 ĐOÁN SỐ",
        value=(
            "`!guess` → Bắt đầu game\n"
            "`!guessnumber <số>` → Đoán số"
        ),
        inline=False
    )

    await ctx.send(embed=embed)


# =========================
# THỜI TIẾT
# =========================

@bot.command()
async def weather(ctx, *, location=None):

    if not location:

        await ctx.send(
            "❌ Hãy nhập địa điểm!\n"
            "Ví dụ: `!weather Bac Ninh`"
        )

        return

    geo_url = (
        "https://geocoding-api.open-meteo.com/v1/search"
    )

    geo_params = {
        "name": location,
        "count": 1,
        "language": "vi",
        "format": "json"
    }

    try:

        geo_response = requests.get(
            geo_url,
            params=geo_params,
            timeout=10
        )

        geo = geo_response.json()

    except Exception:

        await ctx.send(
            "❌ Không thể kết nối tới dịch vụ thời tiết."
        )

        return

    if "results" not in geo:

        await ctx.send(
            f"❌ Không tìm thấy địa điểm **{location}**."
        )

        return

    place = geo["results"][0]

    latitude = place["latitude"]
    longitude = place["longitude"]

    weather_url = (
        "https://api.open-meteo.com/v1/forecast"
    )

    weather_params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": (
            "temperature_2m,"
            "relative_humidity_2m,"
            "apparent_temperature,"
            "weather_code,"
            "wind_speed_10m"
        ),
        "timezone": "auto"
    }

    try:

        weather_response = requests.get(
            weather_url,
            params=weather_params,
            timeout=10
        )

        data = weather_response.json()
        current = data["current"]

    except Exception:

        await ctx.send(
            "❌ Không thể lấy dữ liệu thời tiết."
        )

        return

    weather_codes = {

        0: "☀️ Trời quang",
        1: "🌤️ Chủ yếu quang",
        2: "⛅ Có mây",
        3: "☁️ Nhiều mây",
        45: "🌫️ Sương mù",
        48: "🌫️ Sương mù",
        51: "🌦️ Mưa phùn",
        53: "🌦️ Mưa phùn",
        55: "🌧️ Mưa phùn",
        61: "🌧️ Mưa nhẹ",
        63: "🌧️ Mưa vừa",
        65: "🌧️ Mưa to",
        80: "🌦️ Mưa rào",
        81: "🌧️ Mưa rào",
        82: "⛈️ Mưa rào lớn",
        95: "⛈️ Dông",
        96: "⛈️ Dông có mưa đá",
        99: "⛈️ Dông có mưa đá"
    }

    code = current["weather_code"]

    condition = weather_codes.get(
        code,
        "🌥️ Không xác định"
    )

    embed = discord.Embed(
        title=f"🌍 Thời tiết: {place['name']}",
        color=discord.Color.blue()
    )

    embed.description = condition

    embed.add_field(
        name="🌡️ Nhiệt độ",
        value=f"{current['temperature_2m']}°C",
        inline=True
    )

    embed.add_field(
        name="🌡️ Cảm giác như",
        value=f"{current['apparent_temperature']}°C",
        inline=True
    )

    embed.add_field(
        name="💧 Độ ẩm",
        value=f"{current['relative_humidity_2m']}%",
        inline=True
    )

    embed.add_field(
        name="💨 Gió",
        value=f"{current['wind_speed_10m']} km/h",
        inline=True
    )

    await ctx.send(embed=embed)


# =========================
# FUN
# =========================

@bot.command()
async def buax(ctx):

    messages = [
        "🗿 Não đang cập nhật... vui lòng đợi 999 năm.",
        "💀 Bạn vừa được hệ thống xác nhận là hơi báo.",
        "🐧 Chim cánh cụt đã xem và không nói gì.",
        "📡 Đã quét IQ... tín hiệu yếu.",
        "🗿 Hệ thống: Không hiểu bạn đang làm gì.",
        "🚨 Cảnh báo: Độ bựa vượt quá giới hạn!"
    ]

    await ctx.send(random.choice(messages))


@bot.command()
async def iq(ctx):

    iq_value = random.randint(1, 200)

    await ctx.send(
        f"🧠 IQ của {ctx.author.mention}: "
        f"**{iq_value}**\n"
        f"🤡 Máy đo hơi nghi ngờ kết quả..."
    )


@bot.command()
async def xui(ctx):

    messages = [
        "🍀 Hôm nay bạn may mắn... trong game thôi.",
        "💀 Bạn nên ở nhà hôm nay.",
        "🗿 Vũ trụ bảo: tự lo đi.",
        "😂 Chúc mừng! Bạn vừa gặp xui.",
        "🚪 Có vẻ hôm nay không phải ngày của bạn."
    ]

    await ctx.send(random.choice(messages))


@bot.command()
async def phat(ctx, member: discord.Member = None):

    member = member or ctx.author

    amount = random.randint(1, 100)

    await ctx.send(
        f"🔨 {member.mention} bị phạt "
        f"**{amount}% độ bựa**!"
    )


@bot.command()
async def ai_bua(ctx):

    members = ctx.guild.members

    humans = [
        m for m in members
        if not m.bot
    ]

    if not humans:

        await ctx.send(
            "❌ Không tìm thấy người chơi."
        )

        return

    target = random.choice(humans)

    await ctx.send(
        f"🎯 Hệ thống đã chọn: {target.mention}\n"
        f"🤡 Hôm nay bạn là **trùm bựa**!"
    )


@bot.command()
async def xam(ctx):

    await ctx.send(
        "🗿 Bạn vừa sử dụng một lệnh cực kỳ xàm.\n"
        "📈 Độ xàm của bạn đã tăng +100."
    )


@bot.command()
async def batngo(ctx):

    events = [
        "💥 BÙM! Không có gì xảy ra.",
        "🗿 Bạn nhìn vào màn hình. Màn hình nhìn lại.",
        "🐟 Một con cá vừa đi ngang qua.",
        "🚨 FBI đã biết bạn dùng lệnh này.",
        "😂 Bot cũng không biết chuyện gì vừa xảy ra.",
        "👽 Người ngoài hành tinh đã đọc tin nhắn này."
    ]

    await ctx.send(random.choice(events))


@bot.command()
async def joke(ctx):

    jokes = [
        "😂 Tại sao máy tính bị cảm? Vì nó có quá nhiều virus!",
        "🤣 Lập trình viên đi ngủ lúc nào? Khi code chạy được!",
        "🐟 Cá gì không biết bơi? Cá... trong game!",
        "🗿 Tôi định kể một câu chuyện hay, nhưng não đang bảo trì.",
        "💀 Hôm nay tôi rất vui... cho đến khi nhìn thấy bài tập."
    ]

    await ctx.send(random.choice(jokes))


# =========================
# TƯƠNG TÁC
# =========================

@bot.command()
async def love(ctx, member: discord.Member = None):

    member = member or ctx.author

    percent = random.randint(0, 100)

    await ctx.send(
        f"❤️ Mức độ hợp nhau giữa "
        f"{ctx.author.mention} và {member.mention}: "
        f"**{percent}%**"
    )


@bot.command()
async def luck(ctx):

    percent = random.randint(0, 100)

    if percent >= 80:
        text = "🍀 Hôm nay bạn cực kỳ may mắn!"

    elif percent >= 50:
        text = "😎 Hôm nay khá ổn!"

    elif percent >= 20:
        text = "😅 Hơi xui một tí..."

    else:
        text = "💀 Hôm nay nên nằm im!"

    await ctx.send(
        f"🎰 Độ may mắn của {ctx.author.mention}: "
        f"**{percent}%**\n"
        f"{text}"
    )


@bot.command()
async def choose(ctx, *, options=None):

    if not options:

        await ctx.send(
            "❌ Nhập các lựa chọn, ví dụ:\n"
            "`!choose trà sữa | coca | nước lọc`"
        )

        return

    choices = [
        x.strip()
        for x in options.split("|")
        if x.strip()
    ]

    if len(choices) < 2:

        await ctx.send(
            "❌ Cần ít nhất 2 lựa chọn!"
        )

        return

    result = random.choice(choices)

    await ctx.send(
        "🎯 Sau khi suy nghĩ rất nghiêm túc...\n"
        f"👉 **Chọn: {result}**"
    )


@bot.command()
async def dare(ctx, member: discord.Member = None):

    member = member or ctx.author

    dares = [
        "😂 Gửi một emoji bất kỳ vào chat!",
        "🐸 Đổi nickname thành 'Ếch Xanh' trong 1 phút!",
        "🤣 Gõ 'Tôi là huyền thoại' 3 lần!",
        "🗿 Gửi một câu nói cực kỳ vô tri!",
        "🎤 Gửi một bài hát bạn thích!"
    ]

    await ctx.send(
        f"🎯 {member.mention} nhận thử thách:\n"
        f"**{random.choice(dares)}**"
    )


@bot.command()
async def roast(ctx, member: discord.Member = None):

    member = member or ctx.author

    roasts = [
        "🗿 Bạn rất đặc biệt... đặc biệt theo cách không ai hiểu.",
        "😂 Não bạn đang chạy chế độ tiết kiệm pin.",
        "💀 Wi-Fi còn mạnh hơn lập luận của bạn.",
        "🤣 Bạn không lười, bạn chỉ đang tối ưu năng lượng.",
        "🐧 Ngay cả chim cánh cụt cũng đang cố hiểu bạn."
    ]

    await ctx.send(
        f"🔥 {member.mention}: "
        f"{random.choice(roasts)}"
    )


@bot.command()
async def compliment(ctx, member: discord.Member = None):

    member = member or ctx.author

    compliments = [
        "✨ Hôm nay bạn trông rất tuyệt!",
        "😎 Bạn đúng là nhân vật chính!",
        "🔥 Năng lượng hôm nay quá đỉnh!",
        "🌟 Bạn làm server vui hơn đấy!",
        "❤️ Bạn là một thành viên tuyệt vời!"
    ]

    await ctx.send(
        f"{member.mention} "
        f"{random.choice(compliments)}"
    )


@bot.command()
async def hug(ctx, member: discord.Member = None):

    member = member or ctx.author

    await ctx.send(
        f"🤗 {ctx.author.mention} ôm "
        f"{member.mention} một cái thật to!"
    )


@bot.command()
async def dance(ctx):

    dances = [
        "💃🕺🕺💃",
        "🕺💃🕺💃",
        "💃💃🕺💃",
        "🕺🕺💃🕺"
    ]

    await ctx.send(
        f"🎵 {ctx.author.mention} đang nhảy!\n"
        f"{random.choice(dances)}"
    )


@bot.command()
async def mood(ctx):

    moods = [
        "😎 Hôm nay cực chill!",
        "😂 Đang vui không lý do!",
        "🥱 Hơi buồn ngủ...",
        "🤪 Độ điên: 100%",
        "🗿 Không cảm xúc.",
        "🔥 Năng lượng MAX!"
    ]

    await ctx.send(
        f"🎭 Tâm trạng của {ctx.author.mention}:\n"
        f"**{random.choice(moods)}**"
    )


# =========================
# RPG
# =========================

@bot.command()
async def die(ctx):

    await ctx.send(
        f"💀 {ctx.author.mention} đã bị "
        f"**RẮN CẮN**!\n"
        "☠️ Trạng thái: Đã chết trong game 😂"
    )


@bot.command()
async def kill(ctx, member: discord.Member = None):

    member = member or ctx.author

    events = [
        "💀 bị một con gà đuổi đến ngất!",
        "☠️ bị boss trong game hạ!",
        "💥 bước nhầm vào bẫy meme!",
        "🗿 bị tượng đá nhìn quá lâu!",
        "😂 chết vì cười quá nhiều!"
    ]

    await ctx.send(
        f"⚔️ {member.mention} "
        f"{random.choice(events)}"
    )


@bot.command()
async def revive(ctx, member: discord.Member = None):

    member = member or ctx.author

    await ctx.send(
        f"✨ {member.mention} đã được "
        f"**HỒI SINH**!\n"
        "❤️ HP: 100/100"
    )


@bot.command()
async def hp(ctx):

    hp_value = random.randint(1, 100)

    if hp_value <= 20:
        status = "💀 Sắp bay màu!"

    elif hp_value <= 50:
        status = "⚠️ Đang hấp hối!"

    else:
        status = "❤️ Vẫn còn khỏe!"

    await ctx.send(
        f"🩸 HP của {ctx.author.mention}: "
        f"**{hp_value}/100**\n"
        f"{status}"
    )


# =========================
# XỬ LÝ LỖI
# =========================

@bot.event
async def on_command_error(ctx, error):

    if isinstance(error, commands.MissingPermissions):

        await ctx.send(
            "❌ Bạn không có quyền sử dụng lệnh này!"
        )
        return

    if isinstance(error, commands.MissingRequiredArgument):

        await ctx.send(
            "❌ Bạn nhập thiếu thông tin cho lệnh!"
        )
        return

    if isinstance(error, commands.BadArgument):

        await ctx.send(
            "❌ Đối số không hợp lệ!"
        )
        return

    if isinstance(error, commands.CheckFailure):

        if (
            "channel_id" in config
            and ctx.channel.id != config["channel_id"]
            and ctx.command
            and ctx.command.name != "setchannel"
        ):

            channel = bot.get_channel(
                config["channel_id"]
            )

            if channel:
                await ctx.send(
                    f"❌ Chỉ được dùng lệnh bot tại {channel.mention}!"
                )
            else:
                await ctx.send(
                    "❌ Bạn đang dùng bot sai kênh!"
                )

        return

    print(f"Lỗi: {error}")
# =========================
# 🚀 CHẠY BOT
# =========================

bot.run("MTU0NTI3MzMwMzE1MTY3NzQ2Mg.GOF5tI.QbvEwDVhd9kDRYKyptfvLfh_tjBovxXpKy3dzk")
