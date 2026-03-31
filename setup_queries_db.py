import db

def main():
    conn = db.get_connection()
    if not conn:
        print("Failed to connect to setting up queries DB")
        return
        
    cursor = conn.cursor()
    
    try:
        query = """
        CREATE TABLE IF NOT EXISTS contact_queries (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            role VARCHAR(50),
            subject VARCHAR(200) NOT NULL,
            message TEXT NOT NULL,
            status VARCHAR(50) DEFAULT 'Pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            -- We avoid hard foreign key here in case users table varies
        )
        """
        cursor.execute(query)
        conn.commit()
        print("Successfully created 'contact_queries' table.")
    except Exception as e:
        print(f"Error creating queries table: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    main()
