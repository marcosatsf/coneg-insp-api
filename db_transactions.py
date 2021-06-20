import psycopg2

class PsqlPy:
    def __init__(self) -> None:
        """
        Initialize DB connection, retrieving the current cursor
        to it and set auto-commit ON.
        """
        try:
            self.conn = psycopg2.connect(
                host="db",
                port="5432",
                database="coneg_user",
                user="coneg_user",
                password="conegpass"
            )
            self.conn.set_session(autocommit=True)
            self.cur = self.conn.cursor()
            print('Connected DB!')
        except Exception as e:
            print('Cannot connect to DB!')


    def insert_row(self, **row):
        """
        Insert row to fact table.

        Raises:
            Exception: Cannot insert register.
        """
        if row.get('pessoa'):
            with open('sql/insert_person.sql','r') as f:
                query = f.read()

            try:
                data = (row['local'], row['ts'], row['status'], row['pessoa'], )
                self.cur.execute(query, data)
            except Exception:
                print("Cannot insert on insert_person!")
                raise Exception
        else:
            with open('sql/insert_no_person.sql','r') as f:
                query = f.read()

            try:
                data = (row['local'], row['ts'], row['status'], )
                self.cur.execute(query, data)
            except Exception:
                print("Cannot insert on insert_no_person!")
                raise Exception

    
    def select_query(self, id_person: str):
        with open('sql/select_person.sql','r') as f:
            query = f.read()
        
        try:
            data = (id_person, )
            self.cur.execute(query, data)
            res = self.cur.fetchall()[0]
            return {
                'pesid':res[0],
                'nome':res[1],
                'email':res[2],
                'telefone':res[3],
                'notif':res[4]
            }
        except IndexError:
            return {}
        except Exception:
            print("Cannot select!")
            raise Exception


    def update_query(self, set_value: bool, id_person: str):
        with open('sql/update_status.sql','r') as f:
            query = f.read()
        
        try:
            data = (set_value, id_person, )
            self.cur.execute(query, data)
        except Exception:
            print("Cannot update!")
            raise Exception


    def disconnect(self):
        """
        Invalidate DB connection.
        """
        if self.cur is not None:
            self.cur.close()
        if self.conn is not None:
            self.conn.close()
            print('Disconnected DB!')