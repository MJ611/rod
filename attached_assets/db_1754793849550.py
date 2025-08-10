import sqlite3
import os
import shutil
import datetime

# تحديد مجلد لحفظ قاعدة البيانات
BASE_DIR = os.path.expanduser("~/RodaQaterData")
os.makedirs(BASE_DIR, exist_ok=True)

DB_PATH = os.path.join(BASE_DIR, "school.db")
BACKUP_DIR = os.path.join(BASE_DIR, "backups")
os.makedirs(BACKUP_DIR, exist_ok=True)

def backup_database():
    """إنشاء نسخة احتياطية تلقائية مع التاريخ والوقت"""
    if os.path.exists(DB_PATH):
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = os.path.join(BACKUP_DIR, f"school_backup_{timestamp}.db")
        shutil.copy2(DB_PATH, backup_file)

def connect_db():
    """إنشاء قاعدة البيانات والجداول"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            birthdate TEXT,
            gender TEXT,
            address TEXT,
            phone TEXT,
            fee REAL,
            extra_fee REAL,
            register_date TEXT,
            notes TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            reason TEXT,
            amount REAL,
            expense_date TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS receipts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL,
            note TEXT,
            date TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_type TEXT,
            name TEXT,
            amount REAL,
            transaction_date TEXT
        )
    """)

    conn.commit()
    conn.close()

def insert_student(name, birthdate, gender, address, phone, fee, extra_fee, register_date=None):
    """إضافة طالب جديد"""
    if register_date is None:
        register_date = datetime.date.today().isoformat()
    
    backup_database()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # إضافة الطالب
    c.execute("""
        INSERT INTO students (name, birthdate, gender, address, phone, fee, extra_fee, register_date, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (name, birthdate, gender, address, phone, fee, extra_fee, register_date, ""))
    
    # تسجيل المعاملة
    total_amount = fee + extra_fee
    c.execute("""
        INSERT INTO transactions (transaction_type, name, amount, transaction_date)
        VALUES (?, ?, ?, ?)
    """, ("تسجيل طالب", name, total_amount, register_date))
    
    conn.commit()
    conn.close()

def insert_expense(amount, reason):
    """إضافة صرفية جديدة"""
    today = datetime.date.today().isoformat()
    backup_database()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute("INSERT INTO expenses (reason, amount, expense_date) VALUES (?, ?, ?)", 
              (reason, amount, today))
    
    c.execute("""
        INSERT INTO transactions (transaction_type, name, amount, transaction_date)
        VALUES (?, ?, ?, ?)
    """, ("صرفية", reason, amount, today))
    
    conn.commit()
    conn.close()

def insert_receipt(amount, note):
    """إضافة إيصال جديد"""
    today = datetime.date.today().isoformat()
    backup_database()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute("INSERT INTO receipts (amount, note, date) VALUES (?, ?, ?)", 
              (amount, note, today))
    
    c.execute("""
        INSERT INTO transactions (transaction_type, name, amount, transaction_date)
        VALUES (?, ?, ?, ?)
    """, ("إيصال", note, amount, today))
    
    conn.commit()
    conn.close()

def get_total_students_count():
    """الحصول على العدد الكلي للطلاب"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM students")
    result = c.fetchone()[0]
    conn.close()
    return result

def get_students_count_today():
    """الحصول على عدد الطلاب المسجلين اليوم"""
    today = datetime.date.today().isoformat()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM students WHERE register_date = ?", (today,))
    result = c.fetchone()[0]
    conn.close()
    return result

def get_income_summary():
    """الحصول على ملخص الإيرادات (يومي، شهري، سنوي)"""
    today = datetime.date.today().isoformat()
    this_month = today[:7]
    this_year = today[:4]

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # إيرادات اليوم
    c.execute("SELECT SUM(amount) FROM transactions WHERE transaction_type = 'تسجيل طالب' AND transaction_date = ?", (today,))
    daily = c.fetchone()[0] or 0

    # إيرادات الشهر
    c.execute("SELECT SUM(amount) FROM transactions WHERE transaction_type = 'تسجيل طالب' AND transaction_date LIKE ?", (f"{this_month}%",))
    monthly = c.fetchone()[0] or 0

    # إيرادات السنة
    c.execute("SELECT SUM(amount) FROM transactions WHERE transaction_type = 'تسجيل طالب' AND transaction_date LIKE ?", (f"{this_year}%",))
    yearly = c.fetchone()[0] or 0

    conn.close()
    return daily, monthly, yearly

def get_expenses_today():
    """الحصول على صرفيات اليوم"""
    today = datetime.date.today().isoformat()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT SUM(amount) FROM expenses WHERE expense_date = ?", (today,))
    result = c.fetchone()[0]
    conn.close()
    return result if result else 0

def get_all_students():
    """الحصول على جميع الطلاب"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        SELECT id, name, birthdate, gender, address, phone, fee, extra_fee, register_date
        FROM students
        ORDER BY register_date DESC
    """)
    students = c.fetchall()
    conn.close()
    return students

def get_all_expenses():
    """الحصول على جميع الصرفيات"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        SELECT id, amount, reason, expense_date
        FROM expenses
        ORDER BY expense_date DESC
    """)
    expenses = c.fetchall()
    conn.close()
    return expenses

def get_gender_stats():
    """الحصول على إحصائيات الجنس"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM students WHERE gender = 'ذكر'")
    males = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM students WHERE gender = 'أنثى'")
    females = c.fetchone()[0]
    conn.close()
    return males, females

def get_transaction_log():
    """الحصول على سجل المعاملات"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        SELECT transaction_date, transaction_type, amount, name
        FROM transactions
        ORDER BY transaction_date DESC, id DESC
    """)
    transactions = c.fetchall()
    conn.close()
    return transactions

def get_daily_transactions():
    """الحصول على معاملات اليوم"""
    today = datetime.date.today().isoformat()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        SELECT transaction_type, name, amount FROM transactions 
        WHERE transaction_date = ? 
        ORDER BY id DESC
    """, (today,))
    rows = c.fetchall()
    conn.close()
    return rows

def make_backup():
    """إنشاء نسخة احتياطية يدوية"""
    backup_database()

# تهيئة قاعدة البيانات عند الاستيراد
connect_db()

# للتوافق مع الكود القديم
def get_total_students():
    return get_total_students_count()

def get_today_students():
    return get_students_count_today()

def get_students_by_gender():
    males, females = get_gender_stats()
    return [("ذكر", males), ("أنثى", females)]

def add_student(name, birthdate, gender, address, phone, fee, extra_fee, register_date, notes):
    insert_student(name, birthdate, gender, address, phone, fee, extra_fee, register_date)

def add_expense(reason, amount, expense_date):
    insert_expense(amount, reason)

# متغيرات للتوافق
DB_NAME = DB_PATH