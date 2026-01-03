from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.types import ChatMemberStatus, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import ChatMemberAdministrator, ChatMemberOwner, ChatPermissions, Message
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from decimal import Decimal
from datetime import datetime, timedelta
from dateutil import parser
import numpy as np
import asyncio
import random
import sqlite3
import locale
import calendar
import config

scheduler =AsyncIOScheduler(timezone="Asia/Almaty")

bot = Bot(token=config.TOKEN)
dp = Dispatcher(bot)

game_time=dict()


MONTHS_RU = {
    'January': 'Января',
    'February': 'Февраля',
    'March': 'Марта',
    'April': 'Апреля',
    'May': 'Мая',
    'June': 'Июня',
    'July': 'Июля',
    'August': 'Августа',
    'September': 'Сентября',
    'October': 'Октября',
    'November': 'Ноября',
    'December': 'Декабря'
}


connect = sqlite3.connect("data.db")
cursor = connect.cursor()

cursor.execute("""CREATE TABLE IF NOT EXISTS users(
    user_id NUMERIC NOT NULL ,
    user_name TEXT,
    tag text NOT NULL ,
    slito INT,
    vero INT,
    serch NUMERIC ,
    status INT,
    pruf TEXT,
    pritc TEXT,
    balance INT,
    admin_balance INT
)
""")
cursor.execute("""CREATE TABLE IF NOT EXISTS prover(
    id INT,
    user_id INT,
    ids NUMERIC NOT NULL ,
    url TEXT,
    proc INT,
    prich TEXT
)
""")

def unmute_kb(user_id: int):
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(InlineKeyboardButton(text='🔗 Размутить', callback_data=f'unmute_{user_id}'))
    return kb


def unban_kb(user_id: int):
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(InlineKeyboardButton(text='🔗 Разбанить', callback_data=f'unban_{user_id}'))
    return kb

# Обработчик команды /чат +
@dp.message_handler(commands=['чат'], commands_prefix="+")
async def toggle_chat_on(message: types.Message):
    if message.chat.type != 'private':
        chat_id = message.chat.id
        user_id = message.from_user.id
    
        # Получаем информацию о пользователе
        user_info = await bot.get_chat_member(chat_id, user_id)
    
        # Проверяем, является ли пользователь администратором или создателем чата
        if user_info.status in ['administrator', 'creator'] and not user_info.user.is_bot:
            # Получаем текущие разрешения чата
            current_permissions = await bot.get_chat(chat_id)
    
            # Если чат открыт для всех, выводим сообщение об этом
            if current_permissions.permissions.can_send_messages:
                await message.reply("Чат уже открыт для всех.")
            # Если чат закрыт, открываем его
            else:
                permissions = types.ChatPermissions(can_send_messages=True)
                await bot.set_chat_permissions(chat_id, permissions)
                await message.reply("Теперь всем разрешено писать в чат.")
        else:
            await message.reply("Вы не можете изменять разрешения чата, так как не являетесь администратором чата.")
    else:
        pass

# Обработчик команды /чат -
@dp.message_handler(commands=['чат'],commands_prefix="-")
async def toggle_chat_off(message: types.Message):
    if message.chat.type != 'private':
        chat_id = message.chat.id
        user_id = message.from_user.id
    
        # Получаем информацию о пользователе
        user_info = await bot.get_chat_member(chat_id, user_id)
    
        # Проверяем, является ли пользователь администратором или создателем чата
        if user_info.status in ['administrator', 'creator'] and not user_info.user.is_bot:
            # Получаем текущие разрешения чата
            current_permissions = await bot.get_chat(chat_id)
    
            # Если чат открыт для всех, закрываем его
            if current_permissions.permissions.can_send_messages:
                permissions = types.ChatPermissions(can_send_messages=False)
                await bot.set_chat_permissions(chat_id, permissions)
                await message.reply("Теперь всем запрещено писать в чат.")
            # Если чат уже закрыт, выводим сообщение об этом
            else:
                await message.reply("Чат уже закрыт для всех.")
        else:
            await message.reply("Вы не можете изменять разрешения чата, так как не являетесь администратором чата.")
    else:
        pass

@dp.message_handler(commands=['поинт'], commands_prefix='+')
async def mute_handler(message):

    user_id = message.from_user.id
    status = cursor.execute("SELECT status FROM users WHERE user_id = ?",(user_id,)).fetchone()[0]
    if message.from_user.id in config.owner_id or message.from_user.id in config.prava:
        if message.reply_to_message:
            try:
                ids = int(message.text.split()[1])
            except:
                await message.reply("неправильный ввод команды -поинт число")
                return
            user_isd = message.reply_to_message.from_user.id
            cursor.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?",(ids,user_isd,))
            connect.commit()
            await message.reply("Вы успешно выдали поинт пользователю")
        else:
            await message.reply("Команда должна ответом на сообщения")

@dp.message_handler(commands=['поинт'], commands_prefix='-')
async def mute_handler(message):

    user_id = message.from_user.id
    status = cursor.execute("SELECT status FROM users WHERE user_id = ?",(user_id,)).fetchone()[0]
    if message.from_user.id in config.owner_id or message.from_user.id in config.prava:
        if message.reply_to_message:
            try:
                ids = int(message.text.split()[1])
            except:
                await message.reply("неправильный ввод команды -поинт число")
                return
            user_isd = message.reply_to_message.from_user.id
            cursor.execute("UPDATE users SET balance = balance - ? WHERE user_id = ?",(ids,user_isd,))
            connect.commit()
            await message.reply("Вы успешно забрали поинт у пользователя")
        else:
            await message.reply("Команда должна ответом на сообщения")

@dp.message_handler(commands=['реп'], commands_prefix='+')
async def mute_handler(message):

    user_id = message.from_user.id
    status = cursor.execute("SELECT status FROM users WHERE user_id = ?",(user_id,)).fetchone()[0]
    if status == 5 or status == 3 or status == 7 or status == 6:
        if message.reply_to_message:
            user_isd = message.reply_to_message.from_user.id
            cursor.execute("UPDATE users SET slito = slito + 1 WHERE user_id = ?",(user_isd,))
            connect.commit()
            await message.reply("Вы успешно выдали репутацию пользователю")
        else:
            await message.reply("Команда должна ответом на сообщения")

@dp.message_handler(commands=['реп'], commands_prefix='-')
async def mute_handler(message):

    user_id = message.from_user.id
    status = cursor.execute("SELECT status FROM users WHERE user_id = ?",(user_id,)).fetchone()[0]
    if status == 5 or status == 3 or status == 7 or status == 6:
        if message.reply_to_message:
            user_isd = message.reply_to_message.from_user.id
            cursor.execute("UPDATE users SET slito = slito - 1 WHERE user_id = ?",(user_isd,))
            connect.commit()
            await message.reply("Вы успешно забрали репутацию у пользователя")
        else:
            await message.reply("Команда должна ответом на сообщения")

@dp.message_handler(commands=['garant'])
async def garant_command(message: types.Message):
    # Получаем список пользователей с статусом 4 (администраторов)
    cursor.execute("SELECT tag FROM users WHERE status = 4")
    admins = cursor.fetchall()
    
    # Отправляем список админов
    if admins:
        admin_list = "\n@".join(str(admin[0]) for admin in admins)
        await message.reply(f"Список админов:\n@{admin_list}", parse_mode="html")
    else:
        await message.reply("Администраторы не найдены.")

@dp.message_handler(commands=['garants'], commands_prefix='/')
async def mute_handler(message):

    user_id = message.from_user.id
    status = cursor.execute("SELECT status FROM users WHERE user_id = ?",(user_id,)).fetchone()[0]
    if message.from_user.id in config.owner_id or message.from_user.id in config.prava or status == 4:
        try:
            ids = message.reply_to_message.from_user.id
        except:
            return
        cursor.execute("UPDATE users SET status = 1 WHERE user_id = ?",(ids,))
        connect.commit()
        await message.reply("Вы успешно выдали Проверено гарантом")

@dp.message_handler(commands=['nocheck'], commands_prefix='/')
async def mute_handler(message):
    user_id = message.from_user.id
    if user_id in config.owner_id:
        try:
            ids = message.text.split()[1]
        except:
            await message.reply('Используйте: <code>/noscam айди</code>',parse_mode='html')
            return
        cursor.execute("UPDATE users SET serch = 0 WHERE user_id = ?",(ids,))
        connect.commit()
        await message.reply("Вы обнулили поиски пользователю")

@dp.message_handler(commands=['noscam'], commands_prefix='/')
async def mute_handler(message):
    user_id = message.from_user.id
    status = cursor.execute("SELECT status FROM users WHERE user_id = ?",(user_id,)).fetchone()[0]
    if status == 5 or status == 6 or status == 7:
        try:
            ids = message.text.split()[1]
        except:
            await message.reply('Используйте: <code>/noscam айди</code>',parse_mode='html')
            return
        try:
            stats = cursor.execute("SELECT status FROM users WHERE user_id = ?",(ids,)).fetchone()[0]
        except:
            await message.reply("Ошибка")
        if stats == 2:
            try:
                cursor.execute("UPDATE users SET status = 0 WHERE user_id = ?",(ids,))
                cursor.execute("UPDATE users SET vero = 35 WHERE user_id = ?",(ids,))
                connect.commit()
                await message.reply("Вы успешно обнулили статус скамера")
            except:
                await message.reply("Ошибка")
        else:
            await message.reply("У пользователя нету статуса скамера")

@dp.message_handler(commands=['scamadd'], commands_prefix='/')
async def mute_handler(message):

    user_id = message.from_user.id
    status = cursor.execute("SELECT status FROM users WHERE user_id = ?",(user_id,)).fetchone()[0]
    if status == 5 or status == 7 or status == 6:
        try:
            ids = message.text.split()[1]
            url = message.text.split()[2]
            proc = message.text.split()[3]
            tag = message.text.split()[4]
            words = message.text.split()
            prich = ' '.join(words[5:])
        except:
            await message.reply('Используйте: <code>/scamadd айди ссылка процент тег причина</code>',parse_mode='html')
            return
        us = cursor.execute("SELECT user_name FROM users WHERE user_id = ?",(ids,)).fetchone()
        if us is None:
            cursor.execute("UPDATE users SET admin_balance = admin_balance + 1 WHERE user_id = ?",(message.from_user.id,))
            cursor.execute("INSERT INTO users VALUES(?,?,?,?,?,?,?,?,?,?,?)",(ids,"Неизвестно",tag,0,proc,0,2,url,prich,0,0))
            connect.commit()
            await message.reply("Вы успешно выдали статус скамера с доказательствами\nВам даётся +1 значение")
        else:
            await message.reply("Пользователя уже есть в базе данных используйте /scam")
    elif status == 3:
        try:
            ids = message.text.split()[1]
            url = message.text.split()[2]
            proc = message.text.split()[3]
            tag = message.text.split()[4]
            words = message.text.split()
            prich = ' '.join(words[5:])
        except:
            await message.reply('Используйте: <code>/scamadd айди ссылка процент тег причина</code>',parse_mode='html')
            return
        await message.reply("Ваша заявка будет принята,для этого отправьте её своему куратору")
        

@dp.message_handler(commands=['scam'], commands_prefix='/')
async def mute_handler(message):

    user_id = message.from_user.id
    status = cursor.execute("SELECT status FROM users WHERE user_id = ?",(user_id,)).fetchone()[0]
    if status == 5 or status == 7 or status == 6:
        try:
            ids = message.text.split()[1]
            url = message.text.split()[2]
            proc = message.text.split()[3]
            words = message.text.split()
            prich = ' '.join(words[4:])
        except:
            await message.reply('Используйте: <code>/scam айди ссылка процент причина</code>',parse_mode='html')
            return
        us = cursor.execute("SELECT user_name FROM users WHERE user_id = ?",(ids,)).fetchone()
        if us is None:
            await message.reply("Пользователя нет в базе данных")
        else:
            cursor.execute("UPDATE users SET admin_balance = admin_balance + 1 WHERE user_id = ?",(message.from_user.id,))
            cursor.execute("UPDATE users SET status = 2 WHERE user_id = ?",(ids,))
            cursor.execute("UPDATE users SET pruf = ? WHERE user_id = ?",(url,ids,))
            cursor.execute("UPDATE users SET pritc = ? WHERE user_id = ?",(prich,ids,))
            cursor.execute("UPDATE users SET vero = ? WHERE user_id = ?",(proc,ids,))
            connect.commit()
            await message.reply("Вы успешно выдали статус скамера с доказательствами\nВам даётся +1 значение")
    elif status == 3:
        try:
            ids = message.text.split()[1]
            url = message.text.split()[2]
            proc = message.text.split()[3]
            words = message.text.split()
            prich = ' '.join(words[4:])
        except:
            await message.reply('Используйте: <code>/scam айди ссылка процент причина</code>',parse_mode='html')
            return
        cursor.execute('INSERT INTO prover (user_id, ids,url,proc,prich) VALUES (?,?,?,?,?)',(message.from_user.id,ids,url,proc,prich))
        connect.commit()
        numm = cursor.execute("SELECT id FROM prover WHERE user_id = ? AND prich = ?",(message.from_user.id,prich)).fetchone()[0]
        help_menu = types.InlineKeyboardMarkup(row_width=2)
        yes = types.InlineKeyboardButton(text=f"Принять✅",callback_data=f"yes_{numm}")
        no = types.InlineKeyboardButton(text=f"Отклонить❌",callback_data=f"no_{numm}")
        help_menu.add(yes,no)
        await message.reply("Ваша заявка будет принята,для этого отправьте её своему куратору",reply_markup=help_menu)

@dp.message_handler(commands=['noadmin'], commands_prefix='/')
async def mute_handler(message):
    if message.from_user.id in config.owner_id or message.from_user.id in config.prava:
        print(2)
        try:
            user = message.reply_to_message.from_user.id
        except:
            await message.reply("Команда должна быть ответом на сообщение")
            return
        cursor.execute("UPDATE users SET status = 0 WHERE user_id = ?",(user,))
        connect.commit()
        await message.reply("Вы успешно забрали Администратора у пользователя")

@dp.message_handler(commands=['стажёр'], commands_prefix='+')
async def mute_handler(message):
    print(1)
    if message.from_user.id in config.owner_id or message.from_user.id in config.prava:
        print(2)
        try:
            user = message.reply_to_message.from_user.id
        except:
            await message.reply("Команда должна быть ответом на сообщение")
            return
        cursor.execute("UPDATE users SET status = 3 WHERE user_id = ?",(user,))
        connect.commit()
        await message.reply("Вы успешно выдали Стажёра пользователю")

@dp.message_handler(commands=['стажёр'], commands_prefix='-')
async def mute_handler(message):
    print(1)
    if message.from_user.id in config.owner_id or message.from_user.id in config.prava:
        print(2)
        try:
            user = message.reply_to_message.from_user.id
        except:
            await message.reply("Команда должна быть ответом на сообщение")
            return
        cursor.execute("UPDATE users SET status = 0 WHERE user_id = ?",(user,))
        connect.commit()
        await message.reply("Вы успешно забрали Стажёра у пользователя")

@dp.message_handler(commands=['президент'], commands_prefix='+')
async def mute_handler(message):
    print(1)
    if message.from_user.id in config.owner_id or message.from_user.id in config.prava:
        print(2)
        try:
            user = message.reply_to_message.from_user.id
        except:
            await message.reply("Команда должна быть ответом на сообщение")
            return
        cursor.execute("UPDATE users SET status = 6 WHERE user_id = ?",(user,))
        connect.commit()
        await message.reply("Вы успешно выдали Президента пользователю")

@dp.message_handler(commands=['президент'], commands_prefix='-')
async def mute_handler(message):
    print(1)
    if message.from_user.id in config.owner_id or message.from_user.id in config.prava:
        print(2)
        try:
            user = message.reply_to_message.from_user.id
        except:
            await message.reply("Команда должна быть ответом на сообщение")
            return
        cursor.execute("UPDATE users SET status = 0 WHERE user_id = ?",(user,))
        connect.commit()
        await message.reply("Вы успешно забрали Президента у пользователя")

@dp.message_handler(commands=['гарант'], commands_prefix='+')
async def mute_handler(message):
    print(1)
    if message.from_user.id in config.owner_id or message.from_user.id in config.prava:
        print(2)
        try:
            user = message.reply_to_message.from_user.id
        except:
            await message.reply("Команда должна быть ответом на сообщение")
            return
        cursor.execute("UPDATE users SET status = 4 WHERE user_id = ?",(user,))
        connect.commit()
        await message.reply("Вы успешно выдали Гаранта пользователю")

@dp.message_handler(commands=['гарант'], commands_prefix='-')
async def mute_handler(message):
    print(1)
    if message.from_user.id in config.owner_id or message.from_user.id in config.prava:
        print(2)
        try:
            user = message.reply_to_message.from_user.id
        except:
            await message.reply("Команда должна быть ответом на сообщение")
            return
        cursor.execute("UPDATE users SET status = 0 WHERE user_id = ?",(user,))
        connect.commit()
        await message.reply("Вы успешно забрали Гаранта у пользователя")


@dp.message_handler(commands=['директор'], commands_prefix='+')
async def mute_handler(message):
    print(1)
    if message.from_user.id in config.owner_id or message.from_user.id in config.prava:
        print(2)
        try:
            user = message.reply_to_message.from_user.id
        except:
            await message.reply("Команда должна быть ответом на сообщение")
            return
        cursor.execute("UPDATE users SET status = 5 WHERE user_id = ?",(user,))
        connect.commit()
        await message.reply("Вы успешно выдали Директора пользователю")

@dp.message_handler(commands=['директор'], commands_prefix='-')
async def mute_handler(message):
    print(1)
    if message.from_user.id in config.owner_id or message.from_user.id in config.prava:
        print(2)
        try:
            user = message.reply_to_message.from_user.id
        except:
            await message.reply("Команда должна быть ответом на сообщение")
            return
        cursor.execute("UPDATE users SET status = 0 WHERE user_id = ?",(user,))
        connect.commit()
        await message.reply("Вы успешно забрали Директора у пользователя")

@dp.message_handler(commands=['admin'], commands_prefix='/')
async def mute_handler(message):
    print(1)
    if message.from_user.id in config.owner_id or message.from_user.id in config.prava:
        print(2)
        try:
            user = message.reply_to_message.from_user.id
        except:
            await message.reply("Команда должна быть ответом на сообщение")
            return
        cursor.execute("UPDATE users SET status = 7 WHERE user_id = ?",(user,))
        connect.commit()
        await message.reply("Вы успешно выдали Администратора пользователю")


@dp.message_handler(commands=['оффтоп'], commands_prefix='/')
async def offtop_handler(message):
    # Проверяем, является ли бот администратором или владельцем чата
    user_id = message.from_user.id
    status = cursor.execute("SELECT status FROM users WHERE user_id = ?",(user_id,)).fetchone()[0]
    if status == 3 or status == 4 or status == 5 or status == 6 or status == 7:
        # Получаем информацию о пользователе, который отправил команду
        member = await message.chat.get_member(user_id=message.from_user.id)
        usid = message.from_user.id
        
        # Устанавливаем время мута на 5 мин

        if message.reply_to_message:
            user = message.reply_to_message.from_user.id
            data = timedelta(minutes=5)
        else:
            return await message.reply('🤐 Вы не указали кому дать мут!')
        # Выдаём молчание пользователю
        try:
            await message.chat.restrict(user_id=user,
                                        permissions=mute_perms,
                                        until_date=data)
            await message.reply(text='🤐 Вам выдано молчание на 5 минут за оффтоп!',
                                parse_mode='html')
        except Exception as ex:
            await message.reply(f'👾 Не удалось выдать молчание\nОшибка: <code>{ex}</code>', parse_mode='html')




@dp.message_handler(commands=['mute'], commands_prefix='/')
async def mute_handler(message):

    bot = await message.chat.get_member(user_id=message.bot.id)
    text = ''
    if not isinstance(bot, (ChatMemberOwner, ChatMemberAdministrator)):
        return await message.reply('👾 У бота нет админки в чате :(')
    elif not bot.can_delete_messages:
        text += '[+] <code>🗑️ Удаление сообщений</code>\n'
    elif not bot.can_restrict_members:
        text += '[+] <code>👤 Блокировка пользователей</code>\n'
    if text:
        return await message.reply(f'👾 Боту нужны такие разрешения:\n\n{text}\n\n📞 Администраторы должны выдать их '
                                   f'боту чтобы был доступ к командам модерирования!',parse_mode='html')

    member = await message.chat.get_member(user_id=message.from_user.id)
    usid = message.from_user.id
    if usid != config.owner_id:
        if not isinstance(member, (ChatMemberOwner, ChatMemberAdministrator)):
            return await message.reply('👾 У вас нет админки в этом чате!')

    arg = message.text.split()[1:]

    if len(arg) > 0:

        data = await get_datetime(''.join(arg[:-1]))

        if data is None:
            data = timedelta(minutes=15)

        if message.reply_to_message:
            user = message.reply_to_message.from_user.id
            data = await get_datetime(''.join(arg[0]))
            if data is None:
                data = timedelta(minutes=15)
        elif arg[-1].isdigit():
            user = arg[-1]

        else:
            return await message.reply('🤐 Вы не указали кому дать мут!')

        try:
            try:
                user_name = message.from_user.full_name
            except Exception as ex:
                return await message.reply(f'Ошибка: <code>{ex}</code>',
                                           parse_mode='html')
            await message.chat.restrict(user_id=user,
                                        permissions=mute_perms,
                                        until_date=data)
            await message.reply(text=f'🤐 Пользователь  <a href="tg://user?id={user}">{user_name}</a> был замучен на <code>{str(data)}</code>',
                                       reply_markup=unmute_kb(user),parse_mode='html')
        except Exception as ex:
            await message.reply(f'👾 Не удалось замутить {arg[-1]}\n'
                                       f'Ошибка: <code>{ex}</code>',parse_mode='html')
    else:
        await message.reply('👾 Используйте: <code>/mute число *ссылка</code>',parse_mode='html')


@dp.message_handler(commands=['unmute'], commands_prefix='/')
async def unmute_handler(message: types.Message):

    call = message
    if not isinstance(message,Message):
        message = message.message
    bot = await message.chat.get_member(user_id=message.bot.id)
    text = ''
    if not isinstance(bot, (ChatMemberOwner, ChatMemberAdministrator)):
        return await message.reply('👾 У бота нет админки в чате :(')
    elif not bot.can_delete_messages:
        text += '[+] <code>🗑️ Удаление сообщений</code>\n'
    elif not bot.can_restrict_members:
        text += '[+] <code>👤 Блокировка пользователей</code>\n'
    if text:
        return await message.reply(f'👾 Боту нужны такие разрешения:\n\n{text}\n\n📞 Администраторы должны выдать их '
                                   f'боту чтобы был доступ к командам модерирования!',parse_mode='html')

    member = await message.chat.get_member(user_id=call.from_user.id)
    usid = message.from_user.id
    if usid != config.owner_id:
        if not isinstance(member, (ChatMemberOwner, ChatMemberAdministrator)):
            return await message.reply('👾 У вас нет админки в этом чате!')

    if isinstance(call,Message):
        arg = message.text.split()[1:]
        if len(arg) == 0 and not message.reply_to_message:
            return await message.reply('👾 Используйте: <code>/unmute *{ссылка}</code>',parse_mode='html')

    if isinstance(call,Message):
        if message.reply_to_message:
            user = message.reply_to_message.from_user.id
        else:
            try:
                if arg[-1].isdigit():
                    user = arg[-1]
            except:
                return await message.reply(f'👾 Вы не указали кого размутить!')
    else:
        user = int(call.data.split('_')[1])

    try:
        try:
            user_name = message.from_user.full_name
        except Exception as ex:
            return await message.reply(f'Ошибка: <code>{ex}</code>',
                                       parse_mode='html')
        await message.chat.restrict(user_id=user,
                                    permissions=unmute_perms)
        await message.reply(text=f' <a href="tg://user?id={user}">{user_name}</a> 🤤 Пользователь был размучен!',parse_mode='html')
    except Exception as ex:
        await message.reply(f'👾 Не удалось размутить \n'
                                   f'Ошибка: <code>{ex}</code>',parse_mode='html')
@dp.message_handler(commands=['ban'], commands_prefix='/')
async def ban_handler(message: types.Message):

    bot = await message.chat.get_member(user_id=message.bot.id)
    text = ''
    if not isinstance(bot, (ChatMemberOwner, ChatMemberAdministrator)):
        return await message.reply('👾 У бота нет админки в чате :(')
    elif not bot.can_delete_messages:
        text += '[+] <code>🗑️ Удаление сообщений</code>\n'
    elif not bot.can_restrict_members:
        text += '[+] <code>👤 Блокировка пользователей</code>\n'
    if text:
        return await message.reply(f'👾 Боту нужны такие разрешения:\n\n{text}\n\n📞 Администраторы должны выдать их '
                                   f'боту чтобы был доступ к командам модерирования!',parse_mode='html')

    member = await message.chat.get_member(user_id=message.from_user.id)
    usid = message.from_user.id
    if usid != config.owner_id:
        if not isinstance(member, (ChatMemberOwner, ChatMemberAdministrator)):
            return await message.reply('👾 У вас нет админки в этом чате!')

    arg = message.text.split()[1:]
    if len(arg) == 0:
        return await message.reply('👾 Используйте: <code>/ban {число} *{ссылка}</code>',parse_mode='html')

    data = await get_datetime(''.join(arg[:-1]))
    if data is None:
        data = timedelta(seconds=30)

    if message.reply_to_message:
        user = message.reply_to_message.from_user.id
        data = await get_datetime(''.join(arg[0]))
        if data is None:
            data = timedelta(seconds=30)
    elif arg[-1].isdigit():
        user = arg[-1]
    else:
        return await message.reply('👾 Вы не указали кого забанить!')

    try:
        try:
            user_name = message.from_user.full_name
        except Exception as ex:
            return await message.reply(f'Ошибка: <code>{ex}</code>',
                                       parse_mode='html')

        await message.chat.kick(user_id=user,until_date=data)
        xd = f'до <code>{str(data)}</code>' if data.total_seconds() > 30 else 'навсегда'
        await message.reply(text=f'👾 Пользователь  <a href="tg://user?id={user}">{user_name}</a> был забанен {xd}',
                                   reply_markup=unban_kb(user),parse_mode='html')
    except Exception as ex:
        await message.reply(f'👾 Не удалось забанить \n'
                                   f'Ошибка: <code>{ex}</code>',
                                   parse_mode='html')

@dp.message_handler(commands=['start'], commands_prefix='/')
async def unban_handler(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username
    us = cursor.execute("SELECT tag FROM users WHERE user_id = ?",(user_id,)).fetchone()

    if us is None:
        now = datetime.now().replace(microsecond=0)
        formatted_date = now.strftime('%m-%d')
        cursor.execute("INSERT INTO users VALUES(?,?,?,?,?,?,?,?,?,?,?)",(user_id,message.from_user.first_name,username,0,35,0,0,"","",0,0))
        connect.commit()
        await message.reply("""Привет,тут ты можешь проверить человека на скам,напиши "чек ми" чтобы проверить себя или чек @юзернейм чтобы проверить другого пользователя
По всем вопросам писать @GaaRDeeX""")
    else:
        await message.reply("""Привет,тут ты можешь проверить человека на скам,напиши "чек ми" чтобы проверить себя или чек @юзернейм чтобы проверить другого пользователя
По всем вопросам писать @GaaRDeeX""")
@dp.message_handler(commands=['unban'], commands_prefix='/')
async def unban_handler(message: Message):

    call = message
    if not isinstance(message, Message):
        message = message.message

    bot = await message.chat.get_member(user_id=message.bot.id)
    text = ''
    if not isinstance(bot, (ChatMemberOwner, ChatMemberAdministrator)):
        return await message.reply('👾 У бота нет админки в чате :(')
    elif not bot.can_delete_messages:
        text += '[+] <code>🗑️ Удаление сообщений</code>\n'
    elif not bot.can_restrict_members:
        text += '[+] <code>👤 Блокировка пользователей</code>\n'
    if text:
        return await message.reply(f'👾 Боту нужны такие разрешения:\n\n{text}\n\n📞 Администраторы должны выдать их '
                                   f'боту чтобы был доступ к командам модерирования!')

    member = await message.chat.get_member(user_id=message.from_user.id)
    usid = message.from_user.id
    if usid != config.owner_id:
        if not isinstance(member, (ChatMemberOwner, ChatMemberAdministrator)):
            return await message.reply('👾 У вас нет админки в этом чате!')

    arg = message.text.split()[1:]


    if message.reply_to_message:
        user = message.reply_to_message.from_user.id

    elif arg[-1].isdigit():
        user = arg[-1]
    else:
        return await message.reply('👾 Вы не указали кого забанить!')

    try:
        try:
            user_name = cursor.execute(
                "SELECT user_name from users where user_id = ?", (user,))
            user_name = cursor.fetchone()
            user_name = user_name[0]
        except Exception as ex:
            return await message.reply(f'Ошибка: <code>{ex}</code>',
                                   parse_mode='html')

        await message.chat.unban(user_id=user)
        await message.reply(text=f'👾 Пользователь <a href="tg://user?id={user}">{user_name}</a> был разбанен',parse_mode='html')
    except Exception as ex:
        await message.reply(f'👾 Не удалось разбанить <a href="tg://user?id={user}">{user_name}</a>\n'
                                   f'Ошибка: <code>{ex}</code>',
                                   parse_mode='html')



@dp.message_handler()
async def mute_handler(message):
    user_id = message.from_user.id
    username = message.from_user.username
    us = cursor.execute("SELECT tag FROM users WHERE user_id = ?",(user_id,)).fetchone()

    if us is None:
        now = datetime.now().replace(microsecond=0)
        formatted_date = now.strftime('%m-%d')
        cursor.execute("INSERT INTO users VALUES(?,?,?,?,?,?,?,?,?,?,?)",(user_id,message.from_user.first_name,username,0,35,0,0,"","",0,0))
        connect.commit()
    else:
        us = us[0]
        if us != username:
            cursor.execute("UPDATE users SET tag = ? WHERE user_id = ?",(username,user_id))
        if message.text.lower() == "игры":
            await message.reply("""🎮 Игры:
🃏 Казино [ставка]
⚽️ Футбол [сумма]""")
        if message.text.startswith("Казино") or message.text.startswith("казино"):
            if message.text != 'Казино':
                msg = message
                user_id = msg.from_user.id
                chat_id = message.chat.id
                user_name = msg.from_user.first_name
                win = ['🙂', '😋', '😄', '😃']
                loser = ['😔', '😕', '😣', '😞', '😢']

                rwin = random.choice(win)
                rloser = random.choice(loser)
                rx=np.random.choice([1,2,3,4,5,6,7,8,9,10], 1, p=[0.15, 0.1, 0.1, 0.11, 0.1, 0.12, 0.1, 0.15, 0.05, 0.02])[0]
                try:
                    su = msg.text.split()[1]
                    su2 = (su).replace('к', '000')
                    su3 = (su2).replace('м', '000000')
                    su4 = (su3).replace('.', '')
                    su5 = float(su4)
                    summ = int(su5)
                    summ2 = '{:,}'.format(summ).replace(',', '.')
                except:
                    await message.reply('‼️  Неправильный ввод команды!\nПример: Казино 1 ')
                    return
                balance = cursor.execute("SELECT balance from users where user_id = ?", (message.from_user.id,)).fetchone()[0]
                
                need_seconds3 = 4
                current_time_bonus3 = datetime.now()
                last_datetime3 = game_time.get(message.from_user.id)

                                # Если первое сообщение (время не задано)
                if not last_datetime3:
                    game_time[message.from_user.id] = current_time_bonus3
                    last_datetime3 = datetime.fromtimestamp(0)
                if last_datetime3:

                    delta_seconds3 = (current_time_bonus3 - last_datetime3).total_seconds()

                    seconds_left3 = int(need_seconds3 - delta_seconds3)

                    if seconds_left3 > 0:
                        left1 = seconds_left3
                        await bot.send_message(message.chat.id,f'♣️<a href="tg://user?id={user_id}">{user_name}</a>, играть можно через {round(left1)} сек {rloser}',parse_mode='html')
                    else:
                        game_time[message.from_user.id] = current_time_bonus3
                        if balance >= summ:
                            if summ > 0:

                                if int(rx) ==1:
                                    c = Decimal(summ)
                                    c2 = round(c)
                                    c2 = '{:,}'.format(c2).replace(',', '.')
                                    await bot.send_message(chat_id,f'♣️Игра: Казино\n<a href="tg://user?id={user_id}">{user_name}</a>\n🕹️ Проигрыш: -{summ2}$  x0 {rloser}',parse_mode='html')
                                    
                                    cursor.execute(f'UPDATE users SET balance = {balance - summ} WHERE user_id = {user_id}')
                                    connect.commit()
                                    return
                                if int(rx) ==2:
                                    c = Decimal( summ * 0.25)
                                    c2 = round(c)
                                    c2 = '{:,}'.format(c2).replace(',', '.')
                                    await bot.send_message(chat_id,f'♣️Игра: Казино\n<a href="tg://user?id={user_id}">{user_name}</a>\n🕹️ Проигрыш: -{summ2}$  x0.25 {rloser}',parse_mode='html')

                                    cursor.execute(f'UPDATE users SET balance = balance - {summ} * 0.25 WHERE user_id = {user_id}')
                                    connect.commit()
                                    return
                                if int(rx) ==3:
                                    c = Decimal(summ * 0.5)
                                    c2 = round(c)
                                    c2 = '{:,}'.format(c2).replace(',', '.')
                                    await bot.send_message(chat_id,f'♣️Игра: Казино\n<a href="tg://user?id={user_id}">{user_name}</a>\n🕹️ Проигрыш: -{summ2}$  x0.5 {rloser}',parse_mode='html')

                                    cursor.execute(f'UPDATE users SET balance = balance - {summ} * 0.5 WHERE user_id = {user_id}')
                                    connect.commit()
                                    return
                                if int(rx) ==4:
                                    c = Decimal(summ * 0.75)
                                    c2 = round(c)
                                    c2 = '{:,}'.format(c2).replace(',', '.')
                                    await bot.send_message(chat_id,f'♣️Игра: Казино\n<a href="tg://user?id={user_id}">{user_name}</a>\n🕹️ Проигрыш: -{summ2}$  x0.75 {rloser}',parse_mode='html')

                                    cursor.execute(f'UPDATE users SET balance = balance - {summ} * 0.75 WHERE user_id = {user_id}')
                                    connect.commit()
                                    return
                                if int(rx) ==5:
                                    c = summ * 1
                                    c2 = round(c)
                                    c2 = '{:,}'.format(c2).replace(',', '.')
                                    await bot.send_message(chat_id,f'♣️Игра: Казино\n<a href="tg://user?id={user_id}">{user_name}</a>\n🕹️ Деньги остаются у вас: {summ2}$  x1 {rwin}',parse_mode='html')
                                        

                                    connect.commit()
                                    return
                                if int(rx) ==6:
                                    c = Decimal(summ * 1.25-summ)
                                    c2 = round(c)
                                    c2 = '{:,}'.format(c2).replace(',', '.')
                                    await bot.send_message(chat_id,f'♣️Игра: Казино\n<a href="tg://user?id={user_id}">{user_name}</a>\n🕹️ Выигрыш: +{c2}$  x1.25 {rwin}',parse_mode='html')

                                    cursor.execute(f'UPDATE users SET balance = (balance - {summ}) + ({summ} * 1.25) WHERE user_id = {user_id}')
                                    connect.commit()
                                    return
                                if int(rx) ==7:
                                    c = Decimal(summ * 1.5-summ)
                                    c2 = round(c)
                                    c2 = '{:,}'.format(c2).replace(',', '.')
                                    await bot.send_message(chat_id,f'♣️Игра: Казино\n<a href="tg://user?id={user_id}">{user_name}</a>\n🕹️ Выигрыш: +{c2}$  x1.5 {rwin}',parse_mode='html')

                                    cursor.execute(f'UPDATE users SET balance = (balance - {summ}) + ({summ} * 1.5) WHERE user_id = {user_id}')
                                    connect.commit()
                                    return
                                if int(rx) ==8:
                                    c = Decimal(summ * 1.75-summ)
                                    c2 = round(c)
                                    c2 = '{:,}'.format(c2).replace(',', '.')
                                    await bot.send_message(chat_id,f'♣️Игра: Казино\n<a href="tg://user?id={user_id}">{user_name}</a>\n🕹️ Выигрыш: +{c2}$  x1.75 {rwin}',parse_mode='html')

                                    cursor.execute(f'UPDATE users SET balance = (balance - {summ}) + ({summ} * 1.75) WHERE user_id = {user_id}')
                                    connect.commit()
                                    return
                                if int(rx) ==9:
                                    c = Decimal(summ * 2-summ)
                                    c2 = round(c)
                                    c2 = '{:,}'.format(c2).replace(',', '.')
                                    await bot.send_message(chat_id,
                                                           f'♣️Игра: Казино\n<a href="tg://user?id={user_id}">{user_name}</a>\n🕹️ Выигрыш: +{c2}$  x2 {rwin}',
                                                           parse_mode='html')
                                    cursor.execute(f'UPDATE users SET balance = (balance - {summ}) + ({summ} * 2) WHERE user_id = {user_id}')
                                    connect.commit()
                                    return
                                if int(rx) ==10:
                                    c = Decimal(summ * 3-summ)
                                    c2 = round(c)
                                    c2 = '{:,}'.format(c2).replace(',', '.')
                                    await bot.send_message(chat_id,
                                                           f'♣️Игра: Казино\n<a href="tg://user?id={user_id}">{user_name}</a>\n🕹️ Выигрыш: +{c2}$  x3 {rwin}',
                                                           parse_mode='html')
                                    cursor.execute(f'UPDATE users SET balance = (balance - {summ}) + ({summ} * 3) WHERE user_id = {user_id}')
                                    connect.commit()
                                    return

                            elif summ <= 1:
                                await bot.send_message(chat_id,f'♠️ <a href="tg://user?id={user_id}">{user_name}</a>, нельзя ставить отрицательное число! {rloser}',parse_mode='html')
                        elif int(balance) <= int(summ):
                            await bot.send_message(chat_id,f'♠️ <a href="tg://user?id={user_id}">{user_name}</a>, недостаточно средств! {rloser}',parse_mode='html')

            else:
                await bot.send_message(message.chat.id,f'‼️ <a href="tg://user?id={user_id}">{user_name}</a>,Ошибка! Пример Казино [сумма] {rloser}',parse_mode='html')
                return
        if message.text.startswith("Футбол") or message.text.startswith("футбол"):
            user_id = message.from_user.id

            rwin = ['🙂', '😋', '😄', '😃']
            rloser = ['😔', '😕', '😣', '😞', '😢']
            win = random.choice(rwin)
            loser = random.choice(rloser)
            if message.text != 'Футбол':
                balance = cursor.execute("SELECT balance from users where user_id = ?", (message.from_user.id,)).fetchone()[0]
                balance2 = '{:,}'.format(balance).replace(',', '.')
                msg = message

                chat_id = message.chat.id
                user_name = msg.from_user.first_name

                try:
                    su = msg.text.split()[1]
                    su2 = (su).replace('к', '000')
                    su3 = (su2).replace('м', '000000')
                    su4 = (su3).replace('.', '')
                    su5 = float(su4)
                    summ = int(su5)
                    summ2 = '{:,}'.format(summ).replace(',', '.')
                except:
                    await message.reply('‼️  Неправильный ввод команды!\nПример: Футбол 1 ')
                    return
                
                need_seconds3 = 4
                current_time_bonus3 = datetime.now()
                last_datetime3 = game_time.get(message.from_user.id)

                                # Если первое сообщение (время не задано)
                if not last_datetime3:
                    game_time[message.from_user.id] = current_time_bonus3
                    last_datetime3 = datetime.fromtimestamp(0)
                if last_datetime3:

                                    # Разница в секундах между текущим временем и временем последнего сообщения
                    delta_seconds3 = (current_time_bonus3 - last_datetime3).total_seconds()

                                        # Осталось ждать секунд перед отправкой
                    seconds_left3 = int(need_seconds3 - delta_seconds3)

                                    # Если время ожидания не закончилось
                    if seconds_left3 > 0:
                        left1 = seconds_left3
                        await bot.send_message(message.chat.id,f'⚽ <a href="tg://user?id={user_id}">{user_name}</a>, играть можно через {round(left1)} сек {loser}',parse_mode='html')
                    else:
                        game_time[message.from_user.id] = current_time_bonus3
                        if balance >= summ:
                            if summ > 0:
                                rx1 = await message.reply_dice(emoji="⚽")
                                await asyncio.sleep(2)
                                rx = rx1.dice.value
                        
                                if int(rx) == 1:
                                    c = Decimal(summ * 0)
                                    c2 = round(c)
                                    c2 = '{:,}'.format(c2).replace(',', '.')

                                    await bot.send_message(chat_id,f'<a href="tg://user?id={user_id}">{user_name}</a>,мяч не попал в ворота!\n🎟️ Вы проиграли: -{c2}$ {loser}',parse_mode='html')
                                    cursor.execute(
                                        f'UPDATE users SET balance = (balance - {summ})   + ({summ} * 0) WHERE user_id = {user_id}')
                                    connect.commit()
                                    return
                                if int(rx) == 3:
                                    c = Decimal(summ * 1.25-summ)
                                    c2 = round(c)
                                    c2 = '{:,}'.format(c2).replace(',', '.')

                                    await bot.send_message(chat_id,
                                                           f'<a href="tg://user?id={user_id}">{user_name}</a>,невероятно,мяч попал в ворота\n🏅 Выйгрыш составляет: +{c2}$ {win}',
                                                           parse_mode='html')
                                    
                                    cursor.execute(
                                        f'UPDATE users SET balance = (balance - {summ})   + ({summ} *  1.25) WHERE user_id = {user_id}')
                                       
                                    connect.commit()
                                    return
                                if int(rx) == 2:
                                    c = Decimal(summ * 0)
                                    c2 = round(c)
                                    c2 = '{:,}'.format(c2).replace(',', '.')

                                    connect.commit()

                                    await bot.send_message(chat_id,
                                                           f'<a href="tg://user?id={user_id}">{user_name}</a>,мяч не попал в ворота!\n🎟️ Вы проиграли: -{c2}$ {loser}',
                                                           parse_mode='html')
                                    cursor.execute(f'UPDATE users SET balance = (balance - {summ})  + ({summ} * 0) WHERE user_id = {user_id}')
                                    connect.commit()
                                    return
                                if int(rx) == 5:
                                    c = Decimal(summ * 2-summ)
                                    c2 = round(c)
                                    c2 = '{:,}'.format(c2)
                                    await bot.send_message(chat_id,f'<a href="tg://user?id={user_id}">{user_name}</a>, невероятно,мяч попал в ворота\n🏅 Выйгрыш составляет: +{c2}$ {win}',parse_mode='html')
                                    cursor.execute(f'UPDATE users SET balance = (balance - {summ}) + ({summ} * 2) WHERE user_id = {user_id}')

                                    connect.commit()
                                    return

                                if int(rx) == 4:
                                    c = Decimal(summ * 1)
                                    c2 = round(c)
                                    c2 = '{:,}'.format(c2)
                                    await bot.send_message(chat_id,f'<a href="tg://user?id={user_id}">{user_name}</a>, 🍀 Ваши деньги сохранились\n🎟️ Вы сохранили: {c2}$ {win}',parse_mode='html')
                                    return

                            elif summ <= 1:
                                await bot.send_message(chat_id,f'⚽ <a href="tg://user?id={user_id}">{user_name}</a>, нельзя ставить отрицательное число! {loser}',parse_mode='html')
                        elif int(balance) <= int(summ):
                            await bot.send_message(chat_id,f'⚽ <a href="tg://user?id={user_id}">{user_name}</a>, недостаточно средств! {loser}',parse_mode='html')

            else:
                await bot.send_message(message.chat.id,f'‼️ <a href="tg://user?id={user_id}">{user_name}</a>,Ошибка! Пример Футбол [сумма] {rloser}',parse_mode='html')
                return

        if message.text.startswith("Поинтдать"):
            try:
                mon = int(message.text.split()[1])
            except:
                await message.reply("Ошибка вы не верно ввели команду\nПример: Поинтдать сумма")
            if message.reply_to_message:
                user_isd = message.reply_to_message.from_user.id
                balance = cursor.execute("SELECT balance FROM users WHERE user_id = ?",(message.from_user.id,)).fetchone()[0]
                if mon < 0:
                    await message.reply("Вы не можете передать пользователю отрицательное количество поинтов")
                else: 
                    if balance  < mon - 1:

                        await message.reply("У вас недостаточно поинтов")
                        
                    else:
                        cursor.execute("UPDATE users SET balance = balance - ? WHERE user_id = ?",(mon,message.from_user.id,))
                        cursor.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?",(mon,user_isd,))
                        connect.commit()
                        await message.reply(f"Вы успешно передали {mon} поинтов")
                    
            else:
                await message.reply("Команда должна быть ответом на сообщение")
        if message.text.startswith("Топ") or message.text.startswith("топ"):
            top_balance = cursor.execute("SELECT user_name, slito FROM users ORDER BY slito DESC LIMIT 10")
            top_balance = cursor.fetchall()

            top_message = "Топ 10 пользователей:\n\n"
            emoji_numbers = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]

            for i, (user_name, slito) in enumerate(top_balance):
                top_message += f"{emoji_numbers[i]} {user_name}: {slito} скамеров\n"

            await message.reply(top_message)
        if message.text.lower() in ["значение"]:
            user_id = message.from_user.id
            status = cursor.execute("SELECT status FROM users WHERE user_id = ?",(user_id,)).fetchone()[0]
            if status == 3 or status == 5 or status == 7 or status == 6:
                balance = cursor.execute("SELECT admin_balance FROM users WHERE user_id = ?",(user_id,)).fetchone()[0]

                await message.reply(f"На балансе {balance} значений")
        if message.text.lower() in ["б","баланс"]:
            if message.reply_to_message:
                user_isd = message.reply_to_message.from_user.id
                balance = cursor.execute("SELECT balance FROM users WHERE user_id = ?",(user_isd,)).fetchone()[0]

                await message.reply(f"На балансе пользователя {balance} поинтов")
            else:
                balance = cursor.execute("SELECT balance FROM users WHERE user_id = ?",(message.from_user.id,)).fetchone()[0]

                await message.reply(f"На вашем балансе {balance} поинтов")
        if message.text.lower() == "персонал":
            # Получаем список пользователей с статусом 4 (администраторов)
            
            garant = cursor.execute("SELECT tag FROM users WHERE status = 4").fetchall()
            garant_list = "\n@".join(str(admin[0]) for admin in garant)
            stajer = cursor.execute("SELECT tag FROM users WHERE status = 3").fetchall()
            stajer_list = "\n@".join(str(admin[0]) for admin in stajer)
            director = cursor.execute("SELECT tag FROM users WHERE status = 5").fetchall()
            director_list = "\n@".join(str(admin[0]) for admin in director)
            president = cursor.execute("SELECT tag FROM users WHERE status = 6").fetchall()
            president_list = "\n@".join(str(admin[0]) for admin in president)
            admins = cursor.execute("SELECT tag FROM users WHERE status = 7").fetchall()
            admin_list = "\n@".join(str(admin[0]) for admin in admins)
            await message.reply(f"""Весь персонал асгард базы
🤐Создатели
@GaaRDeeX
@Rostik_y
🤫Призиденты 
@{president_list}
⭐️ Директора 
@{director_list}
⭐️⭐️ Гаранты
@{garant_list}
⭐️⭐️⭐️ Админы
@{admin_list}
⭐️⭐️⭐️⭐️ Стажёры 
@{stajer_list}""", parse_mode="html")
        if message.text.startswith("Статистика бота"):

            user_id = message.from_user.id
            if user_id in config.owner_id:
                coint = cursor.execute("SELECT * FROM users").fetchall()
                provereno = cursor.execute("SELECT * FROM users WHERE status = 1").fetchall()
                scam = cursor.execute("SELECT * FROM users WHERE status = 2").fetchall()
                stajer = cursor.execute("SELECT * FROM users WHERE status = 3").fetchall()
                garant = cursor.execute("SELECT * FROM users WHERE status = 4").fetchall()
                director = cursor.execute("SELECT * FROM users WHERE status = 5").fetchall()

                await bot.send_message(message.from_user.id,f"Всего пользователей в боте - {len(coint)}\nПроверены - {len(provereno)}\nСкамеры - {len(scam)}\nСтажёров - {len(stajer)}\nГарантов - {len(garant)}\nДиректоров - {len(director)}")
        if message.text.lower() in ["апелляция"]:
            await message.reply("Если вас занесли в скам базу по ошибке напишите команду /garant и расскажите о своей проблеме одному из админов")
        if message.text.lower() in ["чек ми"]:
            user_id = message.from_user.id
            status = cursor.execute("SELECT status FROM users WHERE user_id = ?",(user_id,)).fetchone()[0]
            serch = cursor.execute("SELECT serch FROM users WHERE user_id = ?",(user_id,)).fetchone()[0]
            slito = cursor.execute("SELECT slito FROM users WHERE user_id = ?",(user_id,)).fetchone()[0]
            if user_id in config.owner_id:
                current_date = datetime.now()
                month_en = current_date.strftime("%B")
                month_ru = MONTHS_RU.get(month_en)
                formatted_date = current_date.strftime(f"%d {month_ru} %Y")
                tags = cursor.execute("SELECT tag FROM users WHERE user_id = ?",(user_id,)).fetchone()[0]
                cursor.execute("UPDATE users SET serch = serch + 1 WHERE user_id = ?",(user_id,))
                connect.commit()
                with open("seng/sozd.jpg", "rb") as photo:        
                    fir_name = message.from_user.first_name
                    await message.reply_photo(
            photo=photo,  # URL или путь к файлу фотографии
            caption=f"""Информация о {fir_name} [{user_id}]
      
❓ Официальный  создатель Асгард
🤝 Оригинальный юзернейм @{tags} других аккаунтов не имею

🔥 Скаммеров слито: {slito}

👍 Будьте аккуратны и всегда используйте проверенных гарантов, их можно найти написав команду /garant

🔍 Искали {serch} раз
🗓 Проверено {formatted_date}""")
                return  
            if status == 3:
                current_date = datetime.now()
                month_en = current_date.strftime("%B")
                month_ru = MONTHS_RU.get(month_en)
                formatted_date = current_date.strftime(f"%d {month_ru} %Y")

                cursor.execute("UPDATE users SET serch = serch + 1 WHERE user_id = ?",(user_id,))
                connect.commit()
                with open("seng/stajer.jpg", "rb") as photo:
                    
                    fir_name = message.from_user.first_name
                    await message.reply_photo(
        photo=photo,  # URL или путь к файлу фотографии
        caption=f"""Информация о {fir_name} [{message.from_user.id}]
  
❓ Пользователь не официальный гарант асгард
🤫Вероятность скама 25%

🔥 Скаммеров слито: {slito}

👍 Будьте аккуратны и всегда используйте проверенных гарантов, их можно найти написав команду /garant

🔍 Искали {serch} раз
🗓 Проверено {formatted_date}""")

            if status == 5:
                current_date = datetime.now()
                month_en = current_date.strftime("%B")
                month_ru = MONTHS_RU.get(month_en)
                formatted_date = current_date.strftime(f"%d {month_ru} %Y")
                tags = cursor.execute("SELECT tag FROM users WHERE user_id = ?",(user_id,)).fetchone()[0]
                cursor.execute("UPDATE users SET serch = serch + 1 WHERE user_id = ?",(user_id,))
                connect.commit()
                with open("seng/direktor.jpg", "rb") as photo:
                    
                    fir_name = message.from_user.first_name
                    await message.reply_photo(
        photo=photo,  # URL или путь к файлу фотографии
        caption=f"""Информация о {fir_name} [{message.from_user.id}]
  
❓ Пользователь является официальным директором Асгард
🤝Оригинальный юз @{tags}
Других аккаунтов не имею🌟

🔥 Скаммеров слито: {slito}

👍 Будьте аккуратны и всегда используйте проверенных гарантов, их можно найти написав команду /garant

🔍 Искали {serch} раз
🗓 Проверено {formatted_date}""")
            if status == 6:
                current_date = datetime.now()
                month_en = current_date.strftime("%B")
                month_ru = MONTHS_RU.get(month_en)
                formatted_date = current_date.strftime(f"%d {month_ru} %Y")
                tags = cursor.execute("SELECT tag FROM users WHERE user_id = ?",(user_id,)).fetchone()[0]
                cursor.execute("UPDATE users SET serch = serch + 1 WHERE user_id = ?",(user_id,))
                connect.commit()
                with open("seng/president.jpg", "rb") as photo:
                    
                    fir_name = message.from_user.first_name
                    await message.reply_photo(
        photo=photo,  # URL или путь к файлу фотографии
        caption=f"""Информация о {fir_name} [{message.from_user.id}]
  
❓ Официальный  президент Асгард
🌟Пользователь имеет высшую должность асгард базы 

🔥Скамеров слито: {slito}

👍 Будьте аккуратны и всегда используйте проверенных гарантов, их можно найти написав команду /garant

🔍 Искали {serch} раз
🗓 Проверено {formatted_date}""")
            if status == 7:
                current_date = datetime.now()
                month_en = current_date.strftime("%B")
                month_ru = MONTHS_RU.get(month_en)
                formatted_date = current_date.strftime(f"%d {month_ru} %Y")
                tags = cursor.execute("SELECT tag FROM users WHERE user_id = ?",(user_id,)).fetchone()[0]
                cursor.execute("UPDATE users SET serch = serch + 1 WHERE user_id = ?",(user_id,))
                connect.commit()
                with open("seng/admin.jpg", "rb") as photo:
                    
                    fir_name = message.from_user.first_name
                    await message.reply_photo(
        photo=photo,  # URL или путь к файлу фотографии
        caption=f"""Информация о {fir_name} [{message.from_user.id}]
  
❓ Пользователь не официальный гарант скам базы,а администратор 
Вероятность скама: 25%

🔥 Скаммеров слито: {slito}

👍 Будьте аккуратны и всегда используйте проверенных гарантов,чтобы найти гаранта напишите команду /garant 🌟

🔍 Искали {serch} раз
🗓 Проверено {formatted_date}""")
            if status == 1:
                current_date = datetime.now()
                month_en = current_date.strftime("%B")
                month_ru = MONTHS_RU.get(month_en)
                formatted_date = current_date.strftime(f"%d {month_ru} %Y")

                cursor.execute("UPDATE users SET serch = serch + 1 WHERE user_id = ?",(user_id,))
                connect.commit()
                with open("seng/garant.jpg", "rb") as photo:
                    
                    fir_name = message.from_user.first_name
                    await message.reply_photo(
        photo=photo,  # URL или путь к файлу фотографии
        caption=f"""Информация о {fir_name} 
 
🆔: [{message.from_user.id}]
  
⚠️ Пользователь проверен создателем скам базы ⚠️

   ▫️ Вероятность скама: 20%

   ▫️ Скаммеров слито: {slito}
 
🕵️ Будьте бдительны и всегда используйте только проверенных гарантов 
👮чтобы увидеть список гарантов введите команду /garant 

 🔍 Искали: {serch} раз
 💻 Проверено: {formatted_date}""")
            if status == 4:
                current_date = datetime.now()
                month_en = current_date.strftime("%B")
                month_ru = MONTHS_RU.get(month_en)
                formatted_date = current_date.strftime(f"%d {month_ru} %Y")

                cursor.execute("UPDATE users SET serch = serch + 1 WHERE user_id = ?",(user_id,))
                connect.commit()
                with open("seng/garants.jpg", "rb") as photo:
                    
                    fir_name = message.from_user.first_name
                    await message.reply_photo(
        photo=photo,  # URL или путь к файлу фотографии
        caption=f"""Информация о {fir_name} [{message.from_user.id}]
  
❓ Пользователь является официальным гарантом Асгард

🔥 Скаммеров слито: {slito}

👍 Будьте аккуратны и всегда используйте проверенных гарантов, не ведитесь на обман!

🔍 Искали {serch} раз
🗓 Проверено {formatted_date}""")
            if status == 2:
                current_date = datetime.now()
                month_en = current_date.strftime("%B")
                month_ru = MONTHS_RU.get(month_en)
                formatted_date = current_date.strftime(f"%d {month_ru} %Y")
                url = cursor.execute("SELECT pruf FROM users WHERE user_id = ?",(user_id,)).fetchone()[0]
                prich = cursor.execute("SELECT pritc FROM users WHERE user_id = ?",(user_id,)).fetchone()[0]
                vero = cursor.execute("SELECT vero FROM users WHERE user_id = ?",(user_id,)).fetchone()[0]
                
                cursor.execute("UPDATE users SET serch = serch + 1 WHERE user_id = ?",(user_id,))
                connect.commit()
                with open("seng/scam.jpg", "rb") as photo:
                    
                    fir_name = message.from_user.first_name
                    await message.reply_photo(
        photo=photo,  # URL или путь к файлу фотографии
        caption=f"""📳Информация: {fir_name}

🆔: {message.from_user.id}
          
▫️Репутация: СКАММЕР ⚠️
▫️Вероятность скама: {vero}%
▫️Доказательства: {url}
📄 Причина: {prich}

🔥Скамеров слито: {slito}

Если вас занесли по ошибке, напишите команду "апелляция"

🔍 Искали {serch} раз
💻 Последний раз проверен {formatted_date}""")
            if status == 0:

                current_date = datetime.now()
                month_en = current_date.strftime("%B")
                month_ru = MONTHS_RU.get(month_en)
                formatted_date = current_date.strftime(f"%d {month_ru} %Y")

                cursor.execute("UPDATE users SET serch = serch + 1 WHERE user_id = ?",(user_id,))
                connect.commit()
                with open("seng/nobase.jpg", "rb") as photo:
                    
                    fir_name = message.from_user.first_name
                    await message.reply_photo(
        photo=photo,  # URL или путь к файлу фотографии
        caption=f"""Информация о {fir_name}
 
🆔: [{message.from_user.id}]
  
⚠️ Пользователь не является  официальным гарантом скам базы ⚠️

   ▫️ Вероятность скама: 30%

   ▫️ Скаммеров слито: {slito}
 
🕵️ Будьте бдительны и всегда используйте только проверенных гарантов 
👮чтобы увидеть список гарантов введите команду /garant 

 🔍 Искали: {serch} раз
 💻 Проверено: {formatted_date}""")
        elif message.text.lower() == "помощь":
            await message.reply("""Всё команды которые есть в скам базе:
Чек ми-выдаст информацию о вас
Чек @юзернейм выдаст информацию о пользователе 
Апелляция-вы сможете написать апелляцию админку нашей базы,если вас занесли туда по ошибке

Как сливать скамера?
Всё что вам надо, это отправить юз или айди скамера,а также предъявить доказательства того,что человек скамер 
За каждого слитого скамера вы получаете репутация и если ваша репутация будет настолько большая,что при написании команды "топ" вы будете в нём,то вы получите призовые места
1.место инженер
2.место шеф
3.место олд годли 
Как стать админом?
К сожалению админов в базе достаточно,но при определенной сумме,вы можете попасть к нам в команду,если ваша анкета подойдёт
                """)
        elif message.text.startswith("чек") or message.text.startswith("Чек"):
            if message.reply_to_message:
                user_isd = message.reply_to_message.from_user.id
                try:
                    user_isd = message.reply_to_message.from_user.id

                except:
                    return
                us = cursor.execute("SELECT user_name FROM users WHERE user_id = ?",(user_isd,)).fetchone()
                if us is None:
                    await message.reply("Человека нету в базе\nосторожно!\n🆘🆘🆘🆘")
                else:

                    us = us[0]
                    status = cursor.execute("SELECT status FROM users WHERE user_id = ?",(user_isd,)).fetchone()[0]
                    serch = cursor.execute("SELECT serch FROM users WHERE user_id = ?",(user_isd,)).fetchone()[0]
                    slito = cursor.execute("SELECT slito FROM users WHERE user_id = ?",(user_isd,)).fetchone()[0]
                    user_name = cursor.execute("SELECT user_name FROM users WHERE user_id = ?",(user_isd,)).fetchone()[0]
                    if int(user_isd) in config.owner_id:
                        current_date = datetime.now()
                        month_en = current_date.strftime("%B")
                        month_ru = MONTHS_RU.get(month_en)
                        formatted_date = current_date.strftime(f"%d {month_ru} %Y")
                        tags = cursor.execute("SELECT tag FROM users WHERE user_id = ?",(user_isd,)).fetchone()[0]
                        cursor.execute("UPDATE users SET serch = serch + 1 WHERE user_id = ?",(user_isd,))
                        connect.commit()
                        with open("seng/sozd.jpg", "rb") as photo:
                            
                            fir_name = message.from_user.first_name
                            await message.reply_photo(
            photo=photo,  # URL или путь к файлу фотографии
            caption=f"""Информация о {user_name} [{user_isd}]
      
❓ Официальный  создатель Асгард
🤝 Оригинальный юзернейм @{tags} других аккаунтов не имею

🔥 Скаммеров слито: {slito}

👍 Будьте аккуратны и всегда используйте проверенных гарантов, их можно найти написав команду /garant

🔍 Искали {serch} раз
🗓 Проверено {formatted_date}""")
                        return
                    if status == 1:
                        current_date = datetime.now()
                        month_en = current_date.strftime("%B")
                        month_ru = MONTHS_RU.get(month_en)
                        formatted_date = current_date.strftime(f"%d {month_ru} %Y")

                        cursor.execute("UPDATE users SET serch = serch + 1 WHERE user_id = ?",(user_isd,))
                        connect.commit()
                        with open("seng/garant.jpg", "rb") as photo:
                            
                            fir_name = message.from_user.first_name
                            await message.reply_photo(
            photo=photo,  # URL или путь к файлу фотографии
            caption=f"""Информация о {user_name}
 
🆔: [{user_isd}]
  
⚠️ Пользователь проверен создателем скам базы ⚠️

   ▫️ Вероятность скама: 20%

   ▫️ Скаммеров слито: {slito}
 
🕵️ Будьте бдительны и всегда используйте только проверенных гарантов 
👮чтобы увидеть список гарантов введите команду /garant 

 🔍 Искали: 26{serch} раз
 💻 Проверено: 25 Апреля 2024{formatted_date}""")
                    if status == 3:
                        current_date = datetime.now()
                        month_en = current_date.strftime("%B")
                        month_ru = MONTHS_RU.get(month_en)
                        formatted_date = current_date.strftime(f"%d {month_ru} %Y")

                        cursor.execute("UPDATE users SET serch = serch + 1 WHERE user_id = ?",(user_isd,))
                        connect.commit()
                        with open("seng/stajer.jpg", "rb") as photo:
                            
                            fir_name = message.from_user.first_name
                            await message.reply_photo(
            photo=photo,  # URL или путь к файлу фотографии
            caption=f"""Информация о {user_name} [{user_isd}]
      
❓ Пользователь не официальный гарант асгард
🤫Вероятность скама 25%

🔥 Скаммеров слито: {slito}

👍 Будьте аккуратны и всегда используйте проверенных гарантов, их можно найти написав команду /garant

🔍 Искали {serch} раз
🗓 Проверено {formatted_date}""")
                    if status == 5:
                        current_date = datetime.now()
                        month_en = current_date.strftime("%B")
                        month_ru = MONTHS_RU.get(month_en)
                        formatted_date = current_date.strftime(f"%d {month_ru} %Y")
                        tags = cursor.execute("SELECT tag FROM users WHERE user_id = ?",(user_isd,)).fetchone()[0]
                        cursor.execute("UPDATE users SET serch = serch + 1 WHERE user_id = ?",(user_isd,))
                        connect.commit()
                        with open("seng/direktor.jpg", "rb") as photo:
                            
                            fir_name = message.from_user.first_name
                            await message.reply_photo(
            photo=photo,  # URL или путь к файлу фотографии
            caption=f"""Информация о {user_name} [{user_isd}]
      
❓ Пользователь является официальным директором Асгард
🤝Оригинальный юз @{tags}
Других аккаунтов не имею🌟

🔥 Скаммеров слито: {slito}

👍 Будьте аккуратны и всегда используйте проверенных гарантов, не ведитесь на обман!

🔍 Искали {serch} раз
🗓 Проверено {formatted_date}""")
                    if status == 6:
                        current_date = datetime.now()
                        month_en = current_date.strftime("%B")
                        month_ru = MONTHS_RU.get(month_en)
                        formatted_date = current_date.strftime(f"%d {month_ru} %Y")
                        tags = cursor.execute("SELECT tag FROM users WHERE user_id = ?",(user_isd,)).fetchone()[0]
                        cursor.execute("UPDATE users SET serch = serch + 1 WHERE user_id = ?",(user_isd,))
                        connect.commit()
                        with open("seng/president.jpg", "rb") as photo:
                            
                            fir_name = message.from_user.first_name
                            await message.reply_photo(
            photo=photo,  # URL или путь к файлу фотографии
            caption=f"""Информация о {user_name} [{user_isd}]
      
❓ Официальный  президент Асгард
🌟Пользователь имеет высшую должность асгард базы 

🔥Скамеров слито: {slito}

👍 Будьте аккуратны и всегда используйте проверенных гарантов, их можно найти написав команду /garant

🔍 Искали {serch} раз
🗓 Проверено {formatted_date}""")
                    if status == 7:
                        current_date = datetime.now()
                        month_en = current_date.strftime("%B")
                        month_ru = MONTHS_RU.get(month_en)
                        formatted_date = current_date.strftime(f"%d {month_ru} %Y")
                        tags = cursor.execute("SELECT tag FROM users WHERE user_id = ?",(user_isd,)).fetchone()[0]
                        cursor.execute("UPDATE users SET serch = serch + 1 WHERE user_id = ?",(user_isd,))
                        connect.commit()
                        with open("seng/admin.jpg", "rb") as photo:
                            
                            fir_name = message.from_user.first_name
                            await message.reply_photo(
            photo=photo,  # URL или путь к файлу фотографии
            caption=f"""Информация о {user_name} [{user_isd}]
      
❓ Пользователь не официальный гарант скам базы,а администратор 
Вероятность скама: 25%

🔥 Скаммеров слито: {slito}

👍 Будьте аккуратны и всегда используйте проверенных гарантов,чтобы найти гаранта напишите команду /garant 🌟

🔍 Искали {serch} раз
🗓 Проверено {formatted_date}""")
                    if status == 4:
                        current_date = datetime.now()
                        month_en = current_date.strftime("%B")
                        month_ru = MONTHS_RU.get(month_en)
                        formatted_date = current_date.strftime(f"%d {month_ru} %Y")

                        cursor.execute("UPDATE users SET serch = serch + 1 WHERE user_id = ?",(user_isd,))
                        connect.commit()
                        with open("seng/garants.jpg", "rb") as photo:
                            
                            fir_name = message.from_user.first_name
                            await message.reply_photo(
            photo=photo,  # URL или путь к файлу фотографии
            caption=f"""Информация о {user_name} [{user_isd}]
  
❓ Пользователь является официальным гарантом Асгард

🔥 Скаммеров слито: {slito}

👍 Будьте аккуратны и всегда используйте проверенных гарантов, не ведитесь на обман!

🔍 Искали {serch} раз
🗓 Проверено {formatted_date}""")
                    if status == 2:
                        current_date = datetime.now()
                        month_en = current_date.strftime("%B")
                        month_ru = MONTHS_RU.get(month_en)
                        formatted_date = current_date.strftime(f"%d {month_ru} %Y")
                        url = cursor.execute("SELECT pruf FROM users WHERE user_id = ?",(user_isd,)).fetchone()[0]
                        vero = cursor.execute("SELECT vero FROM users WHERE user_id = ?",(user_isd,)).fetchone()[0]
                        
                        prich = cursor.execute("SELECT pritc FROM users WHERE user_id = ?",(user_isd,)).fetchone()[0]
                        cursor.execute("UPDATE users SET serch = serch + 1 WHERE user_id = ?",(user_isd,))
                        connect.commit()
                        with open("seng/scam.jpg", "rb") as photo:
                            
                            fir_name = message.from_user.first_name
                            await message.reply_photo(
            photo=photo,  # URL или путь к файлу фотографии
            caption=f"""📳Информация: {user_name} 

🆔: {user_isd}
          
▫️Репутация: СКАММЕР ⚠️
▫️Вероятность скама: {vero}%
▫️Доказательства: {url}
📄 Причина: {prich}

🔥Скамеров слито: {slito}

Если вас занесли по ошибке, напишите команду "апелляция"

🔍 Искали {serch} раз
💻 Последний раз проверен {formatted_date}""")
                    if status == 0:

                        current_date = datetime.now()
                        month_en = current_date.strftime("%B")
                        month_ru = MONTHS_RU.get(month_en)
                        formatted_date = current_date.strftime(f"%d {month_ru} %Y")

                        cursor.execute("UPDATE users SET serch = serch + 1 WHERE user_id = ?",(user_isd,))
                        connect.commit()
                        with open("seng/nobase.jpg", "rb") as photo:
                            
                            fir_name = message.from_user.first_name
                            await message.reply_photo(
            photo=photo,  # URL или путь к файлу фотографии
            caption=f"""Информация о {user_name} 
 
🆔: [{user_isd}]
  
⚠️ Пользователь не является  официальным гарантом скам базы ⚠️

   ▫️ Вероятность скама: 30%

   ▫️ Скаммеров слито: {slito}
 
🕵️ Будьте бдительны и всегда используйте только проверенных гарантов 
👮чтобы увидеть список гарантов введите команду /garant 

 🔍 Искали: {serch} раз
 💻 Проверено: {formatted_date}""")

            else:
                try:
                    tag = message.text.split()[1]
                except:
                    return
                if tag.startswith('@'):
                    try:
                        tag = message.text.split()[1].replace('@','')
                        print(tag)
                    except:
                        return
                    us = cursor.execute("SELECT user_id FROM users WHERE tag = ?",(tag,)).fetchone()
                    if us is None:
                        await message.reply("Человека нету в базе\nосторожно!\n🆘🆘🆘🆘")
                    else:
                        us = us[0]
                        
                        status = cursor.execute("SELECT status FROM users WHERE tag = ?",(tag,)).fetchone()[0]
                        serch = cursor.execute("SELECT serch FROM users WHERE tag = ?",(tag,)).fetchone()[0]
                        slito = cursor.execute("SELECT slito FROM users WHERE tag = ?",(tag,)).fetchone()[0]
                        user_name = cursor.execute("SELECT user_name FROM users WHERE tag = ?",(tag,)).fetchone()[0]
                        if us in config.owner_id:
                            current_date = datetime.now()
                            month_en = current_date.strftime("%B")
                            month_ru = MONTHS_RU.get(month_en)
                            formatted_date = current_date.strftime(f"%d {month_ru} %Y")
                            tags = cursor.execute("SELECT tag FROM users WHERE tag = ?",(tag,)).fetchone()[0]
                            cursor.execute("UPDATE users SET serch = serch + 1 WHERE user_id = ?",(us,))
                            connect.commit()
                            with open("seng/sozd.jpg", "rb") as photo:
                                
                                fir_name = message.from_user.first_name
                                await message.reply_photo(
            photo=photo,  # URL или путь к файлу фотографии
            caption=f"""Информация о {user_name} [{us}]
      
❓ Официальный  создатель Асгард
🤝 Оригинальный юзернейм @{tags} других аккаунтов не имею

🔥 Скаммеров слито: {slito}

👍 Будьте аккуратны и всегда используйте проверенных гарантов, их можно найти написав команду /garant

🔍 Искали {serch} раз
🗓 Проверено {formatted_date}""")
                            return
                        if status == 1:
                            current_date = datetime.now()
                            month_en = current_date.strftime("%B")
                            month_ru = MONTHS_RU.get(month_en)
                            formatted_date = current_date.strftime(f"%d {month_ru} %Y")

                            cursor.execute("UPDATE users SET serch = serch + 1 WHERE user_id = ?",(us,))
                            connect.commit()
                            with open("seng/garant.jpg", "rb") as photo:
                                
                                fir_name = message.from_user.first_name
                                await message.reply_photo(
                photo=photo,  # URL или путь к файлу фотографии
                caption=f"""Информация о {user_name}
 
🆔: [{us}]
  
⚠️ Пользователь проверен создателем скам базы ⚠️

   ▫️ Вероятность скама: 20%

   ▫️ Скаммеров слито: {slito}
 
🕵️ Будьте бдительны и всегда используйте только проверенных гарантов 
👮чтобы увидеть список гарантов введите команду /garant 

 🔍 Искали: {serch} раз
 💻 Проверено: {formatted_date}""")
                        if status == 3:
                            current_date = datetime.now()
                            month_en = current_date.strftime("%B")
                            month_ru = MONTHS_RU.get(month_en)
                            formatted_date = current_date.strftime(f"%d {month_ru} %Y")

                            cursor.execute("UPDATE users SET serch = serch + 1 WHERE user_id = ?",(us,))
                            connect.commit()
                            with open("seng/stajer.jpg", "rb") as photo:
                                
                                fir_name = message.from_user.first_name
                                await message.reply_photo(
                photo=photo,  # URL или путь к файлу фотографии
                caption=f"""Информация о {user_name} [{us}]
          
❓ Пользователь не официальный гарант асгард
🤫Вероятность скама 25%

🔥 Скаммеров слито: {slito}

👍 Будьте аккуратны и всегда используйте проверенных гарантов, их можно найти написав команду /garant

🔍 Искали {serch} раз
🗓 Проверено {formatted_date}""")
                        if status == 5:
                            current_date = datetime.now()
                            month_en = current_date.strftime("%B")
                            month_ru = MONTHS_RU.get(month_en)
                            formatted_date = current_date.strftime(f"%d {month_ru} %Y")
                            tags = cursor.execute("SELECT tag FROM users WHERE user_id = ?",(us,)).fetchone()[0]
                            cursor.execute("UPDATE users SET serch = serch + 1 WHERE user_id = ?",(us,))
                            connect.commit()
                            with open("seng/direktor.jpg", "rb") as photo:
                                
                                fir_name = message.from_user.first_name
                                await message.reply_photo(
                photo=photo,  # URL или путь к файлу фотографии
                caption=f"""Информация о {user_name} [{us}]
          
❓ Пользователь является официальным директором Асгард
🤝Оригинальный юз @{tags}
Других аккаунтов не имею🌟

🔥 Скаммеров слито: {slito}

🔍 Искали {serch} раз
🗓 Проверено {formatted_date}""")
                        if status == 6:
                            current_date = datetime.now()
                            month_en = current_date.strftime("%B")
                            month_ru = MONTHS_RU.get(month_en)
                            formatted_date = current_date.strftime(f"%d {month_ru} %Y")
                            tags = cursor.execute("SELECT tag FROM users WHERE user_id = ?",(us,)).fetchone()[0]
                            cursor.execute("UPDATE users SET serch = serch + 1 WHERE user_id = ?",(us,))
                            connect.commit()
                            with open("seng/president.jpg", "rb") as photo:
                                
                                fir_name = message.from_user.first_name
                                await message.reply_photo(
                photo=photo,  # URL или путь к файлу фотографии
                caption=f"""Информация о {user_name} [{us}]
          
❓ Официальный  президент Асгард
🌟Пользователь имеет высшую должность асгард базы 

🔥Скамеров слито: {slito}

🔍 Искали {serch} раз
🗓 Проверено {formatted_date}""")
                        if status == 7:
                            current_date = datetime.now()
                            month_en = current_date.strftime("%B")
                            month_ru = MONTHS_RU.get(month_en)
                            formatted_date = current_date.strftime(f"%d {month_ru} %Y")
                            tags = cursor.execute("SELECT tag FROM users WHERE user_id = ?",(us,)).fetchone()[0]
                            cursor.execute("UPDATE users SET serch = serch + 1 WHERE user_id = ?",(us,))
                            connect.commit()
                            with open("seng/admin.jpg", "rb") as photo:
                                
                                fir_name = message.from_user.first_name
                                await message.reply_photo(
                photo=photo,  # URL или путь к файлу фотографии
                caption=f"""Информация о {user_name} [{us}]
          
❓ Пользователь не официальный гарант скам базы,а администратор 
Вероятность скама: 25%

🔥 Скаммеров слито: {slito}

👍 Будьте аккуратны и всегда используйте проверенных гарантов,чтобы найти гаранта напишите команду /garant 🌟

🔍 Искали {serch} раз
🗓 Проверено {formatted_date}""")
                        if status == 4:
                            current_date = datetime.now()
                            month_en = current_date.strftime("%B")
                            month_ru = MONTHS_RU.get(month_en)
                            formatted_date = current_date.strftime(f"%d {month_ru} %Y")

                            cursor.execute("UPDATE users SET serch = serch + 1 WHERE user_id = ?",(us,))
                            connect.commit()
                            with open("seng/garants.jpg", "rb") as photo:
                                
                                fir_name = message.from_user.first_name
                                await message.reply_photo(
                photo=photo,  # URL или путь к файлу фотографии
                caption=f"""Информация о {user_name} [{us}]
  
❓ Пользователь является официальным гарантом Асгард

🔥 Скаммеров слито: {slito}

👍 Будьте аккуратны и всегда используйте проверенных гарантов, не ведитесь на обман!

🔍 Искали {serch} раз
🗓 Проверено {formatted_date}""")

                        if status == 2:
                            current_date = datetime.now()
                            month_en = current_date.strftime("%B")
                            month_ru = MONTHS_RU.get(month_en)
                            formatted_date = current_date.strftime(f"%d {month_ru} %Y")
                            url = cursor.execute("SELECT pruf FROM users WHERE tag = ?",(tag,)).fetchone()[0]
                            prich = cursor.execute("SELECT pritc FROM users WHERE tag = ?",(tag,)).fetchone()[0]
                            vero = cursor.execute("SELECT vero FROM users WHERE tag = ?",(tag,)).fetchone()[0]
                            
                            cursor.execute("UPDATE users SET serch = serch + 1 WHERE user_id = ?",(us,))
                            connect.commit()
                            with open("seng/scam.jpg", "rb") as photo:
                                
                                fir_name = message.from_user.first_name
                                await message.reply_photo(
                photo=photo,  # URL или путь к файлу фотографии
                caption=f"""📳Информация: {user_name} 

🆔: {us}
          
▫️Репутация: СКАММЕР ⚠️
▫️Вероятность скама: {vero}%
▫️Доказательства: {url}
📄 Причина: {prich}

🔥Скамеров слито: {slito}

Если вас занесли по ошибке, напишите команду "апелляция"

🔍 Искали {serch} раз
💻 Последний раз проверен {formatted_date}""")
                        if status == 0:

                            current_date = datetime.now()
                            month_en = current_date.strftime("%B")
                            month_ru = MONTHS_RU.get(month_en)
                            formatted_date = current_date.strftime(f"%d {month_ru} %Y")

                            cursor.execute("UPDATE users SET serch = serch + 1 WHERE user_id = ?",(us,))
                            connect.commit()
                            with open("seng/nobase.jpg", "rb") as photo:
                                
                                fir_name = message.from_user.first_name
                                await message.reply_photo(
                photo=photo,  # URL или путь к файлу фотографии
                caption=f"""Информация о {user_name}
 
🆔: [{us}]
  
⚠️ Пользователь не является  официальным гарантом скам базы ⚠️

   ▫️ Вероятность скама: 30%

   ▫️ Скаммеров слито: {slito}
 
🕵️ Будьте бдительны и всегда используйте только проверенных гарантов 
👮чтобы увидеть список гарантов введите команду /garant 

 🔍 Искали: {serch} раз
 💻 Проверено: {formatted_date}""")
                
                else:
                    try:
                        user_isd = int(message.text.split()[1])
                    except:
                        return
                    
                    us = us[0]
                    try:
                        status = cursor.execute("SELECT status FROM users WHERE user_id = ?",(user_isd,)).fetchone()[0]
                    except:
                        await message.reply("""Человека нету в базе
осторожно!
🆘🆘🆘🆘""")
                        return
                    serch = cursor.execute("SELECT serch FROM users WHERE user_id = ?",(user_isd,)).fetchone()[0]
                    slito = cursor.execute("SELECT slito FROM users WHERE user_id = ?",(user_isd,)).fetchone()[0]
                    user_name = cursor.execute("SELECT user_name FROM users WHERE user_id = ?",(user_isd,)).fetchone()[0]
                    if int(user_isd) in config.owner_id:
                        current_date = datetime.now()
                        month_en = current_date.strftime("%B")
                        month_ru = MONTHS_RU.get(month_en)
                        formatted_date = current_date.strftime(f"%d {month_ru} %Y")
                        tags = cursor.execute("SELECT tag FROM users WHERE user_id = ?",(user_isd,)).fetchone()[0]
                        cursor.execute("UPDATE users SET serch = serch + 1 WHERE user_id = ?",(user_isd,))
                        connect.commit()
                        with open("seng/sozd.jpg", "rb") as photo:
                            
                            fir_name = message.from_user.first_name
                            await message.reply_photo(
            photo=photo,  # URL или путь к файлу фотографии
            caption=f"""Информация о {user_name} [{user_isd}]
      
❓ Официальный  создатель Асгард
🤝 Оригинальный юзернейм @{tags} других аккаунтов не имею

🔥 Скаммеров слито: {slito}

👍 Будьте аккуратны и всегда используйте проверенных гарантов, их можно найти написав команду /garant

🔍 Искали {serch} раз
🗓 Проверено {formatted_date}""")
                        return
                    if status == 1:
                        current_date = datetime.now()
                        month_en = current_date.strftime("%B")
                        month_ru = MONTHS_RU.get(month_en)
                        formatted_date = current_date.strftime(f"%d {month_ru} %Y")

                        cursor.execute("UPDATE users SET serch = serch + 1 WHERE user_id = ?",(user_isd,))
                        connect.commit()
                        with open("seng/garant.jpg", "rb") as photo:
                            
                            fir_name = message.from_user.first_name
                            await message.reply_photo(
            photo=photo,  # URL или путь к файлу фотографии
            caption=f"""Информация о {user_name}
 
🆔: [{user_isd}]
  
⚠️ Пользователь проверен создателем скам базы ⚠️

   ▫️ Вероятность скама: 20%

   ▫️ Скаммеров слито: 0{slito}
 
🕵️ Будьте бдительны и всегда используйте только проверенных гарантов 
👮чтобы увидеть список гарантов введите команду /garant 

 🔍 Искали: {serch} раз
 💻 Проверено: {formatted_date}""")
                    if status == 3:
                        current_date = datetime.now()
                        month_en = current_date.strftime("%B")
                        month_ru = MONTHS_RU.get(month_en)
                        formatted_date = current_date.strftime(f"%d {month_ru} %Y")

                        cursor.execute("UPDATE users SET serch = serch + 1 WHERE user_id = ?",(user_isd,))
                        connect.commit()
                        with open("seng/stajer.jpg", "rb") as photo:
                            
                            fir_name = message.from_user.first_name
                            await message.reply_photo(
            photo=photo,  # URL или путь к файлу фотографии
            caption=f"""Информация о {user_name} [{user_isd}]
      
❓ Пользователь не официальный гарант асгард
🤫Вероятность скама 25%

🔥 Скаммеров слито: {slito}

👍 Будьте аккуратны и всегда используйте проверенных гарантов, их можно найти написав команду /garant

🔍 Искали {serch} раз
🗓 Проверено {formatted_date}""")
                    if status == 5:
                        current_date = datetime.now()
                        month_en = current_date.strftime("%B")
                        month_ru = MONTHS_RU.get(month_en)
                        formatted_date = current_date.strftime(f"%d {month_ru} %Y")
                        tags = cursor.execute("SELECT tag FROM users WHERE user_id = ?",(user_isd,)).fetchone()[0]
                        cursor.execute("UPDATE users SET serch = serch + 1 WHERE user_id = ?",(user_isd,))
                        connect.commit()
                        with open("seng/direktor.jpg", "rb") as photo:
                            
                            fir_name = message.from_user.first_name
                            await message.reply_photo(
            photo=photo,  # URL или путь к файлу фотографии
            caption=f"""Информация о {user_name} [{user_isd}]
      
❓ Пользователь является официальным директором Асгард
🤝Оригинальный юз @{tags}
Других аккаунтов не имею🌟

🔥 Скаммеров слито: {slito}

👍 Будьте аккуратны и всегда используйте проверенных гарантов, не ведитесь на обман!

🔍 Искали {serch} раз
🗓 Проверено {formatted_date}""")
                    if status == 6:
                        current_date = datetime.now()
                        month_en = current_date.strftime("%B")
                        month_ru = MONTHS_RU.get(month_en)
                        formatted_date = current_date.strftime(f"%d {month_ru} %Y")
                        tags = cursor.execute("SELECT tag FROM users WHERE user_id = ?",(user_isd,)).fetchone()[0]
                        cursor.execute("UPDATE users SET serch = serch + 1 WHERE user_id = ?",(user_isd,))
                        connect.commit()
                        with open("seng/president.jpg", "rb") as photo:
                            
                            fir_name = message.from_user.first_name
                            await message.reply_photo(
            photo=photo,  # URL или путь к файлу фотографии
            caption=f"""Информация о {user_name} [{user_isd}]
      
❓ Официальный  президент Асгард
🌟Пользователь имеет высшую должность асгард базы 

🔥Скамеров слито: {slito}

👍 Будьте аккуратны и всегда используйте проверенных гарантов, их можно найти написав команду /garant

🔍 Искали {serch} раз
🗓 Проверено {formatted_date}""")
                    if status == 7:
                        current_date = datetime.now()
                        month_en = current_date.strftime("%B")
                        month_ru = MONTHS_RU.get(month_en)
                        formatted_date = current_date.strftime(f"%d {month_ru} %Y")
                        tags = cursor.execute("SELECT tag FROM users WHERE user_id = ?",(user_isd,)).fetchone()[0]
                        cursor.execute("UPDATE users SET serch = serch + 1 WHERE user_id = ?",(user_isd,))
                        connect.commit()
                        with open("seng/admin.jpg", "rb") as photo:
                            
                            fir_name = message.from_user.first_name
                            await message.reply_photo(
            photo=photo,  # URL или путь к файлу фотографии
            caption=f"""Информация о {user_name} [{user_isd}]
      
❓ Пользователь не официальный гарант скам базы,а администратор 
Вероятность скама: 25%

🔥 Скаммеров слито: {slito}

👍 Будьте аккуратны и всегда используйте проверенных гарантов,чтобы найти гаранта напишите команду /garant 🌟

🔍 Искали {serch} раз
🗓 Проверено {formatted_date}""")
                    if status == 4:
                        current_date = datetime.now()
                        month_en = current_date.strftime("%B")
                        month_ru = MONTHS_RU.get(month_en)
                        formatted_date = current_date.strftime(f"%d {month_ru} %Y")

                        cursor.execute("UPDATE users SET serch = serch + 1 WHERE user_id = ?",(user_isd,))
                        connect.commit()
                        with open("seng/garants.jpg", "rb") as photo:
                            
                            fir_name = message.from_user.first_name
                            await message.reply_photo(
            photo=photo,  # URL или путь к файлу фотографии
            caption=f"""Информация о {user_name} [{user_isd}]
  
❓ Пользователь является официальным гарантом Асгард

🔥 Скаммеров слито: {slito}

👍 Будьте аккуратны и всегда используйте проверенных гарантов, не ведитесь на обман!

🔍 Искали {serch} раз
🗓 Проверено {formatted_date}""")
                    if status == 2:
                        current_date = datetime.now()
                        month_en = current_date.strftime("%B")
                        month_ru = MONTHS_RU.get(month_en)
                        formatted_date = current_date.strftime(f"%d {month_ru} %Y")
                        vero = cursor.execute("SELECT vero FROM users WHERE user_id = ?",(user_isd,)).fetchone()[0]
                        url = cursor.execute("SELECT pruf FROM users WHERE user_id = ?",(user_isd,)).fetchone()[0]

                        cursor.execute("UPDATE users SET serch = serch + 1 WHERE user_id = ?",(user_isd,))
                        prich = cursor.execute("SELECT pritc FROM users WHERE user_id = ?",(user_isd,)).fetchone()[0]
                        connect.commit()
                        with open("seng/scam.jpg", "rb") as photo:
                            
                            fir_name = message.from_user.first_name
                            await message.reply_photo(
            photo=photo,  # URL или путь к файлу фотографии
            caption=f"""📳Информация: {user_name} 

🆔: {user_isd}
          
▫️Репутация: СКАММЕР ⚠️
▫️Вероятность скама: {vero}%
▫️Доказательства: {url}
📄 Причина: {prich}

🔥Скамеров слито: {slito}

Если вас занесли по ошибке, напишите команду "апелляция"

🔍 Искали {serch} раз
💻 Последний раз проверен {formatted_date}""")
                    if status == 0:

                        current_date = datetime.now()
                        month_en = current_date.strftime("%B")
                        month_ru = MONTHS_RU.get(month_en)
                        formatted_date = current_date.strftime(f"%d {month_ru} %Y")

                        cursor.execute("UPDATE users SET serch = serch + 1 WHERE user_id = ?",(user_isd,))
                        connect.commit()
                        with open("seng/nobase.jpg", "rb") as photo:
                            
                            fir_name = message.from_user.first_name
                            await message.reply_photo(
            photo=photo,  # URL или путь к файлу фотографии
            caption=f"""Информация о {user_name} 
 
🆔: [{user_isd}]
  
⚠️ Пользователь не является  официальным гарантом скам базы ⚠️

   ▫️ Вероятность скама: 30%

   ▫️ Скаммеров слито: {slito}
 
🕵️ Будьте бдительны и всегда используйте только проверенных гарантов 
👮чтобы увидеть список гарантов введите команду /garant 

 🔍 Искали: {serch} раз
 💻 Проверено: {formatted_date}""")
    connect.commit()



async def get_datetime(text: str):
    days, hours, minutes = timedelta(seconds=0), timedelta(seconds=0), timedelta(seconds=0)

    if 'д' in text or 'd' in text:
        if 'д' in text:
            xd = text.split('д')[0]
        else:
            xd = text.split('d')[0]
        if len(xd.split()) == 1:
            xd = xd.split()[0]
        else:
            xd = xd.split()[1]
        days = timedelta(days=int(xd))
    if 'м' in text or 'm' in text:
        if 'м' in text:
            xd = text.split('м')[0]
        else:
            xd = text.split('m')[0]

        if len(xd.split()) == 1:
            xd = xd.split()[0]
        else:
            xd = xd.split()[1]
        minutes = timedelta(minutes=int(xd))
    if 'ч' in text or 'h' in text:
        if 'h' in text:
            xd = text.split('h')[0]
        else:
            xd = text.split('ч')[0]
        if len(xd.split()) == 1:
            xd = xd.split()[0]
        else:
            xd = xd.split()[1]
        hours = timedelta(hours=int(xd))

    result = days + hours + minutes
    return result if result.total_seconds() > 30 else None
unmute_perms = ChatPermissions(
    can_send_messages=True,
    can_send_media_messages=False,
    can_send_polls=False,
    can_send_other_messages=True,
    can_add_web_page_previews=True,
    can_invite_users=True,
)
mute_perms = ChatPermissions(
    can_send_messages=False,
    can_send_media_messages=False,
    can_send_polls=False,
    can_send_other_messages=False,
    can_add_web_page_previews=False,
    can_change_info=False,
    can_invite_users=False,
    can_pin_messages=False
)

@dp.callback_query_handler(lambda c: c.data.startswith('no_'))
async def process_callback(callback_query: types.CallbackQuery):
    # Замените этот ID на ID вашего счета
    callback_data = callback_query.data
    invoice_id = callback_data.split('_')[1]
    user_id = callback_query.from_user.id
    status = cursor.execute("SELECT status FROM users WHERE user_id = ?",(user_id,)).fetchone()[0]
    if status == 5 or user_id in config.owner_id:
        al = cursor.execute("SELECT * FROM prover WHERE id = ?",(invoice_id,)).fetchone()
        cursor.execute('DELETE FROM prover WHERE id=?', (al[0],))
        connect.commit()    
        await callback_query.message.edit_text("Вы успешно отклонили")
@dp.callback_query_handler(lambda c: c.data.startswith('yes_'))
async def process_callback(callback_query: types.CallbackQuery):
    # Замените этот ID на ID вашего счета
    callback_data = callback_query.data
    invoice_id = callback_data.split('_')[1]
    user_id = callback_query.from_user.id
    status = cursor.execute("SELECT status FROM users WHERE user_id = ?",(user_id,)).fetchone()[0]
    if status == 5 or user_id in config.owner_id:
        al = cursor.execute("SELECT * FROM prover WHERE id = ?",(invoice_id,)).fetchone()
        cursor.execute("UPDATE users SET admin_balance = admin_balance + 1 WHERE user_id = ?",(al[1],))
        cursor.execute("UPDATE users SET status = 2 WHERE user_id = ?",(al[2],))
        cursor.execute("UPDATE users SET pruf = ? WHERE user_id = ?",(al[3],al[2],))
        cursor.execute("UPDATE users SET pritc = ? WHERE user_id = ?",(al[5],al[2],))
        cursor.execute("UPDATE users SET vero = ? WHERE user_id = ?",(al[4],al[2],))
        cursor.execute('DELETE FROM prover WHERE id=?', (al[0],))
        connect.commit()    
        await callback_query.message.edit_text("Вы успешно приняли")




async def bakcup():
    database_path= "data.db"
    backup_folder = "backup"
    # Проверяем, существует ли папка для бэкапов, если нет, то создаем её
    if not os.path.exists(backup_folder):
        os.makedirs(backup_folder)
    
    # Получаем текущую дату и время
    current_datetime = datetime.now()
    
    # Генерируем имя файла с учетом даты и времени
    backup_filename = f"data_{current_datetime.strftime('%Y-%m-%d_%H-%M-%S')}.db"
    
    # Полный путь к файлу базы данных и копии
    database_full_path = os.path.abspath(database_path)
    backup_full_path = os.path.join(backup_folder, backup_filename)
    
    # Копируем файл базы данных
    shutil.copy2(database_full_path, backup_full_path)
def schedule2r():
    scheduler.add_job(bakcup,'interval', hours=1)

async def on_startup(_):
    #dp.middleware.setup(ThrottlingMiddleware())
    schedule2r()



if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True,on_startup=on_startup)
