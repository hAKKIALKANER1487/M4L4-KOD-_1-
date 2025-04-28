import sqlite3
from config import DATABASE

class DB_Manager:
    def __init__(self, database):
        self.database = database
        
    def get_news(self):
        conn = sqlite3.connect(self.database)
        with conn:
            cur = conn.cursor()
            conn.execute("SELECT title, link FROM news") 
            conn.commit()
            return [{"title":row[0], "link":row[1]} for row in cur.fetchall()]



            
if __name__ == '__main__':
    manager = DB_Manager(DATABASE)