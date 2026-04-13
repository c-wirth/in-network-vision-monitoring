from core.db_infrastructure.db_interface import DBInterface

db = DBInterface()
clips = db.get_all_clips()

print(clips)