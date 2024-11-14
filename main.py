import psycopg2

class Table():
    """
    Класс Table - создает бызу данных, состоящую их двух таблиц clients, phones
    """
    def __init__(self, database: str, user: str, password: str) -> None:
        """
        :param database: название БД
        :param user: имя пользователя
        :param password: пароль
        """
        self.database = database
        self.user = user
        self.password = password

    def __get_connection(self) -> None:
        """
        Метод класса создает соединение с БД
        :return:
        """
        connection = psycopg2.connect(database=self.database, user=self.user, password=self.password)
        return connection

    def create_table(self) -> None:
        """
        Метод класса создает таблицы:
        clients: содержит данные о клиентах (PK-id-клиента, имя, фамилия, эл.почта). Имеет связь "один кл многим" с таблиец phones
        phones: содерит данные о номерах телефонов клиента (PK-id-номера, FK-id-клиента, номер телефона)
        """
        with self.__get_connection() as conn:
            with conn.cursor() as cur:

                cur.execute("""
                    DROP TABLE phones;
                    DROP TABLE clients;
                """)

                cur.execute("""
                    CREATE TABLE IF NOT EXISTS clients (
                        id_client SERIAL PRIMARY KEY,
                        first_name VARCHAR(30) NOT NULL,
                        last_name VARCHAR(30) NOT NULL,
                        email VARCHAR(50) UNIQUE NOT NULL,
                            CONSTRAINT chk_first_name CHECK (first_name !~ '[0-9]'),
                            CONSTRAINT chk_last_name CHECK (last_name !~ '[0-9]'),
                            CONSTRAINT chk_email CHECK (email LIKE '%@%')
                    );
                """)

                cur.execute("""
                    CREATE TABLE IF NOT EXISTS phones (
                        id_phone SERIAL PRIMARY KEY,
                        id_client SERIAL NOT NULL,
                        phone_number VARCHAR(11),
                            FOREIGN KEY (id_client) REFERENCES clients(id_client),
                            CONSTRAINT chk_phone_number CHECK (phone_number ~ '[0-9]{11}$')
                    );
                """)

                conn.commit()

    def __get_id_client(self, email: str) -> int:
        """
        Метод класса для определения id-клиента по email
        :param email: эл.почта
        :return: id-клиента
        """
        with self.__get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT id_client FROM clients WHERE email=%s;
                """, (email,))
                result = cur.fetchone()[0]
                return result

    def __make_change(self, id: int, field: str, info: str) -> None:
        """
        Метод класса для внесения изменений ифнормации клиента,
        запрашивает у клиента данные, проверяет значение поля и менят данные
        :param id: id-клиента
        :param field: поле для замены
        :param info: информация для замены
        """
        with self.__get_connection() as conn:
            if field == 'name':
                with conn.cursor() as cur:
                    cur.execute("""
                        UPDATE clients SET first_name=%s WHERE id_client=%s
                    """, (info, id))
                    conn.commit()
            elif field == 'lastname':
                with conn.cursor() as cur:
                    cur.execute("""
                        UPDATE clients SET last_name=%s WHERE id_client=%s
                    """, (info, id))
                    conn.commit()
            elif field == 'email':
                with conn.cursor() as cur:
                    cur.execute("""
                        UPDATE clients SET email=%s WHERE id_client=%s
                    """, (info, id))
                    conn.commit()
            else:
                print('Введено некоректное поле, попробуйте еще раз')
                self.change_info()

    def add_client(self, first_name: str, last_name: str, email: str, phone_number='') -> None:
        """
        Метод класса для добавления в БД клиента. Проверяет внесение данных о номере телфона,
        в случае наличия вносит в БД.
        :param first_name: имя клиента
        :param last_name: фамилия клиента
        :param email: эл.почта
        :param phone_number: номер телефона клиента. Значение по умолчанию.
        """
        with self.__get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO clients(first_name, last_name, email) VALUES(%s, %s, %s);
                """, (first_name, last_name, email))
                conn.commit()

                if phone_number != '':
                    id_client = self.__get_id_client(email)

                    cur.execute("""
                        INSERT INTO phones(id_client, phone_number) VALUES(%s, %s);
                    """, (id_client, phone_number))
                    conn.commit()

    def add_phone_number(self, email: str, phone_number: str) -> None:
        """
        Метод класса, добавляет номер телефона клиенту, находит id-клиента по email
        :param email: эл.почта
        :param phone_number: номер телефона
        """
        with self.__get_connection() as conn:
            with conn.cursor() as cur:
                id_client = self.__get_id_client(email)

                cur.execute("""
                    INSERT INTO phones(id_client, phone_number) VALUES(%s, %s);
                """, (id_client, phone_number))
                conn.commit()

    def change_info(self) -> None:
        """
        Метод класса для вызова метода __make_change.
        Заправшивает атрибуты для внесения изменений
        """
        id = int(input('Введите id клиента: '))
        field = input('Введите поле (name, lastname, email): ')
        info = input('Введите изменение: ')
        self.__make_change(id, field, info)

    def dlt_phone_number(self, id: int, number: str) -> None:
        """
        Метод класса, удаляет номер телефона из БД
        :param id: id-клиента
        :param number: номер телефона
        """
        with self.__get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                DELETE FROM phones WHERE id_client=%s AND phone_number=%s
                """, (id, number))
                conn.commit()

    def dlt_client(self, id: int) -> None:
        """
        Метод класса, удаляет клинта из БД по id
        :param id: id-клиента
        """
        with self.__get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                DELETE FROM phones WHERE id_client=%s;
                """, (id,))
                conn.commit()

            with conn.cursor() as cur:
                cur.execute("""
                DELETE FROM clients WHERE id_client=%s;
                """, (id,))
                conn.commit()

    def search_client(self, info: str) -> None:
        """
        Метод класса для вывода информации о клиенте из БД по заданному значению
        :param info: информация для поиска коиента
        """
        with self.__get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT c.id_client, c.first_name, c.last_name, c.email, p.phone_number FROM clients c
                    LEFT JOIN phones p ON c.id_client = p.id_client WHERE (c.first_name=%s OR c.last_name=%s 
                    OR c.email=%s OR p.phone_number=%s);
                """, (info, info, info, info))
                print('Данные клиента:', cur.fetchone())

    def get_data(self) -> None:
        """
        Метод класса для вывода всей информации из БД
        """
        with self.__get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT c.id_client, c.first_name, c.last_name, c.email, p.phone_number FROM clients c
                    LEFT JOIN phones p ON c.id_client = p.id_client;
                """)
                print('Данные клиентов:', cur.fetchall())

table = Table('clients', 'postgres', 'Ваш пароль')
table.create_table()
table.add_client('Семен', 'Семенов', 'вавп@дывд.во')
table.add_client('Иван', 'Иванов', 'выапывпывпп@дывд.во', '89001111111')
table.add_client('Петя', 'Петров', '1235пп@дывд.во', '89002222222')
table.add_phone_number('1235пп@дывд.во', '89004444444')
table.get_data()
table.change_info()
table.get_data()
table.dlt_phone_number(3, '89004444444')
table.get_data()
table.dlt_client(3)
table.get_data()
table.search_client('Иван')
