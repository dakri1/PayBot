from aiogram import Bot, Dispatcher
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, FSInputFile
import asyncio
from datetime import datetime, timedelta
from yoomoney import Client, Quickpay
from database import DataBase
import string
import random
import os
from dotenv import load_dotenv
from excel import generate_excel

text = ""
cost, cost_week, cost_sale, cost_sale_week = 0, 0, 0, 0
load_dotenv()
admins = [1290725432, 898792301, 5494679643, 727439347]
# .ENV САМ СДЕЛАЙ, сам свой токен телеграм бота сделай и вставь туда
token = os.getenv("PAY_TOKEN")
bot_token = os.getenv("TOKEN")
id_group = os.getenv("GROUP_ID")
db = DataBase()

dp = Dispatcher()
client = Client(token)
bot = Bot(bot_token)


class AdminPanel(StatesGroup):
    price = State()
    text = State()
    invite_link = State()


async def generate_url_for_pay(rand_string, cost):
    quickpay = Quickpay(
        receiver='410019860369454',
        quickpay_form='shop',
        targets='Test',
        paymentType='SB',
        sum=cost,
        label=rand_string
    )
    return quickpay.redirected_url


async def rassylka():
    users = await db.get_users()
    try:
        for user in users:
            if user[2] == 0:
                await bot.send_message(user[1], text)
    except:
        pass


@dp.callback_query()
async def oplata(callback: CallbackQuery, state: FSMContext):
    if callback.data == "change_cost":
        ib1 = InlineKeyboardButton(text="Отмена", callback_data="stop")
        ikb = InlineKeyboardMarkup(inline_keyboard=[[ib1]])
        await bot.send_message(callback.message.chat.id, """Чтобы изменить цену, введи новую цену, но перед ней введи цифру
        1.Поменять цену за месяц
        2.Поменять цену за неделю
        3.Поменять цену за месяц(скидка)
        4.Поменять цену за неделю(скидка)
        Пример: 2 239
        """, reply_markup=ikb)
        await state.set_state(AdminPanel.price)
        await callback.answer()
    elif callback.data == "stop":
        await state.clear()
        await callback.answer("Отменено")
    elif callback.data == "check_rassylka":
        if text == "":
            await bot.send_message(callback.message.chat.id, "Текст пустой, такое разослать не получится")
        else:
            ib1 = InlineKeyboardButton(text="Подтвердить", callback_data="rassylka")
            ikb = InlineKeyboardMarkup(inline_keyboard=[[ib1]])
            await bot.send_message(callback.message.chat.id,
                                   f"Нажми подтвердить, чтобы отправилась рассылка с таким текстом: {text}",
                                   parse_mode='HTML', reply_markup=ikb)
            await callback.answer()
    elif callback.data == "rassylka":
        if text == "":
            await bot.send_message(callback.message.chat.id, "Текст пустой, такое разослать не получится")
        else:
            await callback.answer("Рассылка запущена")
            await rassylka()
            await callback.answer()
    elif callback.data == "text":
        await bot.send_message(callback.message.chat.id, "Введи новый текст")
        await state.set_state(AdminPanel.text)
        await callback.answer()
    elif callback.data == "get_table":
        await generate_excel()
        await bot.send_document(callback.message.chat.id, FSInputFile('users.xlsx'))
        await callback.answer()
    elif callback.data == "get_price":
        ib4 = InlineKeyboardButton(text="Месяц", callback_data="cost1")
        ib5 = InlineKeyboardButton(text="Неделя", callback_data="cost2")
        ib6 = InlineKeyboardButton(text="Скидка Месяц", callback_data="cost3")
        ib7 = InlineKeyboardButton(text="Скидка Неделя", callback_data="cost4")
        ikb = InlineKeyboardMarkup(inline_keyboard=[[ib5, ib6], [ib7, ib4]])
        await bot.send_message(callback.message.chat.id, "Какую цену хочешь узнать", reply_markup=ikb)
        await callback.answer()
    elif callback.data[:4] == "cost":
        c = callback.data
        if c[-1] == "1": await callback.answer(str(await db.get_cost()))
        elif c[-1] == "2": await callback.answer(str(await db.get_cost_week()))
        elif c[-1] == "3": await callback.answer(str(await db.get_cost_sale()))
        elif c[-1] == "4": await callback.answer(str(await db.get_cost_sale_week()))
    elif callback.data == "get_text":
        if text != "":
            await bot.send_message(callback.message.chat.id, text, parse_mode='HTML')
        else:
            await bot.send_message(callback.message.chat.id, "Текст в данный момент пустой", parse_mode='HTML')
        await callback.answer()
    elif callback.data == "oplata":
        label_month = await db.get_label_month(callback.message.chat.id)
        label_week = await db.get_label_week(callback.message.chat.id)
        url = ""
        if await db.get_last_day(callback.message.chat.id):
            c_month = cost_sale
            c_week = cost_sale_week

        else:
            c_month = cost
            c_week = cost_week
        if label_month == '1':
            new_label_month = await generate_label()
            new_label_week = await generate_label()
            await db.update_label(new_label_month, new_label_week, callback.message.chat.id)

            url_week = await generate_url_for_pay(new_label_week, c_week)
            url_month = await generate_url_for_pay(new_label_month, c_month)
        else:
            url_month = await generate_url_for_pay(label_month, c_month)
            url_week = await generate_url_for_pay(label_week, c_week)
        ib1 = InlineKeyboardButton(text="Проверить платеж", callback_data="check")
        ib2 = InlineKeyboardButton(text="Оплатить месяц", url=url_month)
        ib3 = InlineKeyboardButton(text="Оплатить неделю", url=url_week)
        ikb = InlineKeyboardMarkup(inline_keyboard=[[ib2, ib3], [ib1]])

        await bot.send_message(callback.message.chat.id,
                               "Ожидание оплаты. После оплаты нажмите на кнопку \"Проверить платеж\".",
                               reply_markup=ikb)
        await callback.answer()

    elif callback.data == "invite_link":
        await inviteUser(callback.message.chat.id)
        await callback.answer()

    elif callback.data == "extend":
        data = await db.get_payment_status(callback.message.chat.id)
        bought = data[0][0]
        labels = [data[0][1], data[0][2]]
        # Сначало идет месяц
        days = [3, 2]
        last_day = data[0][3]
        for i in range(len(labels)):
            if bought == 1 and last_day:
                label = labels[i]
                day = days[i]
                client = Client(token)
                history = client.operation_history(label=label)
                try:
                    operation = history.operations[-1]
                    if operation.status == 'success':
                        await db.set_new_podpiska_end(
                            user_id=callback.message.chat.id, days=day
                        )
                        await db.set_last_day(False, callback.message.chat.id)
                        await callback.answer("Оплата прошла")
                        await callback.message.delete()
                        break
                except Exception as e:
                    if i == len(labels) - 1:
                        await callback.answer("Оплата в пути")

    elif callback.data == "check":
        data = await db.get_payment_status(callback.message.chat.id)
        if not data:
            await db.add_user(callback.message.chat.id)
            data = await db.get_payment_status(callback.message.chat.id)
        bought = data[0][0]
        labels = [data[0][1], data[0][2]]
        days = [3, 2]
        if bought == 0:
            client = Client(token)
            for i in range(len(labels)):
                label = labels[i]
                day = days[i]
                history = client.operation_history(label=label)
                try:
                    operation = history.operations[-1]
                    if operation.status == 'success':
                        await db.update_payment_status(True, callback.message.chat.id, day)
                        await inviteUser(callback.message.chat.id)
                        await bot.unban_chat_member(id_group, callback.message.chat.id)
                        await callback.answer("Оплата прошла")
                        await callback.message.delete()
                        break
                except Exception as e:
                    if i == len(labels) - 1:
                        await callback.answer("Оплата в пути")
        else:
            await callback.answer("Вы уже оплатили")
    return


async def generate_label():
    letters_and_digits = string.ascii_lowercase + string.digits
    rand_string = ''.join(random.sample(letters_and_digits, 10))
    return rand_string


async def my_periodic_task():
    while True:
        try:
            await asyncio.sleep(30)
            data = await db.get_subscribe_status()
            if not data:
                pass
            else:
                for i in range(len(data)):

                    if data[i][1] is not None and data[i][3]:
                        date = datetime.strptime(data[i][2], "%Y-%m-%d %H:%M:%S.%f")
                        user_id = data[i][0]
                        if (date - datetime.now()) <= timedelta(minutes=1):
                            if not await db.get_last_day(user_id):
                                await db.set_last_day(True, user_id)
                                label_month = await generate_label()
                                label_week = await generate_label()
                                await db.update_label(label_month, label_week, user_id)
                                ib1 = InlineKeyboardButton(text="Проверить платеж", callback_data="extend")
                                ib2 = InlineKeyboardButton(text="Продлить месяц",
                                                           url=await generate_url_for_pay(label_month, cost_sale))
                                ib3 = InlineKeyboardButton(text="Продлить неделю",
                                                           url=await generate_url_for_pay(label_week, cost_sale_week))
                                ikb = InlineKeyboardMarkup(inline_keyboard=[[ib2, ib3], [ib1]])
                                await bot.send_message(user_id,
                                                       "Срок вашей подписки подходит к концу. Продление подписки составит всего 149 рублей! Успейте продлить по низкой цене, иначе она вернётся к 199 рублям.",
                                                       reply_markup=ikb)
                        if datetime.now() > date:
                            await db.set_last_day(False, user_id)
                            label_month = await generate_label()
                            label_week = await generate_label()
                            await db.update_label_bought(label_month, label_week, user_id, False)
                            await bot.ban_chat_member(id_group, user_id)
                            ib1 = InlineKeyboardButton(text="Проверить платеж", callback_data="check")
                            ib2 = InlineKeyboardButton(text="Оплатить месяц",
                                                       url=await generate_url_for_pay(label_month, cost))
                            ib3 = InlineKeyboardButton(text="Оплатить неделю",
                                                       url=await generate_url_for_pay(label_week, cost_week))
                            ikb = InlineKeyboardMarkup(inline_keyboard=[[ib2, ib3], [ib1]])
                            await bot.send_message(user_id,
                                                   "Срок вашей подписки истек, чтобы ее продлить, совершите оплату по новой ссылке, нажав на кнопку Оплатить",
                                                   reply_markup=ikb)
                        await asyncio.sleep(2)
                    else:
                        await asyncio.sleep(2)
                        continue


        except Exception as e:
            pass


async def inviteUser(user_id):
    link = await bot.create_chat_invite_link(chat_id=id_group, member_limit=1)
    try:
        await bot.send_message(user_id, f"Твоя уникальная ссылка: {link.invite_link}")
    except:
        pass


@dp.message(Command('admin'))
async def get_excel(message: Message):
    if message.chat.id in admins:
        ib1 = InlineKeyboardButton(text="Получить таблицу", callback_data="get_table")
        ib2 = InlineKeyboardButton(text="Узнать текущую цену", callback_data="get_price")
        ib3 = InlineKeyboardButton(text="Показать загруженный текст", callback_data="get_text")
        ib4 = InlineKeyboardButton(text="Изменить цену", callback_data="change_cost")
        ib5 = InlineKeyboardButton(text="Отправить рассылку", callback_data="check_rassylka")
        ib6 = InlineKeyboardButton(text="Ввести новый текст", callback_data="text")
        ib7 = InlineKeyboardButton(text="Сгенерироваить invite-ссылку", callback_data="invite_link")
        ikb = InlineKeyboardMarkup(inline_keyboard=[[ib1, ib2], [ib3, ib4], [ib5, ib6], [ib7]])
        await bot.send_message(message.chat.id, "Добро пожаловать в админку", reply_markup=ikb)
    else:
        print(message.chat.id, admins)


@dp.message(Command('start'))
async def p2p_buy(message: Message):
    ib1 = InlineKeyboardButton(text="💥Купить💥", callback_data="oplata")
    ib2 = InlineKeyboardButton(text="Связаться с админом", url="t.me/srpscorpe")
    ikb = InlineKeyboardMarkup(inline_keyboard=[[ib1], [ib2]])
    try:
        await db.add_user(message.chat.id)
    except Exception as e:
        pass
    finally:
        await bot.send_message(chat_id=message.from_user.id, text="""💰 Привет, ты попал на страницу оплаты приватки паков с отзывов.
🔥 Для продолжения покупки нажми на кнопку снизу

Кнопка связи с админом перенаправляет на аккаунт @angularv""", reply_markup=ikb)


@dp.message(AdminPanel.price)
async def get_price(message: Message, state: FSMContext):
    global cost, cost_week, cost_sale, cost_sale_week
    try:
        ms = message.text
        m = message.text.split()
        c = m[1]
        if m[0] == "1":
            await db.set_cost(int(c))
            cost = int(c)
        elif m[0] == "2":
            await db.set_cost_week(int(c))
            cost_week = int(c)
        elif m[0] == "3":
            await db.set_sale_cost_month(int(c))
            cost_sale = int(c)
        elif m[0] == "4":
            await db.set_sale_cost_week(int(c))
            cost_sale_week = int(c)
        ib1 = InlineKeyboardButton(text="Рассылка", callback_data="check_rassylka")
        ib2 = InlineKeyboardButton(text="Текст", callback_data="text")
        ikb = InlineKeyboardMarkup(inline_keyboard=[[ib1, ib2]])
        await bot.send_message(message.chat.id, f"Цена успешно изменена на {c}."
                                                f" Чтобы отправить рассылку с новой ценой нажми Рассылка."
                                                f" Если хочешь изменить текст для рассылки нажми Текст",
                               reply_markup=ikb)
    except:
        await bot.send_message(message.chat.id, "Это точно число?(Чтобы еще раз отправить, нажми Ввести цену)")
    await state.clear()


@dp.message(AdminPanel.text)
async def get_text(message: Message, state: FSMContext):
    global text
    try:
        text = message.text
        ib1 = InlineKeyboardButton(text="Рассылка", callback_data="check_rassylka")
        ib2 = InlineKeyboardButton(text="Ввести цену", callback_data="change_cost")
        ikb = InlineKeyboardMarkup(inline_keyboard=[[ib1, ib2]])
        await bot.send_message(message.chat.id, f"Текст успешно загружен."
                                                f" Чтобы отправить рассылку с этим текстом нажми Рассылка."
                                                f" Если хочешь изменить цену нажми Ввести цену", reply_markup=ikb)
    except:
        await bot.send_message(message.chat.id, "Не получилось обработать текст")
    await state.clear()


async def main() -> None:
    global cost, cost_week, cost_sale, cost_sale_week
    cost = await db.get_cost()
    cost_week = await db.get_cost_week()
    cost_sale_week = await db.get_cost_sale_week()
    cost_sale = await db.get_cost_sale()
    asyncio.create_task(my_periodic_task())
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
