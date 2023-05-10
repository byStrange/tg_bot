# Import necessary modules
import sqlite3
from telegram import Update, ForceReply, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, MessageHandler, Filters, ConversationHandler, CommandHandler,  CallbackQueryHandler, CallbackContext
from config import API_TOKEN

# Define states of the conversation
OPTION, FACULTY, GROUP, SUMMARY = range(1, 5)

# Define function to start the bot
facilities = [
    "1-TTJ ",
    "2-TTJ",
    "3-TTJ"
]

button_enter_text = "Talabalarni TTJ ga kiritish"
button_list_text = 'TTJ lar bo\'yicha ma\'lumot'


def start_bot(update: Update, context: CallbackContext):
    print("run start_bot")

    # Define the two buttons
    button_enter = KeyboardButton(text=button_enter_text)
    button_list = KeyboardButton(text=button_list_text)

    # Create the keyboard markup with the buttons
    keyboard = ReplyKeyboardMarkup(
        [[button_enter], [button_list]], resize_keyboard=True)

    # Send a message with the keyboard markup
    if update.message:
        update.message.reply_text(
            'Menyuni tanlang',  reply_markup=keyboard)
    else:
        update.callback_query.message.reply_text(
            'Bosh menu', reply_markup=keyboard)


def start(update: Update, context: CallbackContext) -> int:
    print("run start")
    # Define the keyboard layout
    keyboard = [
        [
            InlineKeyboardButton(facilities[0], callback_data='1'),
            InlineKeyboardButton(facilities[1], callback_data='2'),
            InlineKeyboardButton(facilities[2], callback_data='3'),
        ],
        [InlineKeyboardButton("Bosh menyuga qaytish", callback_data='back')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    # Set the reply markup with the above layout

    # Send the message and ask the user to choose an option
    message = "TTJ ni tanlang:"
    a = update.message.reply_text('.', reply_markup=ReplyKeyboardRemove())
    context.bot.delete_message(
        chat_id=update.message.chat_id, message_id=a.message_id)
    update.message.reply_text(message, reply_markup=reply_markup)

    # Set the next state to get the user's chosen option

# Define function to handle user's chosen option


def get_option(update: Update, context: CallbackContext) -> int:
    # Get the user's chosen option
    query = update.callback_query
    query.answer()
    option = query.data
    # Check if the user chose to not do anything
    if option == 'back':
        cancel(update, context)
        return ConversationHandler.END

    if option in ("fc1", "fc2", "fc3"):
        get_stats(update, context, option)
        return ConversationHandler.END
    # Ask the user for their full name
    message = "Talabaning ismi va familiyasini kiriting"
    query.answer()
    query.message.reply_text(
        text=message, reply_markup=ForceReply(selective=True))

    # Set the next state to get the user's faculty name
    context.user_data['option'] = option
    return OPTION

# Define function to handle user's full name


def get_fullname(update: Update, context: CallbackContext) -> int:
    # Get the user's full name
    fullname = update.message.text

    # Ask the user for their faculty name
    message = "Fakultet nomini kiriting"
    update.message.reply_text(message, reply_markup=ForceReply(selective=True))

    # Set the next state to get the user's group name
    context.user_data['fullname'] = fullname
    return FACULTY


# Define function to handle user's faculty name
def get_faculty(update: Update, context: CallbackContext) -> int:
    # Get the user's faculty name
    faculty = update.message.text

    # Ask the user for their group name
    message = "Kursi va guruhi nomini kiriting"
    update.message.reply_text(message, reply_markup=ForceReply(selective=True))

    # Set the next state to get the user's group name
    context.user_data['faculty'] = faculty
    return GROUP

# Define function to handle user's group name


def get_group(update: Update, context: CallbackContext) -> int:
    # Get the user's group name
    group = update.message.text
    data = context.user_data
    # Get the user's full name, faculty name, and group name
    message = f"""Siz quyidagi ma'lumotlar bilan talabani  {facilities[int(data['option']) - 1]}ga qo'shmoqchisiz:
Ismi va familiyasi: {data['fullname']}
Fakultet nomi: {data['faculty']}
Kursi va guruh nomi: {group}
TTJ: {facilities[int(data['option']) - 1]}
    """
    keyboard = [
        [InlineKeyboardButton("Tasdiqlash", callback_data='4'),
         InlineKeyboardButton("Bekor qilish", callback_data='5')]
    ]
    markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(message, reply_markup=markup)

    context.user_data['group'] = group
    # End the conversation
    return SUMMARY

    # Define function to summarize user input and write to database


def summarize(update: Update, context: CallbackContext) -> int:
    print('summarize function ran')
    # Get the user's chat ID and data from conversation context

    query = update.callback_query
    query.answer()
    chat_id = query.message.chat_id
    data = context.user_data
    # Retrieve the user's input from context data
    if query.data == "4":
        message = f"""Tasdiqlandi ✅"""
        query.edit_message_text(text=message)

        fullname = data.get("fullname")
        faculty = data.get("faculty")
        group = data.get("group")
        option = data.get('option')
        # Connect to SQLite database and insert user input
        con = sqlite3.connect("users.db")
        cursor = con.cursor()
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS first_group_users (id INTEGER PRIMARY KEY, full_name TEXT, faculty TEXT, group_name TEXT)")
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS second_group_users (id INTEGER PRIMARY KEY, full_name TEXT, faculty TEXT, group_name TEXT)")
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS third_group_users (id INTEGER PRIMARY KEY, full_name TEXT, faculty TEXT, group_name TEXT)")
        con.commit()

        if int(option) == 1:
            cursor.execute(
                f"INSERT INTO first_group_users (full_name, faculty, group_name) VALUES (?, ?, ?)", (fullname, faculty, group))
        elif int(option) == 2:
            cursor.execute(
                f"INSERT INTO second_group_users (full_name, faculty, group_name) VALUES (?, ?, ?)", (fullname, faculty, group))
        elif int(option) == 3:
            cursor.execute(
                f"INSERT INTO third_group_users (full_name, faculty, group_name) VALUES (?, ?, ?)", (fullname, faculty, group))
        con.commit()
        con.close()
        # Send a message to the user confirming the data was saved
        message = f"Talaba TTJ ga joylandi ✅"
        context.bot.send_message(chat_id=chat_id, text=message)
    elif query.data == "5":
        start_bot(update, context)
        query.edit_message_text(text="Amal bekor qilindi")

    data.clear()
    # End the conversation
    return ConversationHandler.END


# Define function to handle cancelling the conversation
def cancel(update: Update, context: CallbackContext) -> int:

    # Get the user's chat ID and message ID
    query = update.callback_query
    query.answer()

    chat_id = query.message.chat_id
    message_id = query.message.message_id
    context.bot.delete_message(chat_id=chat_id, message_id=message_id)
    start_bot(update, context)
    # Delete the message that triggered the conversation

    # End the conversation
    return ConversationHandler.END


def stats(update: Update,  context: CallbackContext) -> None:
    keyboard = [
        [
            InlineKeyboardButton(facilities[0], callback_data='fc1'),
            InlineKeyboardButton(facilities[1], callback_data='fc2'),
            InlineKeyboardButton(facilities[2], callback_data='fc3'),
        ],
        [InlineKeyboardButton("Bosh menyuga qaytish", callback_data='back')],
    ]

    # Set the reply markup with the above layout
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Send the message and ask the user to choose an option
    message = "TTJ ni tanlang:"
    a = update.message.reply_text('.', reply_markup=ReplyKeyboardRemove())
    context.bot.delete_message(
        chat_id=update.message.chat_id, message_id=a.message_id)
    update.message.reply_text(message, reply_markup=reply_markup)


class User:
    def __init__(self, id, full_name, faculty, group_name):
        self.id = id
        self.full_name = full_name
        self.faculty = faculty
        self.group_name = group_name


def get_stats(update: Update, context: CallbackContext, option: str) -> None:
    con = sqlite3.connect("users.db")
    cursor = con.cursor()
    databases = ['first', 'second', 'third']
    a = []
    for i in databases:
        cursor.execute(f"SELECT * FROM {i}_group_users")
        rows = cursor.fetchall()
        a.append([User(*row) for row in rows])

    message = ""
    if option == "fc1":
        message += facilities[0] + "+\n"
        for i in a[0]:
            message += f"{i.id}. {i.full_name} - {i.faculty} - {i.group_name}\n"
    elif option == 'fc2':
        message += facilities[1] + "+\n"
        for i in a[1]:
            message += f"{i.id}. {i.full_name} - {i.faculty} - {i.group_name}\n"

    elif option == 'fc3':
        message += facilities[2] + "+\n"
        for i in a[2]:
            message += f"{i.id}. {i.full_name} - {i.faculty} - {i.group_name}\n"
    context.bot.send_message(
        chat_id=update.callback_query.message.chat_id, text=message)


def main() -> None:
    updater = Updater(token=API_TOKEN)
    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(get_option)],
        states={
            OPTION: [MessageHandler(Filters.text & ~Filters.command, get_fullname)],
            FACULTY: [MessageHandler(Filters.text & ~Filters.command, get_faculty)],
            GROUP: [MessageHandler(Filters.text & ~Filters.command, get_group)],
            SUMMARY: [CallbackQueryHandler(summarize)],
        },
        fallbacks=[CallbackQueryHandler(cancel)]
    )
    enter_student_handler = MessageHandler(Filters.regex(
        f'^{button_enter_text}$'), start)
    get_stats_handler = MessageHandler(
        Filters.regex(f'^{button_list_text}$'), stats)

    dispatcher.add_handler(conv_handler)
    dispatcher.add_handler(CallbackQueryHandler(get_stats))
    dispatcher.add_handler(CommandHandler('start', start_bot))
    dispatcher.add_handler(CommandHandler("stats", stats))
    dispatcher.add_handler(CommandHandler("add", start))
    dispatcher.add_handler(get_stats_handler)
    dispatcher.add_handler(enter_student_handler)
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
