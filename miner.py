import random
import asyncio
import psycopg2
from aiogram.types import Message, CallbackQuery
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup

def add_new_user(user_id: str) -> None:
    con = psycopg2.connect(dbname='postgres', user='postgres', password='1', host='localhost', port='5432')
    cursor = con.cursor()
    try:
        insert_query = """INSERT INTO miner(id, balance, win, lose, stavka, map, my_map, upend, lobby_player, game_mode) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        cursor.execute(insert_query,
                       (user_id, 100, 0, 0, 0, '1111111111111111111111111', '1111111111111111111111111', 1, "menu", ""))
        con.commit()
    except:
        print("Ошибка добавления пользователя")
    cursor.close()
    con.close()


def payme(user_id: str, pay: int) -> None:
    balance = get_table_info(user_id)[0][1]
    con = psycopg2.connect(dbname='postgres', user='postgres', password='1', host='localhost', port='5432')
    cursor = con.cursor()
    cursor.execute("""UPDATE miner SET balance= %s WHERE id=%s""",
                   (balance + pay, user_id))
    con.commit()
    cursor.close()
    con.close()


def stavka_table(user_id: int, stavka: int) -> None:
    con = psycopg2.connect(dbname='postgres', user='postgres', password='1', host='localhost', port='5432')
    cursor = con.cursor()
    try:
        cursor.execute(""" UPDATE miner SET stavka= %s WHERE id=%s""",
                       (stavka, user_id))
        con.commit()
    except:
        print("Ошибка изменения записи")
    cursor.close()
    con.close()


def get_table_info(user_id: int) -> list:
    id = []
    con = psycopg2.connect(dbname='postgres', user='postgres', password='1', host='localhost', port='5432')
    cursor = con.cursor()
    cursor.execute("""SELECT id FROM miner""")
    cus = cursor.fetchall()
    for i in cus:
        id.append(i[0])
    if user_id in id:
        cursor.execute("""SELECT * from miner where id = %s and id = %s""",
                       (user_id, user_id))
        record = cursor.fetchall()
        return record
    cursor.close()
    con.close()
    add_new_user(user_id)
    con = psycopg2.connect(dbname='postgres', user='postgres', password='1', host='localhost', port='5432')
    cursor = con.cursor()
    cursor.execute("""SELECT * from miner where id = %s and id = %s""",
                   (user_id, user_id))
    record = cursor.fetchall()
    cursor.close()
    con.close()
    return record


def update_table(user_id: int, lobby_player: str, game_mode: str, game_map: str = '111',
                 my_map: str = '1111111111111111111111111', pay: int = 0, win: str = 0,
                 lose: int = 0, stavka: int = 0, upper: int = 1) -> None:
    info = get_table_info(user_id)[0]
    try:
        con = psycopg2.connect(dbname='postgres', user='postgres', password='1', host='localhost', port='5432')
    except:
        print("Ошибка подключения к базе данных")
        exit()
    cursor = con.cursor()
    try:
        cursor.execute(
            """ UPDATE miner SET balance= %s, win= %s, lose= %s, stavka= %s, map= %s, my_map= %s, upend= %s, lobby_player= %s, game_mode= %s WHERE id=%s""",
            (float(info[1]) + pay, info[2] + win, info[3] + lose, stavka, game_map, my_map, upper, lobby_player,
             game_mode, user_id))
        con.commit()
    except:
        print("Ошибка изменения записи")
    cursor.close()  # закрываем курсор
    con.close()  # закрываем соединение


def check_choise(user_id: int, player_choice: int) -> int:
    table_map = ''
    mode = {'5 min': 1.20,
            '7 min': 1.35,
            '10 min': 1.40}
    info = get_table_info(user_id)[0]
    upper = info[7]
    my_map = get_table_my_map(info[6])
    if player_choice in range(25):
        if info[5][player_choice] == '1' and info[6][player_choice] != '3':
            my_map[player_choice] = '3'
            for i in my_map:
                table_map += i
            upper = float(upper) * mode[info[9]]
            update_table(info[0], info[8], info[9], game_map=info[5], stavka=info[4], upper=upper, my_map=table_map)
            return 3
        elif info[5][player_choice] == '2':
            return 2
        elif info[6][player_choice] == '3':
            return 1
    else:
        return 0


def create_game_map(choise: int) -> str:
    play = {5: [2, 1, 1, 1, 1, 2, 1, 1, 1, 1, 2, 1, 1, 1, 1, 2, 1, 1, 1, 1, 2, 1, 1, 1, 1],
            7: [2, 1, 1, 1, 1, 2, 1, 2, 1, 1, 2, 1, 1, 1, 1, 2, 1, 2, 1, 1, 2, 1, 1, 1, 1],
            10: [2, 1, 2, 1, 1, 2, 1, 2, 1, 1, 2, 1, 1, 1, 1, 2, 1, 2, 1, 1, 2, 1, 2, 1, 2]}
    answer = play[choise]
    map = ''
    random.shuffle(answer)
    random.shuffle(answer)
    for i in answer:
        map += str(i)
    return map


def print_game_map(map: str):
    maping = {'1': "⬛️", '3': "💲"}
    keyboard = InlineKeyboardBuilder()
    for i in range(25):
        keyboard.add(InlineKeyboardButton(text=maping[map[int(i)]], callback_data=str(i)))
    keyboard.add(InlineKeyboardButton(text="Забрать", callback_data="take"))
    return keyboard.adjust(5).as_markup()

def get_table_my_map(map: str) -> list:
    answer = []
    for i in map:
        answer.append(i)
    return answer

kb_menu = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Играть", callback_data="play")],
                                        [InlineKeyboardButton(text="Баланс", callback_data="money")],
                                        [InlineKeyboardButton(text="Вывести", callback_data="get_money")],
                                        [InlineKeyboardButton(text="Пополнить баланс", callback_data="pay")]])

kb_pay = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Отмена", callback_data="menu")]])

kb_play = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="5 Мин", callback_data="5 min")],
                                               [InlineKeyboardButton(text="7 Мин", callback_data="7 min")],
                                               [InlineKeyboardButton(text="10 Мин", callback_data="10 min")],
                                               [InlineKeyboardButton(text="Отмена", callback_data="menu")]])
mode = {'5 min': 1.20,
        '7 min': 1.35,
        '10 min': 1.40}
bot = Bot(token='7742788199:AAFdbZDnds3wgpoHqPO49-McbpL-pLaBNCM')
ds = Dispatcher()

@ds.message(CommandStart())
async def start(message: Message):
    """Завершено"""
    global mode
    info = get_table_info(message.from_user.id)[0]
    if info[8] == "menu":
        await message.answer("Меню", reply_markup=kb_menu)
    elif info[8] == "pay":
        await message.answer("Введите сумму пополнения", reply_markup=kb_pay)
    elif info[8] == "stavka":
        await message.answer("Введите сумму ставки", reply_markup=kb_pay)
    elif info[8] == "play":
        await message.answer("Выберите кол-во мин", reply_markup=kb_play)
    elif info[8] == "game":
        await message.answer(f"Выйгрыш: {int(info[4])*float(info[7])} руб, Коэфицент {info[7]},След {float(info[7])*mode[info[9]]}", reply_markup=print_game_map(info[6]))
    else:
        print("Ошибка в блоке (Start)")


@ds.callback_query(F.data == "play")
async def start_game(callback: CallbackQuery):
    """Не Проверено"""
    info = get_table_info(callback.from_user.id)[0]
    update_table(info[0], "play", "")
    await callback.answer("Успешно")
    await callback.message.edit_text("Выберите кол-во мин", reply_markup=kb_play)


@ds.callback_query(F.data == "money")
async def balance(callback: CallbackQuery):
    """Закончено"""
    info = get_table_info(callback.from_user.id)[0]
    await callback.answer(f"Ваш баланс: {info[1]} рублей")

@ds.callback_query(F.data == "get_money")
async def get_money(callback: CallbackQuery):
    await callback.answer("В разработке")

@ds.callback_query(F.data == "pay")
async def pay(callback: CallbackQuery):
    """Не Проверено"""
    info = get_table_info(callback.from_user.id)[0]
    await callback.answer("Успешно")
    await callback.message.edit_text(f"Введите сумму пополнения, текущий баланс: {info[1]} рублей \n "
                                       f"(Если на балансе больше 50 к рублей пополнять нельзя)", reply_markup=kb_pay)
    update_table(info[0], "pay", "")


@ds.callback_query(F.data == "5 min")
async def game_5(callback: CallbackQuery):
    """Не проверено"""
    info = get_table_info(callback.from_user.id)[0]
    update_table(info[0], "stavka", "5 min")
    await callback.answer("Успешно")
    await callback.message.edit_text(f"Ваш баланс: {info[1]} рублей \n Выберите ставку", reply_markup=kb_pay)

@ds.callback_query(F.data == "7 min")
async def game_7(callback: CallbackQuery):
    """Не проверено"""
    info = get_table_info(callback.from_user.id)[0]
    update_table(info[0], "stavka", "7 min")
    await callback.answer("Успешно")
    await callback.message.edit_text(f"Ваш баланс: {info[1]} рублей \n Выберите ставку", reply_markup=kb_pay)

@ds.callback_query(F.data == "10 min")
async def game_10(callback: CallbackQuery):
    """Не проверено"""
    info = get_table_info(callback.from_user.id)[0]
    update_table(info[0], "stavka", "10 min")
    await callback.answer("Успешно")
    await callback.message.edit_text(f"Ваш баланс: {info[1]} рублей \n Выберите ставку", reply_markup=kb_pay)


@ds.callback_query(F.data == "menu")
async def pay_close(callback: CallbackQuery):
    """Не проверено"""
    info = get_table_info(callback.from_user.id)[0]
    if info[8] == "pay":
        update_table(info[0], "menu", "")
        await callback.answer("Отмена оплаты")
        await callback.message.edit_text("Меню", reply_markup=kb_menu)
    elif info[8] == "stavka":
        update_table(info[0], "menu", "")
        await callback.answer("Отмена ставки")
        await callback.message.edit_text("Меню", reply_markup=kb_menu)
    elif info[8] == "play":
        update_table(info[0], "menu", "")
        await callback.answer("Отмена выбора кол-во мин")
        await callback.message.edit_text("Меню", reply_markup=kb_menu)



@ds.callback_query(F.data == "take")
async def withdraw(callback: Message):
    """Не закончено"""
    info = get_table_info(callback.from_user.id)[0]
    update_table(info[0], "menu", "", win=1, pay=(float(info[4]) * float(info[7])) - float(info[4]))
    await callback.answer(f"Вы выйграли: {int(info[4]) * float(info[7])} рублей")
    await callback.message.edit_text("Меню", reply_markup=kb_menu)

@ds.callback_query(F.data.isdigit())
async def game(callback: CallbackQuery):
    """Не проверено"""
    global mode
    info = get_table_info(callback.from_user.id)[0]
    s = callback.data
    choice = check_choise(info[0], int(s))
    info = get_table_info(info[0])[0]
    if choice == 3:
        await callback.message.edit_text(f"Выйгрыш: {info[4] * info[7]} руб, Коэфицент {info[7]},След {float(info[7])*mode[info[9]]}", reply_markup=print_game_map(info[6]))
    elif choice == 2:
        update_table(info[0], "menu", "", lose=1, pay=-info[4])
        await callback.answer(f"Вы проиграли и потеряли {info[4]} руб")
        await callback.message.edit_text("Меню", reply_markup=kb_menu)
    elif choice == 1:
        await callback.answer("Вы уже выбирали это поле")
    elif choice == 0:
        await callback.answer("Выход из списка")

@ds.message(F.text.isdigit())
async def all_number(message: Message):
    """Закончено"""
    info = get_table_info(message.from_user.id)[0]
    if info[8] == "pay":
        if int(info[1]) + int(message.text) <= 50000:
            update_table(info[0], "menu", info[9], pay=int(message.text))
            await message.answer(
                f"Пополнено на {int(message.text)} рублей, ваш баланс: {info[1] + int(message.text)} рублей.")
            await message.answer("Меню", reply_markup=kb_menu)
        else:
            update_table(info[0], "menu", "")
            await message.answer("У вас превышен(будет превышен) лимит")
            await message.answer("Меню", reply_markup=kb_menu)
    elif info[8] == "stavka":
        if 0 < int(message.text) <= info[1] + 1:
            game_map = print_game_map(info[6])
            if info[9] == "10 min":
                await message.answer("Ставка принята \n Режим 10 Мин")
                await message.answer(f"Выйгрыш: {message.text} руб, Коэфицент 1.00, След 1.40", reply_markup=game_map)
                update_table(info[0], "game", "10 min", create_game_map(10), stavka=int(message.text))
            elif info[9] == "7 min":
                await message.answer("Ставка принята \n Режим 7 Мин")
                await message.answer(f"Выйгрыш: {message.text} руб, Коэфицент 1.00, След 1.35", reply_markup=game_map)
                update_table(info[0], "game", "7 min", create_game_map(7), stavka=int(message.text))
            elif info[9] == "5 min":
                await message.answer("Ставка принята \n Режим 5 Мин")
                await message.answer(f"Выйгрыш: {message.text} руб, Коэфицент 1.00, След 1.20", reply_markup=game_map)
                update_table(info[0], "game", "5 min", create_game_map(5), stavka=int(message.text))
        else:
            await message.answer("Недостаточно средств или некорректный ввод")
            await message.answer("Меню", reply_markup=kb_menu)
            update_table(info[0], "menu", "")
    else:
        await message.answer("Ошибка ввода")
async def main():
    await ds.start_polling(bot)


asyncio.run(main())
