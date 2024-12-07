from aiogram import Bot, Dispatcher, types, F
from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton
)
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram import Router
import asyncio

API_TOKEN = ''

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

class Form(StatesGroup):
    age = State()
    growth = State()
    weight = State()

main_keyboard = ReplyKeyboardMarkup(
    resize_keyboard=True,
    keyboard=[
        [KeyboardButton(text='Рассчитать')],
        [KeyboardButton(text='Информация')]
    ]
)

inline_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Рассчитать норму калорий', callback_data='calories')],
        [InlineKeyboardButton(text='Формулы расчёта', callback_data='formulas')]
    ]
)

@dp.message(F.text.lower() == 'привет')
async def greet(message: types.Message):
    await message.answer("Введите команду /start, чтобы начать общение.")

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("Привет! Я бот, помогающий твоему здоровью.", reply_markup=main_keyboard)

@dp.message(F.text == 'Рассчитать')
async def main_menu(message: types.Message):
    await message.reply("Выберите опцию:", reply_markup=inline_keyboard)

@dp.callback_query(F.data == 'formulas')
async def get_formulas(call: types.CallbackQuery):
    formula_text = (
        "Формула Миффлина-Сан Жеора для расчёта калорий:\n\n"
        "Мужчины: 10 × вес (кг) + 6.25 × рост (см) - 5 × возраст + 5\n"
        "Женщины: 10 × вес (кг) + 6.25 × рост (см) - 5 × возраст - 161"
    )
    await call.message.answer(formula_text)
    await call.answer()

@dp.callback_query(F.data == 'calories')
async def set_age(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer("Введите свой возраст:")
    await state.set_state(Form.age)
    await call.answer()

@dp.message(Form.age)
async def process_age(message: types.Message, state: FSMContext):
    await state.update_data(age=int(message.text))
    await message.reply("Введите свой рост:")
    await state.set_state(Form.growth)

@dp.message(Form.growth)
async def process_growth(message: types.Message, state: FSMContext):
    await state.update_data(growth=int(message.text))
    await message.reply("Введите свой вес:")
    await state.set_state(Form.weight)

@dp.message(Form.weight)
async def process_weight(message: types.Message, state: FSMContext):
    data = await state.get_data()
    weight = int(message.text)
    age = data['age']
    growth = data['growth']

    calories = 10 * weight + 6.25 * growth - 5 * age + 5

    await message.reply(f"Ваша норма калорий: {calories:.2f}")
    await state.clear()

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
