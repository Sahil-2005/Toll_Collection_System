import sqlite3
import os

class TollDatabase:
    """
    Handles SQLite database interactions for the toll collection system.
    """
    def __init__(self, db_path="../database/toll_data.db"):
        self.db_path = db_path
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        try:
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self._create_table()
            self._inject_dummy_data()
            print(f"Connected to database successfully at {self.db_path}")
        except sqlite3.Error as e:
            print(f"Database error during initialization: {e}")

    def _create_table(self):
        """Creates the vehicles table if it does not exist."""
        query = '''
        CREATE TABLE IF NOT EXISTS vehicles (
            plate_number TEXT PRIMARY KEY,
            owner TEXT NOT NULL,
            balance REAL NOT NULL
        )
        '''
        cursor = self.conn.cursor()
        cursor.execute(query)
        self.conn.commit()

    def _inject_dummy_data(self):
        """Injects dummy users for testing purposes."""
        dummy_users = [
            ("MH12AB1234", "Alice Smith", 120.0),
            ("MH14HG5678", "Bob Johnson", 30.0), # Low balance
            ("DL1AB9999", "Charlie Brown", 500.0)
        ]
        
        cursor = self.conn.cursor()
        for user in dummy_users:
            cursor.execute('''
            INSERT OR IGNORE INTO vehicles (plate_number, owner, balance)
            VALUES (?, ?, ?)
            ''', user)
        self.conn.commit()

    def process_toll(self, plate_number, toll_amount=50.0):
        """
        Queries the DB for the plate, deducts the toll if balance is sufficient.
        Returns a dict with transaction status.
        """
        try:
            cursor = self.conn.cursor()
            # Prefer the seeded schema used by seed_database.py.
            cursor.execute(
                'SELECT wallet_balance, is_active FROM registered_vehicles WHERE plate_number = ?',
                (plate_number,),
            )
            row = cursor.fetchone()
            table_name = "registered_vehicles"
            balance_column = "wallet_balance"

            # Backward-compatible fallback for legacy schema.
            if row is None:
                cursor.execute('SELECT balance FROM vehicles WHERE plate_number = ?', (plate_number,))
                row = cursor.fetchone()
                table_name = "vehicles"
                balance_column = "balance"
            
            if row is None:
                return {
                    "status": "Error",
                    "msg": "Unregistered",
                    "message": "Unregistered",
                    "updated_balance": None,
                }
                
            balance = row[0]
            if table_name == "registered_vehicles":
                is_active = bool(row[1])
                if not is_active:
                    return {
                        "status": "Failed",
                        "msg": "Inactive Tag",
                        "message": "Inactive Tag",
                        "updated_balance": round(balance, 2),
                    }

            if balance >= toll_amount:
                # Deduct balance
                new_balance = balance - toll_amount
                cursor.execute(
                    f'UPDATE {table_name} SET {balance_column} = ? WHERE plate_number = ?',
                    (new_balance, plate_number),
                )
                self.conn.commit()
                return {
                    "status": "Success",
                    "msg": "Paid",
                    "message": "Paid",
                    "updated_balance": round(new_balance, 2),
                }
            else:
                return {
                    "status": "Failed",
                    "msg": "Low Balance",
                    "message": "Low Balance",
                    "updated_balance": round(balance, 2),
                }
                
        except sqlite3.Error as e:
            print(f"Database operation error: {e}")
            return {
                "status": "Error",
                "msg": "DB Error",
                "message": "DB Error",
                "updated_balance": None,
            }

    def _table_exists(self, table_name):
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name = ? LIMIT 1",
            (table_name,),
        )
        return cursor.fetchone() is not None

    def get_user_by_plate(self, plate_number):
        """Fetch a normalized user payload from either registered_vehicles or legacy vehicles."""
        try:
            cursor = self.conn.cursor()

            if self._table_exists("registered_vehicles"):
                cursor.execute(
                    '''
                    SELECT plate_number, owner_name, wallet_balance, is_active
                    FROM registered_vehicles
                    WHERE plate_number = ?
                    ''',
                    (plate_number,),
                )
                row = cursor.fetchone()
                if row:
                    return {
                        "plate_number": row[0],
                        "owner_name": row[1],
                        "wallet_balance": round(float(row[2]), 2),
                        "is_active": bool(row[3]),
                        "source_table": "registered_vehicles",
                    }

            if self._table_exists("vehicles"):
                cursor.execute(
                    '''
                    SELECT plate_number, owner, balance
                    FROM vehicles
                    WHERE plate_number = ?
                    ''',
                    (plate_number,),
                )
                row = cursor.fetchone()
                if row:
                    return {
                        "plate_number": row[0],
                        "owner_name": row[1],
                        "wallet_balance": round(float(row[2]), 2),
                        "is_active": True,
                        "source_table": "vehicles",
                    }

            return None
        except sqlite3.Error as e:
            print(f"Database operation error: {e}")
            return None

    def get_all_users(self):
        """Return a normalized list of users for frontend verification."""
        users = []
        try:
            cursor = self.conn.cursor()

            if self._table_exists("registered_vehicles"):
                cursor.execute(
                    '''
                    SELECT plate_number, owner_name, wallet_balance, is_active
                    FROM registered_vehicles
                    ORDER BY plate_number
                    '''
                )
                rows = cursor.fetchall()
                users.extend(
                    {
                        "plate_number": row[0],
                        "owner_name": row[1],
                        "wallet_balance": round(float(row[2]), 2),
                        "is_active": bool(row[3]),
                        "source_table": "registered_vehicles",
                    }
                    for row in rows
                )

            # Include legacy users that are not already present in registered_vehicles.
            existing_plates = {user["plate_number"] for user in users}
            if self._table_exists("vehicles"):
                cursor.execute(
                    '''
                    SELECT plate_number, owner, balance
                    FROM vehicles
                    ORDER BY plate_number
                    '''
                )
                rows = cursor.fetchall()
                for row in rows:
                    if row[0] in existing_plates:
                        continue
                    users.append(
                        {
                            "plate_number": row[0],
                            "owner_name": row[1],
                            "wallet_balance": round(float(row[2]), 2),
                            "is_active": True,
                            "source_table": "vehicles",
                        }
                    )

            return users
        except sqlite3.Error as e:
            print(f"Database operation error: {e}")
            return []

    def __del__(self):
        """Close the DB connection when object is destroyed."""
        if hasattr(self, 'conn'):
            self.conn.close()
