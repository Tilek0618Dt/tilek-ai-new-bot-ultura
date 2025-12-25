def can_use(uid, users):
    if users[uid]["plan"] == "free":
        return users[uid]["count"] < 20
    return True

if not can_use(uid, users):
    bot.send_message(
        chat.id,
        "❌ FREE лимит бүттү.\n⭐ PLUS же 👑 PRO алыңыз."
    )
    return
