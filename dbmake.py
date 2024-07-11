import sqlite3

# Step 1: Define the database schema
# This is conceptual and guides the next steps

# Step 2: Connect to the SQLite database
conn = sqlite3.connect('yourdatabase.db')  # This will create 'example.db' if it doesn't exist

# Step 3: Create the `users` table
create_table_query = '''
CREATE TABLE IF NOT EXISTS users (
    email TEXT PRIMARY KEY,
    role TEXT NOT NULL
)
'''
conn.execute(create_table_query)

# Step 4: Insert an admin user
# Replace 'admin@example.com' with the desired admin email
admin_email = '18'
admin_role = 'admin'
insert_query = 'INSERT INTO users (email, role) VALUES (?, ?)'
try:
    conn.execute(insert_query, (admin_email, admin_role))
    conn.commit()  # Commit the transaction
    print("Admin user created successfully.")
except sqlite3.IntegrityError:
    print("Admin user already exists.")
except Exception as e:
    print(f"An error occurred: {e}")
finally:
    conn.close()  # Close the connection