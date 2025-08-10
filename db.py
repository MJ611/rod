import sqlite3
import os
import shutil
import datetime
import json

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

    # جدول جديد لتسجيل عمليات الحذف
    c.execute("""
        CREATE TABLE IF NOT EXISTS deletion_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            operation_type TEXT,
            description TEXT,
            deleted_data TEXT,
            deletion_date TEXT
        )
    """)

    conn.commit()
    conn.close()

def log_deletion(operation_type, description, deleted_data):
    """تسجيل عملية حذف في السجل"""
    today = datetime.date.today().isoformat()
    backup_database()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute("""
        INSERT INTO deletion_log (operation_type, description, deleted_data, deletion_date)
        VALUES (?, ?, ?, ?)
    """, (operation_type, description, json.dumps(deleted_data, ensure_ascii=False), today))
    
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

def delete_student(student_id):
    """حذف طالب بشكل آمن"""
    backup_database()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # الحصول على بيانات الطالب قبل الحذف
    c.execute("SELECT * FROM students WHERE id = ?", (student_id,))
    student_data = c.fetchone()
    
    if student_data:
        # حذف الطالب
        c.execute("DELETE FROM students WHERE id = ?", (student_id,))
        
        # حذف المعاملات المرتبطة بالطالب
        c.execute("DELETE FROM transactions WHERE transaction_type = 'تسجيل طالب' AND name = ?", (student_data[1],))
        
        # تسجيل عملية الحذف
        log_data = {
            "id": student_data[0],
            "name": student_data[1],
            "phone": student_data[5],
            "fee": student_data[6],
            "extra_fee": student_data[7]
        }
        
        c.execute("""
            INSERT INTO deletion_log (operation_type, description, deleted_data, deletion_date)
            VALUES (?, ?, ?, ?)
        """, ("حذف طالب", f"حذف الطالب: {student_data[1]}", 
              json.dumps(log_data, ensure_ascii=False), datetime.date.today().isoformat()))
        
        conn.commit()
        conn.close()
        return True
    
    conn.close()
    return False

def delete_expense(expense_id):
    """حذف صرفية بشكل آمن"""
    backup_database()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # الحصول على بيانات الصرفية قبل الحذف
    c.execute("SELECT * FROM expenses WHERE id = ?", (expense_id,))
    expense_data = c.fetchone()
    
    if expense_data:
        # حذف الصرفية
        c.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
        
        # حذف المعاملة المرتبطة
        c.execute("DELETE FROM transactions WHERE transaction_type = 'صرفية' AND name = ? AND amount = ?", 
                 (expense_data[1], expense_data[2]))
        
        # تسجيل عملية الحذف
        log_data = {
            "id": expense_data[0],
            "reason": expense_data[1],
            "amount": expense_data[2],
            "date": expense_data[3]
        }
        
        c.execute("""
            INSERT INTO deletion_log (operation_type, description, deleted_data, deletion_date)
            VALUES (?, ?, ?, ?)
        """, ("حذف صرفية", f"حذف صرفية: {expense_data[1]} - {expense_data[2]} د.ع", 
              json.dumps(log_data, ensure_ascii=False), datetime.date.today().isoformat()))
        
        conn.commit()
        conn.close()
        return True
    
    conn.close()
    return False

def delete_receipt(receipt_id):
    """حذف إيصال بشكل آمن"""
    backup_database()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # الحصول على بيانات الإيصال قبل الحذف
    c.execute("SELECT * FROM receipts WHERE id = ?", (receipt_id,))
    receipt_data = c.fetchone()
    
    if receipt_data:
        # حذف الإيصال
        c.execute("DELETE FROM receipts WHERE id = ?", (receipt_id,))
        
        # حذف المعاملة المرتبطة
        c.execute("DELETE FROM transactions WHERE transaction_type = 'إيصال' AND name = ? AND amount = ?", 
                 (receipt_data[2], receipt_data[1]))
        
        # تسجيل عملية الحذف
        log_data = {
            "id": receipt_data[0],
            "amount": receipt_data[1],
            "note": receipt_data[2],
            "date": receipt_data[3]
        }
        
        c.execute("""
            INSERT INTO deletion_log (operation_type, description, deleted_data, deletion_date)
            VALUES (?, ?, ?, ?)
        """, ("حذف إيصال", f"حذف إيصال: {receipt_data[2]} - {receipt_data[1]} د.ع", 
              json.dumps(log_data, ensure_ascii=False), datetime.date.today().isoformat()))
        
        conn.commit()
        conn.close()
        return True
    
    conn.close()
    return False

def get_deletion_log():
    """الحصول على سجل عمليات الحذف"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        SELECT id, operation_type, description, deleted_data, deletion_date
        FROM deletion_log
        ORDER BY deletion_date DESC, id DESC
    """)
    deletions = c.fetchall()
    conn.close()
    return deletions

def get_statistics_by_period(period_type, start_date=None, end_date=None):
    """الحصول على الإحصائيات حسب الفترة الزمنية"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # تحديد الفترة الزمنية
    if period_type == "daily":
        date_filter = "DATE('now')"
        date_condition = "DATE(register_date) = DATE('now')"
        expense_condition = "DATE(expense_date) = DATE('now')"
        receipt_condition = "DATE(date) = DATE('now')"
    elif period_type == "monthly":
        date_filter = "strftime('%Y-%m', 'now')"
        date_condition = "strftime('%Y-%m', register_date) = strftime('%Y-%m', 'now')"
        expense_condition = "strftime('%Y-%m', expense_date) = strftime('%Y-%m', 'now')"
        receipt_condition = "strftime('%Y-%m', date) = strftime('%Y-%m', 'now')"
    elif period_type == "yearly":
        date_filter = "strftime('%Y', 'now')"
        date_condition = "strftime('%Y', register_date) = strftime('%Y', 'now')"
        expense_condition = "strftime('%Y', expense_date) = strftime('%Y', 'now')"
        receipt_condition = "strftime('%Y', date) = strftime('%Y', 'now')"
    elif period_type == "custom" and start_date and end_date:
        date_condition = f"register_date BETWEEN '{start_date}' AND '{end_date}'"
        expense_condition = f"expense_date BETWEEN '{start_date}' AND '{end_date}'"
        receipt_condition = f"date BETWEEN '{start_date}' AND '{end_date}'"
    else:
        # افتراضي - جميع البيانات
        date_condition = "1=1"
        expense_condition = "1=1" 
        receipt_condition = "1=1"
    
    # إحصائيات الطلاب
    c.execute(f"SELECT COUNT(*) FROM students WHERE {date_condition}")
    student_count = c.fetchone()[0]
    
    c.execute(f"SELECT COUNT(*) FROM students WHERE gender = 'ذكر' AND {date_condition}")
    male_count = c.fetchone()[0]
    
    c.execute(f"SELECT COUNT(*) FROM students WHERE gender = 'أنثى' AND {date_condition}")
    female_count = c.fetchone()[0]
    
    c.execute(f"SELECT SUM(fee), SUM(extra_fee) FROM students WHERE {date_condition}")
    fees_result = c.fetchone()
    total_fees = (fees_result[0] or 0) + (fees_result[1] or 0)
    
    # إحصائيات الصرفيات
    c.execute(f"SELECT COUNT(*), SUM(amount) FROM expenses WHERE {expense_condition}")
    expense_result = c.fetchone()
    expense_count = expense_result[0] or 0
    total_expenses = expense_result[1] or 0
    
    # إحصائيات الإيصالات
    c.execute(f"SELECT COUNT(*), SUM(amount) FROM receipts WHERE {receipt_condition}")
    receipt_result = c.fetchone()
    receipt_count = receipt_result[0] or 0
    total_receipts = receipt_result[1] or 0
    
    # صافي الدخل
    net_income = total_fees + total_receipts - total_expenses
    
    conn.close()
    
    return {
        'students': {
            'total': student_count,
            'males': male_count,
            'females': female_count,
            'total_fees': total_fees
        },
        'expenses': {
            'count': expense_count,
            'total': total_expenses
        },
        'receipts': {
            'count': receipt_count,
            'total': total_receipts
        },
        'summary': {
            'total_income': total_fees + total_receipts,
            'total_expenses': total_expenses,
            'net_income': net_income
        }
    }

def get_monthly_breakdown(year=None):
    """الحصول على تفصيل شهري للإحصائيات"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    if not year:
        year = datetime.date.today().year
    
    monthly_data = {}
    
    for month in range(1, 13):
        month_str = f"{year}-{month:02d}"
        
        # طلاب جدد في الشهر
        c.execute("SELECT COUNT(*) FROM students WHERE strftime('%Y-%m', register_date) = ?", (month_str,))
        students_count = c.fetchone()[0]
        
        # رسوم الطلاب في الشهر
        c.execute("SELECT SUM(fee + extra_fee) FROM students WHERE strftime('%Y-%m', register_date) = ?", (month_str,))
        student_fees = c.fetchone()[0] or 0
        
        # صرفيات الشهر
        c.execute("SELECT SUM(amount) FROM expenses WHERE strftime('%Y-%m', expense_date) = ?", (month_str,))
        month_expenses = c.fetchone()[0] or 0
        
        # إيصالات الشهر
        c.execute("SELECT SUM(amount) FROM receipts WHERE strftime('%Y-%m', date) = ?", (month_str,))
        month_receipts = c.fetchone()[0] or 0
        
        monthly_data[month] = {
            'students_count': students_count,
            'student_fees': student_fees,
            'expenses': month_expenses,
            'receipts': month_receipts,
            'net': student_fees + month_receipts - month_expenses
        }
    
    conn.close()
    return monthly_data

def get_yearly_summary():
    """الحصول على ملخص سنوي"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    current_year = datetime.date.today().year
    
    # إحصائيات السنوات المختلفة
    c.execute("""
        SELECT strftime('%Y', register_date) as year, 
               COUNT(*) as student_count,
               SUM(fee + extra_fee) as total_fees
        FROM students 
        GROUP BY strftime('%Y', register_date)
        ORDER BY year DESC
    """)
    
    yearly_data = c.fetchall()
    conn.close()
    
    return yearly_data

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

def get_all_receipts():
    """الحصول على جميع الإيصالات"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        SELECT id, amount, note, date
        FROM receipts
        ORDER BY date DESC
    """)
    receipts = c.fetchall()
    conn.close()
    return receipts

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
