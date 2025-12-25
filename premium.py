from telebot.types import LabeledPrice

PROVIDER_TOKEN = "СЕН_STRIPE_PROVIDER_TOKEN"

@bot.callback_query_handler(func=lambda call: call.data in ["buy_plus", "buy_pro"])
def pay(call):

    if call.data == "buy_plus":
        title = "Tilek AI PLUS"
        price = 800 * 100  # 8.00
        payload = "plus"
    else:
        title = "Tilek AI PRO"
        price = 1800 * 100  #18.00
        payload = "pro"

    prices = [LabeledPrice(label=title, amount=price)]

    bot.send_invoice(
        chat_id=call.message.chat.id,
        title=title,
        description="AI Premium мүмкүнчүлүктөрү",
        payload=payload,
        provider_token=PROVIDER_TOKEN,
        currency="USD",
        prices=prices,
        start_parameter="premium"
    ) 

@bot.message_handler(content_types=['successful_payment'])
def successful_payment(message):
    payload = message.successful_payment.invoice_payload

    users = load_users()
    uid = str(message.from_user.id)

    users[uid]["plan"] = payload
    save_users(users)

    bot.send_message(
        message.chat.id,
        f"🎉 Төлөм ийгиликтүү!\nСиз {payload.upper()} актив кылдыңыз."
    )


