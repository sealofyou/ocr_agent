"""初始化数据库"""
from app.db.base import Base, engine
from app.models import User, ScheduleItem, Memo, UploadedFile, TextInput


def init_db():
    """创建所有数据库表"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")


if __name__ == "__main__":
    init_db()
