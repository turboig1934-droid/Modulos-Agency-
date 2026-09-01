import sqlite3
import os

print("🔧 Fixing Modulos Agency Database...")

# Check if database exists
if not os.path.exists('modulos.db'):
    print("❌ Database not found! Creating new database...")
    # Create empty database
    conn = sqlite3.connect('modulos.db')
    conn.close()
    print("✅ Empty database created. Run 'py run.py' to initialize.")
    exit()

conn = sqlite3.connect('modulos.db')
cursor = conn.cursor()

# Get existing columns in ads table
cursor.execute("PRAGMA table_info(ads)")
columns = [col[1] for col in cursor.fetchall()]

print(f"📋 Existing columns: {columns}")

# Add missing columns
if 'ad_size' not in columns:
    try:
        cursor.execute("ALTER TABLE ads ADD COLUMN ad_size VARCHAR(50) DEFAULT '728x90'")
        print("✅ Added ad_size column")
    except Exception as e:
        print(f"❌ Error adding ad_size: {e}")

if 'placement' not in columns:
    try:
        cursor.execute("ALTER TABLE ads ADD COLUMN placement VARCHAR(50) DEFAULT 'banner'")
        print("✅ Added placement column")
    except Exception as e:
        print(f"❌ Error adding placement: {e}")

if 'is_popup' not in columns:
    try:
        cursor.execute("ALTER TABLE ads ADD COLUMN is_popup BOOLEAN DEFAULT 0")
        print("✅ Added is_popup column")
    except Exception as e:
        print(f"❌ Error adding is_popup: {e}")

conn.commit()
conn.close()

print("✅ Database updated successfully!")
print("🚀 Run 'py run.py' to start the server.")