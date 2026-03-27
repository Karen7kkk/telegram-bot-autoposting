from aiogram.fsm.state import State, StatesGroup

class CreatePost(StatesGroup):
    waiting_for_topic = State()
    waiting_for_rubric = State()
    waiting_for_channel = State()
    waiting_for_confirm = State()