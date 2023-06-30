import telebot
from telebot import types
import requests
from datetime import datetime
from dateutil import parser

bot = telebot.TeleBot('5999258876:AAHAeSsLAbNZmVtwMj6kW8xdIxvIBcbM5FQ')
contact_support = 'https://t.me/kraeon'


@bot.message_handler(commands=['start'])
def handle_start(message):
    chat_id = message.chat.id
    welcome_message = "Welcome to the DHL Tracking Bot! How can I assist you today?"
    bot.send_message(chat_id, welcome_message, reply_markup=create_main_menu())

@bot.message_handler(func=lambda message: message.text == '✅ Track Package')
def handle_track(message):
    chat_id = message.chat.id
    msg = bot.reply_to(message, 'Please enter your DHL tracking number:')
    bot.register_next_step_handler(msg, process_tracking_number, chat_id)

@bot.message_handler(func=lambda message: message.text == '📞 Contact Support')
def handle_support(message):
    chat_id = message.chat.id
    support_message = f"<b>Need Help?</b>\n<b>Contact Creator:</b>\n\n{contact_support}"
    bot.send_message(chat_id, support_message, parse_mode='HTML')

def create_main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    track_button = types.KeyboardButton('✅ Track Package')
    support_button = types.KeyboardButton('📞 Contact Support')
    markup.add(track_button, support_button)
    return markup

def process_tracking_number(message, chat_id):
    tracking_number = message.text
    url = "https://api-eu.dhl.com/track/shipments"
    headers = {
        'Accept': 'application/json',
        'DHL-API-Key': 'fvnqAYgIza3E13Nq4I65efDJTtARcL0G'
    }
    params = {
        'trackingNumber': tracking_number
    }
    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            tracking_data = response.json()
            shipment = tracking_data['shipments'][0]
            track_num = shipment['id']
            service = shipment['service']
            delivery_location = shipment['status']['location']['address'].get('addressLocality')
            status = shipment['status']['status']
            description = shipment['status']['description']

            events = shipment.get('events', [])
            grouped_events = {}
            for event in events:
                event_time = parser.parse(event['timestamp'])
                event_date = event_time.date()
                event_location = event['location']['address']['addressLocality']
                event_description = event['description']
                event_message = f"⏰ {event_time.strftime('%I:%M %p')}\n📍 {event_location}\n📝 {event_description}"

                if event_date in grouped_events:
                    grouped_events[event_date].append(event_message)
                else:
                    grouped_events[event_date] = [event_message]

            event_messages = []
            for event_date, event_list in grouped_events.items():
                event_date_str = event_date.strftime("%A,\n%dth %B, %Y")
                events_str = "\n\n".join(reversed(event_list))
                event_box = f"```\n{events_str}\n```"
                event_messages.append(f"{'-' * 40}\n\n**{event_date_str}**\n\n{event_box}")

            event_messages.reverse()  # Reverse the order of event_messages

            # Create the tracking information string
            tracking_info = f"📦 Tracking Number: {track_num}\n" \
                            f"🚚 Service: {service}\n" \
                            f"🌍 Delivery Location: {delivery_location}\n" \
                            f"📣 Status: {status}\n" \
                            f"📝 Description: {description}"

            # Create the final message string with separate sections
            message = f"{chr(10).join(event_messages)}\n\n" \
                      f"👆🏼👆🏼👆🏼👆🏼👆🏼\n\n" \
                      f"TRACKING INFORMATION\n\n" \
                      f"{tracking_info}"

            # Create the inline button
            button_text = "View on Site"
            button_url = f"http://127.0.0.1:5000/tracking_number/{tracking_number}"
            inline_button = types.InlineKeyboardButton(button_text, url=button_url)

            # Create the inline keyboard markup
            inline_markup = types.InlineKeyboardMarkup()
            inline_markup.add(inline_button)

            # Send the message with the inline button
            bot.send_message(chat_id, message, parse_mode='Markdown', reply_markup=inline_markup)
        else:
            bot.send_message(chat_id, "Unable to track the package. Please check the tracking number.")
    except Exception as e:
        bot.send_message(chat_id, "An error occurred while tracking the package. Please try again later.")


bot.polling()
