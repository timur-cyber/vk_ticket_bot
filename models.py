from pony.orm import Database, Required, Json

from settings import DB_CONFIG

db = Database()
db.bind(**DB_CONFIG)


class UserState(db.Entity):
    """Состояние пользователя внутри сценария."""
    user_id = Required(str, unique=True)
    scenario_name = Required(str)
    step_name = Required(str)
    context = Required(Json)


class Registration(db.Entity):
    """Заявка на регистрацию"""
    name = Required(str)
    email = Required(str)
    phone_num = Required(str)
    departure = Required(str)
    arrive = Required(str)
    date = Required(str)
    comment = Required(str)
    passengers = Required(str)


db.generate_mapping(create_tables=True)
