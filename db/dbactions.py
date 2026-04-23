import sqlite3

class Database:
    def __init__(self, db_path="db/scrapmetal.db"):
        self.db_path = db_path
        self.conn = None
        self.cursor = None
    
    def connect(self):
        self.conn = sqlite3.connect(self.db_path)
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.cursor = self.conn.cursor()

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

    def execute(self, query, params=()):
        self.cursor.execute(query, params)
        return self.cursor

    def commit(self):
        self.conn.commit()

    def create_table_currency(self):
        self.execute("""
            CREATE TABLE IF NOT EXISTS currency (
                id_currency INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT NOT NULL UNIQUE
            );
        """)
        self.commit()

    def create_table_stock(self):
        self.execute("""
            CREATE TABLE IF NOT EXISTS stock (
                id_stock INTEGER PRIMARY KEY AUTOINCREMENT,
                isin TEXT NOT NULL UNIQUE,
                symbol TEXT NOT NULL UNIQUE,
                label TEXT NOT NULL,
                boursorama_url TEXT,
                id_currency INTEGER NOT NULL,
                    
                FOREIGN KEY (id_currency) REFERENCES currency (id_currency)
            );
        """)
        self.commit()

    def create_table_quote_live(self):
        self.execute("""
            CREATE TABLE IF NOT EXISTS quote_live (
                id_live_quote INTEGER PRIMARY KEY AUTOINCREMENT,
                id_stock INTEGER NOT NULL,
                datetime_collect TEXT NOT NULL,
                market_price REAL NOT NULL,
                open REAL,
                high REAL,
                low REAL,
                volume_cumulated INTEGER,
                    
                FOREIGN KEY (id_stock) REFERENCES stock (id_stock) ON DELETE CASCADE
            );
        """)
        self.commit()

    def create_table_quote_daily(self):
        self.execute("""
            CREATE TABLE IF NOT EXISTS quote_daily (
                id_daily_quote INTEGER PRIMARY KEY AUTOINCREMENT,
                id_stock INTEGER NOT NULL,
                date TEXT NOT NULL,
                open REAL,
                high REAL,
                low REAL,
                close REAL,
                volume_total INTEGER,
                     
                FOREIGN KEY (id_stock) REFERENCES stock (id_stock) ON DELETE CASCADE,
                UNIQUE (id_stock, date)
            );
        """)
        self.commit()

    def create_tables(self):
        self.create_table_currency()
        self.create_table_stock()
        self.create_table_quote_live()
        self.create_table_quote_daily()

    def drop_tables(self):
        self.execute("DROP TABLE IF EXISTS quote_live;")
        self.execute("DROP TABLE IF EXISTS quote_daily;")
        self.execute("DROP TABLE IF EXISTS stock;")
        self.execute("DROP TABLE IF EXISTS currency;")
        self.commit()
    
    def recreate_tables(self):
        self.drop_tables()
        self.create_tables()

    def purge_data(self):
        self.execute("DELETE FROM quote_live;")
        self.execute("DELETE FROM quote_daily;")
        self.execute("DELETE FROM stock;")
        self.execute("DELETE FROM currency;")
        self.commit()

    def insert_currency(self, code):
        self.execute("INSERT INTO currency (code) VALUES (?);", (code,))
        self.commit()
        return self.cursor.lastrowid
    
    def insert_stock(self, symbol, label, isin, boursorama_url, id_currency):
        self.execute("""
            INSERT INTO stock (symbol, label, isin, boursorama_url, id_currency) 
            VALUES (?, ?, ?, ?, ?);
        """, (symbol, label, isin, boursorama_url, id_currency))
        self.commit()
        return self.cursor.lastrowid
    
    def insert_quote_live(self, id_stock, datetime_collect, market_price, open=None, high=None, low=None, volume_cumulated=None):
        self.execute("""
            INSERT INTO quote_live (id_stock, datetime_collect, market_price, open, high, low, volume_cumulated) 
            VALUES (?, ?, ?, ?, ?, ?, ?);
        """, (id_stock, datetime_collect, market_price, open, high, low, volume_cumulated))
        self.commit()
        return self.cursor.lastrowid
    
    def insert_quote_daily(self, id_stock, date, open=None, high=None, low=None, close=None, volume_total=None):
        self.execute("""
            INSERT INTO quote_daily (id_stock, date, open, high, low, close, volume_total) 
            VALUES (?, ?, ?, ?, ?, ?, ?);
        """, (id_stock, date, open, high, low, close, volume_total))
        self.commit()
        return self.cursor.lastrowid
    
    
