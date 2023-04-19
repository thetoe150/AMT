import sqlite3

if __name__ == '__main__':
        
        conn = sqlite3.connect('air_monitoring.db')

        c = conn.cursor()

        c.execute(""" CREATE TABLE IF NOT EXIST air (
                category TEXT,
                concentration FLOAT 
                )""")

        # c.execute("""INSERT INTO air 
                # VALUES ('NO2', 34.55)""")

        c.execute("INSERT INTO air VALUES (:category, :concentration)", {'category': 'SO2', 'concentration': 11.3})
        conn.commit()

        c.execute("SELECT * FROM air WHERE category = :category", {'category': 'SO2'})
        print(c.fetchall())

        conn.commit()
        conn.close()