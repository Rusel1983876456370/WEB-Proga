"""python -m scripts.init_db — создать БД и исходные записи без запуска HTTP."""
from backend.app.database import engine
from backend.app.seed import init_db

if __name__ == "__main__":
    init_db(engine)
    print("База данных готова. Исходные записи добавляются только при первом запуске.")
