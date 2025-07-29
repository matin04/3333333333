import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup
from sqlalchemy import select,update
from config import BOT_TOKEN
from db import Base, User, engine, async_session,  Course,Task,Student,Material
from random import choice
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# async def make_admin():
#     async with async_session() as session:
#         stmt = update(User).where(User.tg_id == 7101642329).values(is_admin=True)
#         await session.execute(stmt)
#         await session.commit()
# asyncio.run(make_admin())

 





async def make_notadmin( ):
    async with async_session() as session:
        stmt = update(User).where(User.tg_id == 7101642329).values(is_admin=False)
        await session.execute(stmt)
        await session.commit()
asyncio.run(make_notadmin())


class MyStates(StatesGroup):
    name=State()
    description=State()
    task_title=State()
    question_text = State()
    question_answer = State()
    material_title = State()
    material_description = State()
    exam_course = State()
    exam_task = State()
    exam_answer = State()

kb = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='добовлять курс')],
    [KeyboardButton(text='записаться на курс')],
    [KeyboardButton(text='добавить материал'), KeyboardButton(text='получить материалы')],
    [KeyboardButton(text='сдать задание'),KeyboardButton(text='проверка выполнения')] ,
], resize_keyboard=True)

@dp.message(F.text == '/start')
async def start(message: Message):
    await message.answer("Добро пожаловать", reply_markup=kb)
    async with async_session() as session:
        user = User(username=message.from_user.username, tg_id=message.from_user.id)
        user1 = await session.scalar(select(User).filter_by(tg_id=message.from_user.id))
        if not user1:
            session.add(user)
            await session.commit()


@dp.message(F.text == 'добовлять курс')
async def start_add_course(message: Message, state: FSMContext):
    async with async_session() as session:
        user=await session.scalar(select(User).filter_by(tg_id=message.from_user.id))
        if user.is_admin==True:
            await message.answer('Введите название курса:')
            await state.set_state(MyStates.name)
        else:
            await message.answer('Только админ можеть добавлять курс')

@dp.message(MyStates.name)
async def get_course_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Введите описание курса:")
    await state.set_state(MyStates.description)

@dp.message(MyStates.description)
async def get_course_desc(message: Message, state: FSMContext):
    data = await state.get_data()
    name = data['name']
    description = message.text

    async with async_session() as session:
        user = await session.scalar(select(User).filter_by(tg_id=message.from_user.id))
        new_course = Course(
            name_course=name,
            description=description,
            user_id=user.id
        )
        session.add(new_course)
        await session.commit()

        await state.clear()
        await message.answer("Курс добавлен. Теперь введите вопросы для этого курса.")
        await state.set_state(MyStates.task_title)

@dp.message(MyStates.task_title)
async def question(message: Message, state: FSMContext):
    await state.update_data(course_name=message.text) 
    await message.answer("Напиши вопрос и варианты ")
    await state.set_state(MyStates.question_text)

@dp.message(MyStates.question_text)
async def ask_correct_answer(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    await message.answer("вибирай правильный вариант (A,B,C,D)")
    await state.set_state(MyStates.question_answer)


@dp.message(MyStates.question_answer)
async def save_question(message: Message, state: FSMContext):
    data = await state.get_data()
    title = data['title']
    answer = message.text
    async with async_session() as session:
        user = await session.scalar(select(User).filter_by(tg_id=message.from_user.id))
        course = await session.scalar(select(Course).filter_by(user_id=user.id)) 
        task = Task(title=title, answer=answer, user_id=user.id, course_id=course.id)
        session.add(task)
        await session.commit()


@dp.message(F.text=='записаться на курс')
async def show_courses_to_enroll(message: Message, state: FSMContext):
    await state.clear()
    async with async_session() as session:
        courses = (await session.scalars(select(Course))).all()
        if not courses:
            await message.answer("Пока нет доступных курсов.")
            return
        buttons = []
        for course in courses:
            buttons.append([
                InlineKeyboardButton(
                    text=course.name_course,
                    callback_data=f"student_{course.id}"
                    )
                    ])
        markup = InlineKeyboardMarkup(inline_keyboard=buttons)
        await message.answer("Выберите курс для записи:", reply_markup=markup)


@dp.callback_query(F.data.startswith('student_'))
async def courses(callback: CallbackQuery):
    course_id = int(callback.data.split('_')[1])
    tg_id = callback.from_user.id

    async with async_session() as session:
        user = await session.scalar(select(User).filter_by(tg_id=tg_id))
        if not user:
            await callback.message.answer("Вы не зарегистрированы.")
            return

        exists = await session.scalar(
            select(Student).filter_by(user_id=user.id, course_id=course_id)
        )
        if exists:
            await callback.message.answer("Вы уже записаны на этот курс.")
        else:
            student = Student(user_id=user.id, course_id=course_id)
            session.add(student)
            await session.commit()
            await callback.message.answer("Вы успешно записались на курс!")

    await callback.answer()

@dp.message(F.text=='добавить материал')
async def start_add_material(message: Message, state: FSMContext):
    await state.clear()
    async with async_session() as session:
        user = await session.scalar(select(User).filter_by(tg_id=message.from_user.id))
        if user.is_admin==True:
            await message.answer("Введите название материала:")
            await state.set_state(MyStates.material_title)
        else:
            await message.answer("Только админ может добавлять материалы.")

@dp.message(MyStates.material_title)
async def material_name(message: Message, state: FSMContext):
    await state.update_data(material_title=message.text)
    await message.answer("Введите описание материала:")
    await state.set_state(MyStates.material_description)

@dp.message(MyStates.material_description)
async def material_description(message: Message, state: FSMContext):
    data = await state.get_data()
    title = data['material_title']
    description = message.text

    async with async_session() as session:
        user = await session.scalar(select(User).filter_by(tg_id=message.from_user.id))
        course = await session.scalar(select(Course).filter_by(user_id=user.id).order_by(Course.created_at.desc()))
        if not course:
            await message.answer("Сначала добавьте курс.")
            await state.clear()
            return

        material = Material(
            course_id=course.id,
            title=title,
            description=description,
        )
        session.add(material)
        await session.commit()

    await message.answer("Материал добавлен.")
    await state.clear()

@dp.message(F.text == 'получить материалы')
async def send_user_materials(message: Message):
    async with async_session() as session:
        user = await session.scalar(select(User).filter_by(tg_id=message.from_user.id))
        if not user:
            await message.answer("Сначала, зарегистрируйтесь")
            return

        student_courses = await session.scalars(
            select(Student).filter_by(user_id=user.id)
        )
        courses_ids = [sc.course_id for sc in student_courses.all()]

        if not courses_ids:
            await message.answer("Вы пока не записаны ни на один курс.")
            return
        materials = await session.scalars(
            select(Material).filter(Material.course_id.in_(courses_ids))
        )
        materials_list = materials.all()
        if not materials_list:
            await message.answer("Для ваших курсов пока нет материалов.")
            return
        
        text = "Материалы для ваших курсов:\n\n"
        for material in materials_list:
            text += f"{material.title}\n{material.description}\n\n"
        await message.answer(text)


