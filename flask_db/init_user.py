from app import db, User

db.create_all()

user1 = User("test_user1@example.com", "test_user1", "111")
user2 = User("test_user2@example.com", "test_user2", "222")

db.session.add_all([user1, user2])
db.session.commit()

print(f"ユーザーの追加が完了しました。{user1}, {user2}")