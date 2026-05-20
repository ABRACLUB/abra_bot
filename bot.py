import asyncio
import logging
import sqlite3
import os
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart
from aiogram.fsm.storage.memory import MemoryStorage

logging.basicConfig(level=logging.INFO)
BOT_TOKEN = os.getenv("BOT_TOKEN", "8761840516:AAFWjU4F6-weSjiv9bLMLeG6U439SRmRnw0")

bot = Bot(token=BOT_TOKEN)
dp  = Dispatcher(storage=MemoryStorage())

# ─── DATABASE ────────────────────────────────────────────────
DB = "bot.db"

def init_db():
    with sqlite3.connect(DB) as c:
        c.execute('''CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            name    TEXT,
            score   INTEGER DEFAULT 0
        )''')

def upsert_user(uid, name):
    with sqlite3.connect(DB) as c:
        c.execute("INSERT OR IGNORE INTO users (user_id,name,score) VALUES(?,?,0)", (uid,name))

def add_score(uid, pts):
    with sqlite3.connect(DB) as c:
        c.execute("UPDATE users SET score=score+? WHERE user_id=?", (pts,uid))

def get_score(uid):
    with sqlite3.connect(DB) as c:
        r = c.execute("SELECT score FROM users WHERE user_id=?", (uid,)).fetchone()
        return r[0] if r else 0

# ─── HELPERS ─────────────────────────────────────────────────
def kb(*buttons):
    """kb(("Текст","callback"), ...) → InlineKeyboardMarkup"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t, callback_data=d)] for t,d in buttons
    ])

def url_kb(text, url):
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=text, url=url)]])

async def send(cb: CallbackQuery, text, markup=None, md=True):
    await cb.message.answer(text, parse_mode="Markdown" if md else None, reply_markup=markup)

async def edit_and_send(cb: CallbackQuery, text, markup=None, md=True):
    await cb.message.edit_reply_markup()
    await send(cb, text, markup, md)

# ─── /start ──────────────────────────────────────────────────
@dp.message(CommandStart())
async def cmd_start(msg: Message):
    upsert_user(msg.from_user.id, msg.from_user.first_name)
    name = msg.from_user.first_name
    await msg.answer(
        f"Привет, {name} 👋\n\n"
        "Ты только что открыл мини-курс *«Как использовать нейросети в маркетинге»* от ABRA CLUB.\n\n"
        "5 уроков. Только практика. Никакой воды.\n\n"
        "За выполнение практик — баллы. В конце курса баллы дадут тебе кое-что приятное 🎁\n\n"
        "Готов начать?",
        parse_mode="Markdown",
        reply_markup=kb(("🚀 Поехали", "start_course"))
    )

# ─── СТАРТ ───────────────────────────────────────────────────
@dp.callback_query(F.data == "start_course")
async def start_course(cb: CallbackQuery):
    await edit_and_send(cb,
        "🎖 *Звание: НОВОБРАНЕЦ*\n"
        "_Ты сделал первый шаг. Большинство не делает даже его._\n\n"
        "Прогресс: ░░░░░ 0%",
        kb(("📖 Перейти к Уроку 1", "lesson_1"))
    )
    await cb.answer()

# ══════════════════════════════════════════════════════════════
#  УРОК 1
# ══════════════════════════════════════════════════════════════
@dp.callback_query(F.data == "lesson_1")
async def lesson_1(cb: CallbackQuery):
    await edit_and_send(cb,
        "📘 *УРОК 1 из 5*\n"
        "_Зачем маркетологу нейросети — и почему большинство использует их неправильно_\n\n"
        "Прогресс: █░░░░ 20%",
        kb(("Читать урок →", "l1_text"))
    )
    await cb.answer()

@dp.callback_query(F.data == "l1_text")
async def l1_text(cb: CallbackQuery):
    await cb.message.edit_reply_markup()
    msgs = [
        "Когда ChatGPT стал публичным, маркетологи разделились на два лагеря.\n\n"
        "Первые сказали: «ИИ заменит нас всех» — и начали паниковать.\n"
        "Вторые сказали: «Это просто инструмент» — и использовали его как замену копирайтеру.\n\n"
        "Обе реакции — неправильные.",

        "Типичная картина: открываешь ChatGPT, пишешь «напиши пост про мой продукт» — "
        "получаешь что-то среднее — публикуешь или выбрасываешь.\n\n"
        "Проблема не в инструменте. Проблема в подходе.\n\n"
        "ИИ — это не автор. Это *соавтор*. Он работает ровно настолько хорошо, "
        "насколько хорошо ты умеешь с ним разговаривать.",

        "Три уровня использования ИИ:\n\n"
        "🔵 *Уровень 1 — Исполнитель*\nИИ пишет тексты вместо тебя. Экономия — 20-30%.\n\n"
        "🟡 *Уровень 2 — Ассистент*\nИИ помогает думать, генерировать идеи. Скорость ×3-5.\n\n"
        "🟢 *Уровень 3 — Система*\nИИ встроен во весь маркетинговый процесс.\n\n"
        "Большинство застревает на уровне 1. Этот курс — про то, как дойти до уровня 3.",

        "💡 *Попробуй прямо сейчас:*\n\n"
        "Открой ChatGPT или Claude. Напиши:\n\n"
        "«Ты — маркетолог с опытом в [твоя ниша]. Моя аудитория — [описание]. "
        "Мой продукт — [описание]. Главная боль клиента — [боль]. "
        "Напиши пост для Instagram, который цепляет с первой строки.»\n\n"
        "Сравни с тем, что получается без контекста. Почувствуй разницу.",
    ]
    for m in msgs:
        await cb.message.answer(m, parse_mode="Markdown")
        await asyncio.sleep(0.8)
    await cb.message.answer(
        "📝 *ПРАКТИКА К УРОКУ 1*\n\n"
        "Выпиши 5 задач, которые ты делаешь регулярно в маркетинге.\n"
        "Напротив каждой отметь: можно ли делать это с ИИ быстрее или лучше?\n\n"
        "Это твоя карта точек роста. Ты сделал практику?",
        parse_mode="Markdown",
        reply_markup=kb(("✅ Да, сделал (+20 баллов)", "p1_yes"), ("⏭ Пропустить", "p1_skip"))
    )
    await cb.answer()

@dp.callback_query(F.data == "p1_yes")
async def p1_yes(cb: CallbackQuery):
    add_score(cb.from_user.id, 20)
    s = get_score(cb.from_user.id)
    await edit_and_send(cb,
        f"🔥 +20 баллов! Твой счёт: *{s} баллов*\n\n"
        "☑ Я понимаю разницу между ИИ как исполнителем и ИИ как системой\n"
        "☑ Я знаю свой текущий уровень\n"
        "☑ У меня есть список задач, где ИИ может усилить работу",
        kb(("Урок 2 →", "lesson_2"))
    )
    await cb.answer()

@dp.callback_query(F.data == "p1_skip")
async def p1_skip(cb: CallbackQuery):
    await edit_and_send(cb,
        "Окей, можешь вернуться к практике позже.\n\n"
        "☑ Я понимаю разницу между ИИ как исполнителем и ИИ как системой\n"
        "☑ Я знаю свой текущий уровень",
        kb(("Урок 2 →", "lesson_2"))
    )
    await cb.answer()

# ══════════════════════════════════════════════════════════════
#  УРОК 2
# ══════════════════════════════════════════════════════════════
@dp.callback_query(F.data == "lesson_2")
async def lesson_2(cb: CallbackQuery):
    await edit_and_send(cb,
        "🎖 Новое звание: *ПРАКТИК*\n"
        "_Ты уже думаешь иначе, чем большинство._\n\n"
        "📘 *УРОК 2 из 5*\n"
        "_Промпт-инжиниринг для маркетолога: 3 принципа, которые меняют результат_\n\n"
        "Прогресс: ██░░░ 40%",
        kb(("Читать урок →", "l2_text"))
    )
    await cb.answer()

@dp.callback_query(F.data == "l2_text")
async def l2_text(cb: CallbackQuery):
    await cb.message.edit_reply_markup()
    msgs = [
        "Промпт — это задание, которое ты даёшь ИИ.\n\n"
        "Качество результата почти полностью зависит от качества промпта.\n"
        "Плохой промпт = мусор. Хороший промпт = готовый инструмент.\n\n"
        "Три принципа, которые работают в 90% маркетинговых задач 👇",

        "*Принцип 1. Роль + Контекст + Задача*\n\n"
        "❌ Слабый: «Напиши заголовок для поста»\n\n"
        "✅ Сильный:\n«Ты — опытный копирайтер в Instagram. Моя аудитория — женщины 25-40, "
        "владелицы малого бизнеса. Напиши 10 вариантов заголовка для поста о продажах "
        "без навязчивости. До 10 слов, цепляет с первой секунды.»",

        "*Принцип 2. Итерация вместо одного запроса*\n\n"
        "Первый ответ ИИ — это черновик. Дальше уточняй:\n\n"
        "→ «Сделай более провокационным»\n"
        "→ «Убери воду, оставь только суть»\n"
        "→ «Вариант 3 ближе всего — доработай его»\n\n"
        "Обычно 3-4 итерации дают результат, который можно публиковать.",

        "*Принцип 3. Библиотека шаблонов*\n\n"
        "Не изобретай промпт каждый раз. Сохрани рабочие шаблоны.\n\n"
        "📌 *Шаблон для поста:*\n"
        "«Ты — контент-маркетолог. Аудитория: [описание]. Тема: [тема]. "
        "Боль аудитории: [боль]. Структура: цепляющий первый абзац → мысль с примером → призыв к действию.»\n\n"
        "📌 *Продвинутый приём:*\n"
        "«Прежде чем выполнять задачу, задай мне 5 вопросов, которые помогут тебе "
        "сделать результат максимально точным.»\n\n"
        "ИИ сам подскажет, какой контекст ему нужен 🔥",
    ]
    for m in msgs:
        await cb.message.answer(m, parse_mode="Markdown")
        await asyncio.sleep(0.8)
    await cb.message.answer(
        "📝 *ПРАКТИКА К УРОКУ 2*\n\n"
        "1. Выбери 3 задачи, которые делаешь чаще всего\n"
        "2. Для каждой напиши промпт по структуре: Роль + Контекст + Задача\n"
        "3. Протестируй каждый и сохрани в отдельный документ\n\n"
        "Ты сделал практику?",
        parse_mode="Markdown",
        reply_markup=kb(("✅ Да, сделал (+20 баллов)", "p2_yes"), ("⏭ Пропустить", "p2_skip"))
    )
    await cb.answer()

@dp.callback_query(F.data == "p2_yes")
async def p2_yes(cb: CallbackQuery):
    add_score(cb.from_user.id, 20)
    s = get_score(cb.from_user.id)
    await edit_and_send(cb,
        f"🔥 +20 баллов! Твой счёт: *{s} баллов*\n\n"
        "☑ Я знаю структуру сильного промпта: Роль + Контекст + Задача\n"
        "☑ Работа с ИИ — это диалог, а не один запрос\n"
        "☑ У меня есть минимум 3 рабочих промпта",
        kb(("Урок 3 →", "lesson_3"))
    )
    await cb.answer()

@dp.callback_query(F.data == "p2_skip")
async def p2_skip(cb: CallbackQuery):
    await edit_and_send(cb,
        "☑ Я знаю структуру сильного промпта: Роль + Контекст + Задача\n"
        "☑ Работа с ИИ — это диалог, а не один запрос",
        kb(("Урок 3 →", "lesson_3"))
    )
    await cb.answer()

# ══════════════════════════════════════════════════════════════
#  УРОК 3
# ══════════════════════════════════════════════════════════════
@dp.callback_query(F.data == "lesson_3")
async def lesson_3(cb: CallbackQuery):
    await edit_and_send(cb,
        "🎖 Новое звание: *СТРАТЕГ*\n"
        "_Ты работаешь с ИИ системнее, чем 90% маркетологов._\n\n"
        "📘 *УРОК 3 из 5*\n"
        "_Как ИИ помогает прогревать аудиторию — без ощущения манипуляции_\n\n"
        "Прогресс: ███░░ 60%",
        kb(("Читать урок →", "l3_text"))
    )
    await cb.answer()

@dp.callback_query(F.data == "l3_text")
async def l3_text(cb: CallbackQuery):
    await cb.message.edit_reply_markup()
    msgs = [
        "Прогрев — одно из самых недопонятых слов в маркетинге.\n\n"
        "Для многих прогрев = серия манипулятивных постов с FOMO и давлением.\n\n"
        "Именно поэтому аудитория научилась чувствовать прогрев за километр — и закрываться.\n\n"
        "*Прогрев на самом деле* — это последовательное выстраивание доверия "
        "до того, как ты предлагаешь купить.",

        "Человек покупает, когда:\n"
        "1. Понимает, что у него есть проблема\n"
        "2. Видит, что ты её понимаешь лучше него\n"
        "3. Верит, что твоё решение работает\n"
        "4. Чувствует, что ты говоришь честно\n\n"
        "Никакой манипуляции. Только работа с доверием.",

        "*Контентная матрица для прогрева — 4 типа:*\n\n"
        "🔵 *Осознание* — помогает назвать проблему\n"
        "_Пример: «5 признаков, что твоя контент-стратегия не работает»_\n\n"
        "🟡 *Экспертиза* — показывает глубину понимания\n"
        "_Пример: разборы, кейсы, нестандартные углы_\n\n"
        "🟢 *Доверие* — снимает страхи и возражения\n"
        "_Пример: честные посты о провалах, закулисье_\n\n"
        "🔴 *Решение* — показывает результат\n"
        "_Пример: кейсы с цифрами, отзывы_\n\n"
        "Правильный прогрев = все четыре типа в нужной последовательности.",

        "📌 *Для контента осознания:*\n"
        "«Моя аудитория — [описание]. Их проблема — [проблема]. "
        "Напиши 10 идей для постов, которые помогут им осознать эту проблему. Без продажи.»\n\n"
        "📌 *Для контента доверия:*\n"
        "«Помоги написать честный пост о [сложная ситуация/ошибка]. "
        "Тон: открытый, без самобичевания, с выводом.»\n\n"
        "📌 *Как сохранить живой голос:*\n"
        "«Вот 3 моих поста: [тексты]. Определи мой стиль. "
        "Теперь напиши пост на тему [тема] в этом же стиле.»",
    ]
    for m in msgs:
        await cb.message.answer(m, parse_mode="Markdown")
        await asyncio.sleep(0.8)
    await cb.message.answer(
        "📝 *ПРАКТИКА К УРОКУ 3*\n\n"
        "1. Попроси ИИ описать 7 главных болей твоей аудитории — их словами\n"
        "2. Составь контент-план на месяц: 8 осознание, 8 экспертиза, 6 доверие, 6 решение\n"
        "3. Напиши один пост каждого типа с ИИ — добавь личную деталь от себя\n\n"
        "Ты сделал практику?",
        parse_mode="Markdown",
        reply_markup=kb(("✅ Да, сделал (+20 баллов)", "p3_yes"), ("⏭ Пропустить", "p3_skip"))
    )
    await cb.answer()

@dp.callback_query(F.data == "p3_yes")
async def p3_yes(cb: CallbackQuery):
    add_score(cb.from_user.id, 20)
    s = get_score(cb.from_user.id)
    await edit_and_send(cb,
        f"🔥 +20 баллов! Твой счёт: *{s} баллов*\n\n"
        "☑ Я понимаю разницу между манипуляцией и доверием\n"
        "☑ Я знаю 4 типа прогревающего контента\n"
        "☑ У меня есть карта болей аудитории\n"
        "☑ У меня есть контент-план на месяц",
        kb(("Урок 4 →", "lesson_4"))
    )
    await cb.answer()

@dp.callback_query(F.data == "p3_skip")
async def p3_skip(cb: CallbackQuery):
    await edit_and_send(cb,
        "☑ Я понимаю разницу между манипуляцией и доверием\n"
        "☑ Я знаю 4 типа прогревающего контента",
        kb(("Урок 4 →", "lesson_4"))
    )
    await cb.answer()

# ══════════════════════════════════════════════════════════════
#  УРОК 4
# ══════════════════════════════════════════════════════════════
@dp.callback_query(F.data == "lesson_4")
async def lesson_4(cb: CallbackQuery):
    await edit_and_send(cb,
        "🎖 Новое звание: *АНАЛИТИК*\n"
        "_Ты видишь маркетинг как систему. Это уже другой уровень._\n\n"
        "📘 *УРОК 4 из 5*\n"
        "_ИИ в аналитике: как понять что работает — и быстро перестроиться_\n\n"
        "Прогресс: ████░ 80%",
        kb(("Читать урок →", "l4_text"))
    )
    await cb.answer()

@dp.callback_query(F.data == "l4_text")
async def l4_text(cb: CallbackQuery):
    await cb.message.edit_reply_markup()
    msgs = [
        "Большинство маркетологов делают контент интуитивно.\n\n"
        "Публикуют. Смотрят на лайки. Делают выводы на ощущениях.\n\n"
        "Это не аналитика. Это гадание.\n\n"
        "ИИ позволяет перейти к системному пониманию — даже без сложных инструментов.",

        "*Что анализировать с помощью ИИ:*\n\n"
        "📊 *Свой контент:*\n«Вот мои последние 10 постов с показателями: [данные]. "
        "Что работает? Какие паттерны в постах с высоким вовлечением?»\n\n"
        "🔍 *Конкурентов:*\n«Вот тексты конкурента: [тексты]. Где они слабы? "
        "Как я могу занять нишу, которую они не закрывают?»\n\n"
        "💬 *Отзывы клиентов:*\n«Вот отзывы: [тексты]. Выдели: главные боли, "
        "слова которые они используют, скрытые возражения.»\n\n"
        "✏️ *Свой оффер:*\n«Вот мой продающий текст: [текст]. Какие возражения не закрыты? "
        "Как усилить главный аргумент?»",

        "*Система быстрой перестройки:*\n\n"
        "📅 Неделя 1: публикуешь контент\n"
        "📊 Конец недели: собираешь данные\n"
        "🤖 Анализ с ИИ: получаешь выводы\n"
        "📅 Неделя 2: больше того, что работает — меньше того, что нет\n\n"
        "Это не сложно. Это дисциплина.",
    ]
    for m in msgs:
        await cb.message.answer(m, parse_mode="Markdown")
        await asyncio.sleep(0.8)
    await cb.message.answer(
        "📝 *ПРАКТИКА К УРОКУ 4*\n\n"
        "1. Возьми последние 10 постов — проанализируй с ИИ\n"
        "2. Скопируй 5-7 постов конкурента — найди слабую зону\n"
        "3. Попроси ИИ критически оценить твой оффер — внеси 3 улучшения\n\n"
        "Ты сделал практику?",
        parse_mode="Markdown",
        reply_markup=kb(("✅ Да, сделал (+20 баллов)", "p4_yes"), ("⏭ Пропустить", "p4_skip"))
    )
    await cb.answer()

@dp.callback_query(F.data == "p4_yes")
async def p4_yes(cb: CallbackQuery):
    add_score(cb.from_user.id, 20)
    s = get_score(cb.from_user.id)
    await edit_and_send(cb,
        f"🔥 +20 баллов! Твой счёт: *{s} баллов*\n\n"
        "☑ Я провёл анализ своего контента с ИИ\n"
        "☑ Я нашёл слабую зону конкурента\n"
        "☑ Я улучшил свой оффер\n"
        "☑ У меня есть еженедельный цикл аналитики",
        kb(("🏁 Финальный урок →", "lesson_5"))
    )
    await cb.answer()

@dp.callback_query(F.data == "p4_skip")
async def p4_skip(cb: CallbackQuery):
    await edit_and_send(cb,
        "☑ Я понимаю как анализировать контент с ИИ\n"
        "☑ Я знаю как улучшить оффер через обратную связь ИИ",
        kb(("🏁 Финальный урок →", "lesson_5"))
    )
    await cb.answer()

# ══════════════════════════════════════════════════════════════
#  УРОК 5
# ══════════════════════════════════════════════════════════════
@dp.callback_query(F.data == "lesson_5")
async def lesson_5(cb: CallbackQuery):
    name = cb.from_user.first_name
    await edit_and_send(cb,
        f"Ты дошёл до финального урока, {name}.\n\nЭто уже говорит о многом 💪\n\n"
        "📘 *УРОК 5 из 5*\n"
        "_Собираем систему: твой маркетинг на ИИ с нуля до результата_\n\n"
        "Прогресс: █████ 100%",
        kb(("Читать последний урок →", "l5_text"))
    )
    await cb.answer()

@dp.callback_query(F.data == "l5_text")
async def l5_text(cb: CallbackQuery):
    await cb.message.edit_reply_markup()
    msgs = [
        "Четыре урока позади.\n\n"
        "Ты знаешь инструменты. Умеешь писать промпты. "
        "Понимаешь как строить контент. Умеешь анализировать.\n\n"
        "Теперь — собрать всё в систему.\n\n"
        "Потому что разовые действия не дают результата. Система — даёт.",

        "*Маркетинговая система на ИИ — 6 этапов:*\n\n"
        "1️⃣ *Исследование* (раз в квартал)\nПортрет аудитории, анализ конкурентов, актуальные боли.\n\n"
        "2️⃣ *Стратегия* (раз в месяц)\nЦель месяца, контент-план, логика последовательности.\n\n"
        "3️⃣ *Создание контента* (еженедельно)\nЧерновики по промптам → твой финальный голос.\n\n"
        "4️⃣ *Публикация* (по расписанию)\nTelegram: 3-5 постов в неделю. Instagram: 4-5 + сторис.\n\n"
        "5️⃣ *Аналитика* (еженедельно)\nДанные → ИИ → 2-3 вывода → план корректировки.\n\n"
        "6️⃣ *Корректировка* (еженедельно)\nБольше того, что работает. Меньше того, что нет.",

        "*Минимальный стек для старта:*\n\n"
        "🤖 Тексты и идеи — ChatGPT или Claude\n"
        "🔍 Исследование — Perplexity\n"
        "🎨 Визуал — Midjourney или DALL-E\n"
        "📋 Планирование — Notion\n"
        "📊 Аналитика — встроенная статистика платформ\n\n"
        "Начни с ChatGPT + один инструмент для визуала. Не нужно осваивать всё сразу.",

        "Главное, что нужно помнить:\n\n"
        "— ИИ усиливает то, что ты уже умеешь\n"
        "— Понимание аудитории важнее скорости создания контента\n"
        "— Твой голос и экспертиза важнее любого промпта\n\n"
        "Начни с малого. Одна система. Одна неделя. Посмотри на результат. Скорректируй. Повтори.",
    ]
    for m in msgs:
        await cb.message.answer(m, parse_mode="Markdown")
        await asyncio.sleep(0.8)
    await cb.message.answer(
        "📝 *ПРАКТИКА К УРОКУ 5*\n\n"
        "1. Опиши свою систему по 6 этапам — что конкретно делаешь на каждом\n"
        "2. Создай контент-план на первый месяц с помощью ИИ\n"
        "3. Запусти первую рабочую неделю по системе прямо сейчас\n\n"
        "Ты сделал практику?",
        parse_mode="Markdown",
        reply_markup=kb(("✅ Да, сделал (+20 баллов)", "p5_yes"), ("⏭ Пропустить", "p5_skip"))
    )
    await cb.answer()

@dp.callback_query(F.data == "p5_yes")
async def p5_yes(cb: CallbackQuery):
    add_score(cb.from_user.id, 20)
    s = get_score(cb.from_user.id)
    await edit_and_send(cb,
        f"🔥 +20 баллов!\n\nТвой итоговый счёт: *{s} баллов*",
        kb(("🎓 Получить результаты →", "finale"))
    )
    await cb.answer()

@dp.callback_query(F.data == "p5_skip")
async def p5_skip(cb: CallbackQuery):
    s = get_score(cb.from_user.id)
    await edit_and_send(cb,
        f"Твой итоговый счёт: *{s} баллов*",
        kb(("🎓 Получить результаты →", "finale"))
    )
    await cb.answer()

# ══════════════════════════════════════════════════════════════
#  ФИНАЛ
# ══════════════════════════════════════════════════════════════
@dp.callback_query(F.data == "finale")
async def finale(cb: CallbackQuery):
    await cb.message.edit_reply_markup()
    name  = cb.from_user.first_name
    score = get_score(cb.from_user.id)

    await cb.message.answer(
        f"🏆 *Поздравляю, {name}!*\n\n"
        "Ты прошёл курс «Как использовать нейросети в маркетинге» до конца.\n\n"
        "🎖 *МАРКЕТОЛОГ ЭПОХИ ИИ*\n"
        "_Ты в топ-5% тех, кто не просто читает про ИИ — а применяет._",
        parse_mode="Markdown"
    )
    await asyncio.sleep(1)

    # ── Логика бонусов ───────────────────────────────────────
    if score == 100:
        bonus = (
            "Ты выполнил *все* практики — это редкость.\n\n"
            "Твой бонус: *скидка 20% на первый месяц ABRA CLUB* 🎁\n"
            "Промокод: `ABRA20`\nДействует 48 часов."
        )
    elif score >= 40:
        bonus = (
            "Ты прошёл курс и сделал часть практик.\n\n"
            "Твой бонус: *скидка 10% на первый месяц ABRA CLUB* 🎁\n"
            "Промокод: `ABRA10`\nДействует 48 часов."
        )
    else:
        bonus = (
            "Ты прошёл курс — и это уже шаг.\n\n"
            "Специально для тебя: *бесплатный первый урок закрытого модуля ABRA CLUB* 🎁"
        )

    await cb.message.answer(
        f"Твой итоговый счёт: *{score} баллов*\n\n{bonus}",
        parse_mode="Markdown"
    )
    await asyncio.sleep(1)

    await cb.message.answer(
        "*ABRA CLUB* — закрытое сообщество, где:\n\n"
        "→ Живые разборы реальных кейсов — не теория\n"
        "→ Инструменты и связки, которые работают прямо сейчас\n"
        "→ Люди, которые продают и делятся опытом\n"
        "→ Доступ к материалам от основателя клуба\n\n"
        "Не курс. Не инфобиз. Живое сообщество практиков.",
        parse_mode="Markdown",
        reply_markup=kb(
            ("🚀 Вступить в ABRA CLUB", "join_club"),
            ("💬 Узнать подробнее", "learn_more")
        )
    )
    await cb.answer()

@dp.callback_query(F.data == "join_club")
async def join_club(cb: CallbackQuery):
    # ⚠️ Замени URL на реальную ссылку
    await cb.message.answer(
        "Ссылка для вступления:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="🚀 Вступить в ABRA CLUB", url="https://t.me/+W9GuYQ-qL_0zNzli")
        ]])
    )
    await cb.answer()

@dp.callback_query(F.data == "learn_more")
async def learn_more(cb: CallbackQuery):
    score = get_score(cb.from_user.id)
    promo = "ABRA20" if score == 100 else ("ABRA10" if score >= 40 else "")
    promo_line = f"\nТвой промокод: `{promo}` — действует 48 часов." if promo else ""

    await cb.message.answer(
        "*ABRA CLUB* — закрытый клуб для тех, кто строит маркетинг и продажи в новых условиях.\n\n"
        "Что внутри:\n"
        "— Еженедельные разборы кейсов\n"
        "— База проверенных инструментов и промптов\n"
        "— Закрытый чат с участниками\n"
        "— Материалы от основателя клуба Артура Абрамова\n\n"
        f"Членство открыто сейчас.{promo_line}",
        parse_mode="Markdown",
        reply_markup=kb(("🚀 Вступить в ABRA CLUB", "join_club"))
    )
    await cb.answer()

# ─── MAIN ────────────────────────────────────────────────────
async def main():
    init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
