import db

def main():
    conn = db.get_connection()
    if not conn:
        print("Failed to connect to setting up reviews DB")
        return
        
    cursor = conn.cursor()
    
    try:
        # Check if users table is actually 'users'
        cursor.execute("SHOW TABLES LIKE 'user'")
        if cursor.fetchone():
            users_table = "user"
        else:
            users_table = "users"
            
        print(f"Using users table: {users_table}")

        query = f"""
        CREATE TABLE IF NOT EXISTS reviews (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            user_name VARCHAR(100),
            rating INT NOT NULL,
            comment TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            -- We avoid hard foreign key here in case users table varies
        )
        """
        cursor.execute(query)
        conn.commit()
        print("Reviews table created or already exists!")
    except Exception as e:
        print("Error creating reviews table:", e)
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    main()
