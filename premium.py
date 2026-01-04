from telebot import types

premium_users = {}  # user_id: plan

def is_premium(user_id):
    return user_id in premium_users

def register_handlers(bot):

    @bot.callback_query_handler(func=lambda call: call.data in ["plan_plus", "plan_pro"])
    def pay(call):
        if call.data == "plan_plus":
            title = "Tilek AI PLUS"
            price = 800  # демо баа центке эмес, долларда
            payload = "plus"
        else:
            title = "Tilek AI PRO"
            price = 1800
            payload = "pro"

        from telebot.types import LabeledPrice
        prices = [LabeledPrice(label=title, amount=price)]

        PROVIDER_TOKEN = "<СЕНИН_PROVIDER_TOKEN>"

        # Демонстрация үчүн азыр жөн гана кабар беребиз
        bot.send_message(
            call.message.chat.id,
            f"💳 {title} планы демо режимде активдешти!\nБажарылган баа: ${price/100:.2f}"
        )

