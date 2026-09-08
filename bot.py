from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
import os
import json
import time
import asyncio
from collections import defaultdict, deque
from datetime import datetime, timedelta

import discord
from discord.ext import commands


# =========================
# INTENTS
# =========================

intents = discord.Intents.default()
intents.message_content = True
intents.members = True


bot = commands.Bot(
    command_prefix="!",
    intents=intents,
    help_command=None
)


# =========================
# FILE LƯU CẤU HÌNH
# =========================

ANTI_NUKE_FILE = "antinuke.json"


def load_antinu​​ke():
    try:
        with open(ANTI_NUKE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}


def save_antinuke(data):
    with open(ANTI_NUKE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


antinuke_data = load_antinu​​ke()


# =========================
# GIỚI HẠN ANTI-NUKE
# =========================

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


# =========================
# LẤY SETTINGS SERVER
# =========================

def get_settings(guild_id):
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


# =========================
# KIỂM TRA ADMIN
# =========================

def admin_only():
    async def predicate(ctx):
        if ctx.author.guild_permissions.administrator:
            return True

        await ctx.send(
            "❌ Chỉ **Admin** mới có thể sử dụng lệnh này."
        )
        return False

    return commands.check(predicate)


# =========================
# LOG ANTI-NUKE
# =========================

async def antinuke_log(guild, message):
    settings = get_settings(guild.id)

    channel_id = settings.get("log_channel")

    if not channel_id:
        return

    channel = guild.get_channel(channel_id)

    if not channel:
        return

    try:
        embed = discord.Embed(
            title="🛡️ ANTI-NUKE LOG",
            description=message,
            color=discord.Color.red(),
            timestamp=datetime.utcnow()
        )

        await channel.send(embed=embed)

    except Exception as e:
        print("Lỗi gửi Anti-Nuke log:", e)


# =========================
# PUNISH NUKER
# =========================

async def punish_nuker(guild, member, reason):
    if member is None:
        return

    if member == guild.owner:
        return

    if member.guild_permissions.administrator:
        return

    try:
        await member.ban(
            reason=f"Anti-Nuke: {reason}",
            delete_message_days=0
        )

        await antinuke_log(
            guild,
            f"🚨 Đã **BAN** {member.mention}\n"
            f"**Lý do:** {reason}"
        )

    except discord.Forbidden:
        await antinuke_log(
            guild,
            f"⚠️ Không thể ban {member.mention}. "
            f"Kiểm tra quyền **Ban Members**."
        )

    except Exception as e:
        print("Punish error:", e)


# =========================
# GHI NHẬN HÀNH ĐỘNG
# =========================

async def record_action(guild, member, action):
    if member is None:
        return

    settings = get_settings(guild.id)

    actions = settings.setdefault("actions", {})

    user_id = str(member.id)

    if user_id not in actions:
        actions[user_id] = {}

    now = time.time()

    if action not in actions[user_id]:
        actions[user_id][action] = []

    actions[user_id][action] = [
        t for t in actions[user_id][action]
        if now - t <= 10
    ]

    actions[user_id][action].append(now)

    save_antinuke(antinuke_data)

    limit = ANTI_NUKE_LIMITS.get(action, 999)

    if len(actions[user_id][action]) >= limit:
        await punish_nuker(
            guild,
            member,
            f"{action}: {len(actions[user_id][action])} lần trong 10 giây"
        )

        actions[user_id][action] = []
        save_antinuke(antinuke_data)


# =========================
# TÌM NGƯỜI THỰC HIỆN
# =========================

async def find_audit_actor(guild, action_type, target_id=None):
    try:
        async for entry in guild.audit_logs(
            limit=10,
            action=action_type
        ):
            if abs(
                datetime.now(datetime.utcnow().astimezone().tzinfo)
                - entry.created_at
            ).total_seconds() > 10:
                continue

            if target_id is not None:
                if getattr(entry.target, "id", None) != target_id:
                    continue

            return entry.user

    except Exception as e:
        print("Audit log error:", e)

    return None


# =========================
# ANTI-NUKE AUDIT LOG
# =========================

@bot.event
async def on_audit_log_entry_create(entry):
    guild = entry.guild

    settings = get_settings(guild.id)

    if not settings.get("antinuke"):
        return

    actor = entry.user

    if actor is None:
        return

    if actor.id == guild.owner_id:
        return

    if actor.guild_permissions.administrator:
        return

    action = entry.action

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

    action_name = action_map.get(action)

    if not action_name:
        return

    await record_action(
        guild,
        actor,
        action_name
    )


# =========================
# ANTI-RAID
# =========================

raid_joins = defaultdict(deque)


@bot.event
async def on_member_join(member):
    guild = member.guild

    settings = get_settings(guild.id)

    if not settings.get("antiraid"):
        return

    now = time.time()

    joins = raid_joins[guild.id]

    joins.append(now)

    while joins and now - joins[0] > 10:
        joins.popleft()

    # 8 người vào trong 10 giây
    if len(joins) >= 8:

        try:
            await member.timeout(
                timedelta(minutes=10),
                reason="Anti-Raid"
            )

            await antinuke_log(
                guild,
                f"🚨 Phát hiện **RAID**!\n"
                f"👤 Thành viên: {member.mention}\n"
                f"📊 {len(joins)} người tham gia trong 10 giây\n"
                f"🔒 Đã timeout 10 phút."
            )

        except discord.Forbidden:
            await antinuke_log(
                guild,
                "⚠️ Anti-Raid phát hiện raid nhưng bot "
                "không có quyền **Moderate Members**."
            )

        except Exception as e:
            print("Anti-Raid error:", e)


# =========================
# !ANTINUKE
# =========================

@bot.command()
@admin_only()
async def antinuke(ctx, mode=None):

    settings = get_settings(ctx.guild.id)

    if mode is None:
        await ctx.send(
            "🛡️ **Anti-Nuke**\n\n"
            "`!antinuke on` - Bật\n"
            "`!antinuke off` - Tắt\n"
            "`!antinuke status` - Kiểm tra"
        )
        return

    mode = mode.lower()

    if mode == "on":

        settings["antinuke"] = True
        save_antinuke(antinuke_data)

        await ctx.send(
            "🛡️ **ANTI-NUKE ĐÃ BẬT!**\n\n"
            "Bot sẽ theo dõi các hành động phá server."
        )

    elif mode == "off":

        settings["antinuke"] = False
        save_antinuke(antinuke_data)

        await ctx.send(
            "🔓 **Anti-Nuke đã tắt.**"
        )

    elif mode == "status":

        status = "🟢 BẬT" if settings.get("antinuke") else "🔴 TẮT"

        await ctx.send(
            f"🛡️ **Anti-Nuke:** {status}"
        )

    else:
        await ctx.send(
            "❌ Dùng:\n"
            "`!antinuke on`\n"
            "`!antinuke off`\n"
            "`!antinuke status`"
        )


# =========================
# !ANTIRAID
# =========================

@bot.command()
@admin_only()
async def antiraid(ctx, mode=None):

    settings = get_settings(ctx.guild.id)

    if mode is None:
        await ctx.send(
            "🚨 **Anti-Raid**\n\n"
            "`!antiraid on`\n"
            "`!antiraid off`"
        )
        return

    mode = mode.lower()

    if mode == "on":

        settings["antiraid"] = True
        save_antinuke(antinuke_data)

        await ctx.send(
            "🚨 **ANTI-RAID ĐÃ BẬT!**\n\n"
            "Phát hiện nhiều người vào server liên tục."
        )

    elif mode == "off":

        settings["antiraid"] = False
        save_antinuke(antinuke_data)

        await ctx.send(
            "🔓 **Anti-Raid đã tắt.**"
        )

    else:
        await ctx.send(
            "`!antiraid on` hoặc `!antiraid off`"
        )


# =========================
# !ANTIHIGH
# =========================

@bot.command()
@admin_only()
async def antihigh(ctx):

    settings = get_settings(ctx.guild.id)

    settings["antinuke"] = True
    settings["antiraid"] = True

    save_antinuke(antinuke_data)

    await ctx.send(
        "🔐 **ANTI SERVER CAO ĐÃ BẬT!**\n\n"
        "🛡️ Anti-Nuke: 🟢\n"
        "🚨 Anti-Raid: 🟢\n\n"
        "Server đang được bảo vệ."
    )


# =========================
# !ANTILOG
# =========================

@bot.command()
@admin_only()
async def antilog(ctx):

    settings = get_settings(ctx.guild.id)

    settings["log_channel"] = ctx.channel.id

    save_antinuke(antinuke_data)

    await ctx.send(
        f"📋 Đã đặt {ctx.channel.mention} "
        "làm kênh Anti-Nuke Log."
    )


# =========================
# READY
# =========================

@bot.event
async def on_ready():

    print(
        f"✅ Bot đã đăng nhập: "
        f"{bot.user} | ID: {bot.user.id}"
    )

    print(
        f"🛡️ Anti-Nuke System: READY"
    )

    print(
        f"🚨 Anti-Raid System: READY"
    )


# =========================
# CHẠY BOT
# =========================

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is online!")

    def log_message(self, format, *args):
        pass


def start_server():
    port = int(os.getenv("PORT", "10000"))

    server = HTTPServer(
        ("0.0.0.0", port),
        HealthHandler
    )

    print(f"Web server running on port {port}")
    server.serve_forever()


if os.getenv("PORT"):
    threading.Thread(
        target=start_server,
        daemon=True
    ).start()


token = os.getenv("DISCORD_TOKEN")

if not token:
    raise RuntimeError(
        "❌ Thiếu biến môi trường DISCORD_TOKEN"
    )

bot.run(token)
```

