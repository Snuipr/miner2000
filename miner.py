import random
import asyncio
import psycopg2
from aiogram.types import Message
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

kb_game = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='0'), KeyboardButton(text='1'), KeyboardButton(text='2'), KeyboardButton(text='3'),
     KeyboardButton(text='4')],
    [KeyboardButton(text='5'), KeyboardButton(text='6'), KeyboardButton(text='7'), KeyboardButton(text='8'),
     KeyboardButton(text='9')],
    [KeyboardButton(text='10'), KeyboardButton(text='11'), KeyboardButton(text='12'), KeyboardButton(text='13'),
     KeyboardButton(text='14')],
    [KeyboardButton(text='15'), KeyboardButton(text='16'), KeyboardButton(text='17'), KeyboardButton(text='18'),
     KeyboardButton(text='19')],
    [KeyboardButton(text='20'), KeyboardButton(text='21'), KeyboardButton(text='22'), KeyboardButton(text='23'),
     KeyboardButton(text='24')],
    [KeyboardButton(text='Забрать')]], resize_keyboard=True)

kb_main = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="Играть")],
                                        [KeyboardButton(text="Баланс")],
                                        [KeyboardButton(text="Пополнить баланс")]], resize_keyboard=True)

kb_pay = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="Отмена")]], resize_keyboard=True)

kb_play = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="5 Мин")],
                                        [KeyboardButton(text="7 Мин")],
                                        [KeyboardButton(text="10 Мин")],
                                        [KeyboardButton(text="Отмена")]], resize_keyboard=True)


def add_new_user(user_id: str) -> None:
    con = psycopg2.connect(dbname='Test', user='postgres', password='1', host='195.2.80.193', port='22')
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
    con = psycopg2.connect(dbname='Test', user='postgres', password='1', host='195.2.80.193', port='22')
    cursor = con.cursor()
    cursor.execute("""UPDATE miner SET balance= %s WHERE id=%s""",
                   (balance + pay, user_id))
    con.commit()
    cursor.close()
    con.close()


def stavka_table(user_id: int, stavka: int) -> None:
    con = psycopg2.connect(dbname='Test', user='postgres', password='1', host='195.2.80.193', port='22')
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
    con = psycopg2.connect(dbname='Test', user='postgres', password='1', host='195.2.80.193', port='22')
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
    con = psycopg2.connect(dbname='Test', user='postgres', password='1', host='195.2.80.193', port='22')
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
        con = psycopg2.connect(dbname='Test', user='postgres', password='1', host='195.2.80.193', port='22')
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
    mode = {'5 min': 1.04,
            '7 min': 1.05,
            '10 min': 1.07}
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


def print_game_map(map: str) -> list:
    maping = {1: "⬛️", 2: "💥", 3: "💲"}
    s = []
    answer = []
    for i in map:
        s.append(maping[int(i)])
        if len(s) == 5:
            answer.append(s)
            s = []
    return answer


def get_table_my_map(map: str) -> list:
    answer = []
    for i in map:
        answer.append(i)
    return answer


bot = Bot(token='7566423981:AAEGDZp8kRuDWTlUTn_6xz-_XeLKS5aACnU')
ds = Dispatcher()


@ds.message(CommandStart())
async def start(message: Message):
    """Завершено"""
    info = get_table_info(message.from_user.id)[0]
    if info[8] == "menu":
        await message.answer("Приветствую пользователь", reply_markup=kb_main)
    elif info[8] == "pay":
        await message.answer("Введите сумму пополнения", reply_markup=kb_pay)
    elif info[8] == "stavka":
        await message.answer("Введите сумму ставки", reply_markup=kb_pay)
    elif info[8] == "play":
        await message.answer("Выберите кол-во мин", reply_markup=kb_play)
    elif info[8] == "game":
        game_map = print_game_map(info[6])
        await message.answer(
            f"{game_map[0][0]} {game_map[0][1]} {game_map[0][2]} {game_map[0][3]} {game_map[0][4]} \n"
            f"{game_map[1][0]} {game_map[1][1]} {game_map[1][2]} {game_map[1][3]} {game_map[1][4]} \n"
            f"{game_map[2][0]} {game_map[2][1]} {game_map[2][2]} {game_map[2][3]} {game_map[2][4]} \n"
            f"{game_map[3][0]} {game_map[3][1]} {game_map[3][2]} {game_map[3][3]} {game_map[3][4]} \n"
            f"{game_map[4][0]} {game_map[4][1]} {game_map[4][2]} {game_map[4][3]} {game_map[4][4]}",
            reply_markup=kb_game)
    else:
        print("Ошибка в блоке (Start)")


@ds.message(F.text == "Играть")
async def start_game(message: Message):
    """Не Проверено"""
    info = get_table_info(message.from_user.id)[0]
    if info[8] == "menu":
        update_table(info[0], "play", "")
        await message.answer("Выберите кол-во мин", reply_markup=kb_play)
    elif info[8] == "pay" or info[8] == "stavka":
        await message.answer("Вы не находитесь в меню", reply_markup=kb_pay)
    elif info[8] == "game":
        await message.answer("Вы уже начали игру", reply_markup=kb_game)
    elif info[8] == "play":
        await message.answer("Вы уже в игре", reply_markup=kb_play)
    else:
        print("Ошибка в блоке (Играть)")


@ds.message(F.text == "Баланс")
async def balance(message: Message):
    """Закончено"""
    info = get_table_info(message.from_user.id)[0]
    if info[8] == "menu":
        await message.answer(f"Ваш баланс: {info[1]} рублей")
    elif info[8] == "play":
        await message.answer("Вы не находитесь в меню", reply_markup=kb_play)
    elif info[8] == "game":
        await message.answer("Вы не находитесь в меню", reply_markup=kb_game)
    elif info[8] == "pay":
        await message.answer("Вы не находитесь в меню", reply_markup=kb_pay)
    elif info[8] == "stavka":
        await message.answer("Вы не находитесь в меню", reply_markup=kb_pay)


@ds.message(F.text == "Пополнить баланс")
async def pay(message: Message):
    """Не Проверено"""
    info = get_table_info(message.from_user.id)[0]
    if info[8] == "menu":
        await message.answer(
            f"Введите сумму пополнения, текущий баланс: {info[1]} рублей \n (Если на балансе больше 50 к рублей пополнять нельзя)",
            reply_markup=kb_pay)
        update_table(info[0], "pay", "")
    elif info[8] == "play":
        await message.answer("Вы не находитесь в меню", reply_markup=kb_play)
    elif info[8] == "game":
        await message.answer("Вы не находитесь в меню", reply_markup=kb_game)
    elif info[8] == "stavka":
        await message.answer("Вы не находитесь в меню", reply_markup=kb_pay)
    else:
        print("Ошибка в блоке (Пополнить баланс)")


@ds.message(F.text == "5 Мин")
async def game_5(message: Message):
    """Не проверено"""
    info = get_table_info(message.from_user.id)[0]
    if info[8] == "play":
        update_table(info[0], "stavka", "5 min")
        await message.answer(f"Ваш баланс: {info[1]} рублей \n Выберите ставку", reply_markup=kb_pay)
    elif info[8] == "menu":
        await message.answer("Вы не находитесь в меню игры", reply_markup=kb_main)
    elif info[8] == "game":
        await message.answer("Вы не находитесь в меню игры", reply_markup=kb_game)
    elif info[8] == "pay" or info[8] == "stavka":
        await message.answer("Вы не находитесь в меню игры", reply_markup=kb_pay)
    else:
        print("Ошибка в блоке (5 Мин)")


@ds.message(F.text == "7 Мин")
async def game_7(message: Message):
    """Не проверено"""
    info = get_table_info(message.from_user.id)[0]
    if info[8] == "play":
        update_table(info[0], "stavka", "7 min")
        await message.answer(f"Ваш баланс: {info[1]} рублей \n Выберите ставку", reply_markup=kb_pay)
    elif info[8] == "menu":
        await message.answer("Вы не находитесь в меню игры", reply_markup=kb_main)
    elif info[8] == "game":
        await message.answer("Вы не находитесь в меню игры", reply_markup=kb_game)
    elif info[8] == "pay" or info[8] == "stavka":
        await message.answer("Вы не находитесь в меню игры", reply_markup=kb_pay)
    else:
        print("Ошибка в блоке (7 Мин)")


@ds.message(F.text == "10 Мин")
async def game_10(message: Message):
    """Не проверено"""
    info = get_table_info(message.from_user.id)[0]
    if info[8] == "play":
        update_table(info[0], "stavka", "10 min")
        await message.answer(f"Ваш баланс: {info[1]} рублей \n Выберите ставку", reply_markup=kb_pay)
    elif info[8] == "menu":
        await message.answer("Вы не находитесь в меню игры", reply_markup=kb_main)
    elif info[8] == "game":
        await message.answer("Вы не находитесь в меню игры", reply_markup=kb_game)
    elif info[8] == "pay":
        await message.answer("Вы не находитесь в меню игры", reply_markup=kb_pay)
    else:
        print("Ошибка в блоке (10 Мин)")


@ds.message(F.text == "Отмена")
async def pay_close(message: Message):
    """Не проверено"""
    info = get_table_info(message.from_user.id)[0]
    if info[8] == "pay":
        update_table(info[0], "menu", "")
        await message.answer("Отмена оплаты", reply_markup=kb_main)
    elif info[8] == "stavka":
        update_table(info[0], "menu", "")
        await message.answer("Отмена ставки", reply_markup=kb_main)
    elif info[8] == "play":
        update_table(info[0], "menu", "")
        await message.answer("Отмена выбора кол-во мин", reply_markup=kb_main)
    elif info[8] == "game":
        await message.answer("Нельзя во время игры", reply_markup=kb_game)
    elif info[8] == "menu":
        await message.answer("Нечего отменять", reply_markup=kb_main)
    else:
        print("Ошибка в блоке (Отмена)")


@ds.message(F.text == "Забрать")
async def withdraw(message: Message):
    """Не закончено"""
    info = get_table_info(message.from_user.id)[0]
    if info[8] == "game":
        update_table(info[0], "menu", "", win=1, pay=(float(info[4]) * float(info[7])) - float(info[4]))
        await message.answer(f"Вы выйграли: {int(info[4]) * float(info[7]) - float(info[4])} рублей \n"
                             f"Ваш баланс: {float(info[1]) + ((float(info[4]) * float(info[7]) - float(info[4])))} рублей",
                             reply_markup=kb_main)
    elif info[8] == "menu":
        await message.answer("Нельзя вне игры", reply_markup=kb_main)
    elif info[8] == "play":
        await message.answer("Нельзя вне игры", reply_markup=kb_play)
    elif info[8] == "pay" or info[8] == "stavka":
        await message.answer("Нельзя вне игры", reply_markup=kb_pay)
    else:
        print("Ошибка в блоке (Забрать)")


@ds.message(F.text.isdigit())
async def all_number(message: Message):
    """Закончено"""
    info = get_table_info(message.from_user.id)[0]
    if info[8] == "pay":
        if info[1] <= 50000 and int(info[1]) + int(message.text) <= 50000:
            update_table(info[0], "menu", info[9], pay=int(message.text))
            await message.answer(
                f"Пополнено на {int(message.text)} рублей, ваш баланс: {info[1] + int(message.text)} рублей.",
                reply_markup=kb_main)
        else:
            await message.answer("У вас превышен(будет превышен) лимит", reply_markup=kb_main)
            update_table(info[0], "menu", "")
    elif info[8] == "stavka" and info[9] == "10 min":
        if int(message.text) <= info[1] + 1 and int(message.text) > 0:
            await message.answer("Ставка принята \n Режим 10 Мин")
            update_table(info[0], "game", "10 min", game_map=create_game_map(10), stavka=int(message.text))
            game_map = print_game_map(info[6])
            await message.answer(
                f"{game_map[0][0]} {game_map[0][1]} {game_map[0][2]} {game_map[0][3]} {game_map[0][4]} \n"
                f"{game_map[1][0]} {game_map[1][1]} {game_map[1][2]} {game_map[1][3]} {game_map[1][4]} \n"
                f"{game_map[2][0]} {game_map[2][1]} {game_map[2][2]} {game_map[2][3]} {game_map[2][4]} \n"
                f"{game_map[3][0]} {game_map[3][1]} {game_map[3][2]} {game_map[3][3]} {game_map[3][4]} \n"
                f"{game_map[4][0]} {game_map[4][1]} {game_map[4][2]} {game_map[4][3]} {game_map[4][4]}",
                reply_markup=kb_game)
        else:
            update_table(info[0], "menu", "")
            await message.answer("Недостаточно средств", reply_markup=kb_main)
    elif info[8] == "stavka" and info[9] == "7 min":
        if int(message.text) <= info[1] + 1 and int(message.text) > 0:
            await message.answer("Ставка принята \n Режим 7 Мин")
            update_table(info[0], "game", "7 min", create_game_map(7), stavka=int(message.text))
            game_map = print_game_map(info[6])
            await message.answer(
                f"{game_map[0][0]} {game_map[0][1]} {game_map[0][2]} {game_map[0][3]} {game_map[0][4]} \n"
                f"{game_map[1][0]} {game_map[1][1]} {game_map[1][2]} {game_map[1][3]} {game_map[1][4]} \n"
                f"{game_map[2][0]} {game_map[2][1]} {game_map[2][2]} {game_map[2][3]} {game_map[2][4]} \n"
                f"{game_map[3][0]} {game_map[3][1]} {game_map[3][2]} {game_map[3][3]} {game_map[3][4]} \n"
                f"{game_map[4][0]} {game_map[4][1]} {game_map[4][2]} {game_map[4][3]} {game_map[4][4]}",
                reply_markup=kb_game)
        else:
            update_table(info[0], "menu", "")
            await message.answer("Недостаточно средств", reply_markup=kb_main)
    elif info[8] == "stavka" and info[9] == "5 min":
        if int(message.text) <= info[1] + 1 and int(message.text) > 0:
            await message.answer("Ставка принята \n Режим 5 Мин")
            update_table(info[0], "game", "5 min", create_game_map(5), stavka=int(message.text))
            game_map = print_game_map(info[6])
            await message.answer(
                f"{game_map[0][0]} {game_map[0][1]} {game_map[0][2]} {game_map[0][3]} {game_map[0][4]} \n"
                f"{game_map[1][0]} {game_map[1][1]} {game_map[1][2]} {game_map[1][3]} {game_map[1][4]} \n"
                f"{game_map[2][0]} {game_map[2][1]} {game_map[2][2]} {game_map[2][3]} {game_map[2][4]} \n"
                f"{game_map[3][0]} {game_map[3][1]} {game_map[3][2]} {game_map[3][3]} {game_map[3][4]} \n"
                f"{game_map[4][0]} {game_map[4][1]} {game_map[4][2]} {game_map[4][3]} {game_map[4][4]}",
                reply_markup=kb_game)
        else:
            update_table(info[0], "menu", "")
            await message.answer("Недостаточно средств", reply_markup=kb_main)
    elif info[8] == "game":
        choice = check_choise(info[0], int(message.text))
        info = get_table_info(info[0])[0]
        game_map = print_game_map(info[6])
        if choice == 3:
            await message.answer(
                f"{game_map[0][0]} {game_map[0][1]} {game_map[0][2]} {game_map[0][3]} {game_map[0][4]} \n"
                f"{game_map[1][0]} {game_map[1][1]} {game_map[1][2]} {game_map[1][3]} {game_map[1][4]} \n"
                f"{game_map[2][0]} {game_map[2][1]} {game_map[2][2]} {game_map[2][3]} {game_map[2][4]} \n"
                f"{game_map[3][0]} {game_map[3][1]} {game_map[3][2]} {game_map[3][3]} {game_map[3][4]} \n"
                f"{game_map[4][0]} {game_map[4][1]} {game_map[4][2]} {game_map[4][3]} {game_map[4][4]}",
                reply_markup=kb_game)
        elif choice == 2:
            update_table(info[0], "menu", "", lose=1, pay=-info[4])
            await message.answer("💥")
            await message.answer(
                f"Вы проиграли и потеряли {info[4]} рублей. \n Ваш баланс: {int(info[1]) - int(info[4])} рублей.",
                reply_markup=kb_main)
        elif choice == 1:
            await message.answer(
                f"{game_map[0][0]} {game_map[0][1]} {game_map[0][2]} {game_map[0][3]} {game_map[0][4]} \n"
                f"{game_map[1][0]} {game_map[1][1]} {game_map[1][2]} {game_map[1][3]} {game_map[1][4]} \n"
                f"{game_map[2][0]} {game_map[2][1]} {game_map[2][2]} {game_map[2][3]} {game_map[2][4]} \n"
                f"{game_map[3][0]} {game_map[3][1]} {game_map[3][2]} {game_map[3][3]} {game_map[3][4]} \n"
                f"{game_map[4][0]} {game_map[4][1]} {game_map[4][2]} {game_map[4][3]} {game_map[4][4]}",
                reply_markup=kb_game)
        elif choice == 0:
            await message.answer(
                f"{game_map[0][0]} {game_map[0][1]} {game_map[0][2]} {game_map[0][3]} {game_map[0][4]} \n"
                f"{game_map[1][0]} {game_map[1][1]} {game_map[1][2]} {game_map[1][3]} {game_map[1][4]} \n"
                f"{game_map[2][0]} {game_map[2][1]} {game_map[2][2]} {game_map[2][3]} {game_map[2][4]} \n"
                f"{game_map[3][0]} {game_map[3][1]} {game_map[3][2]} {game_map[3][3]} {game_map[3][4]} \n"
                f"{game_map[4][0]} {game_map[4][1]} {game_map[4][2]} {game_map[4][3]} {game_map[4][4]}",
                reply_markup=kb_game)
    else:
        await message.answer("Неверный ввод", reply_markup=kb_game)


@ds.message()
async def all_message(message: Message):
    await message.answer("Старайтесь пользоваться клавиатурой если это возможно")


async def main():
    await ds.start_polling(bot)


asyncio.run(main())
