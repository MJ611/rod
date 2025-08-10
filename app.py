import streamlit as st
import pandas as pd
import os
from datetime import date, datetime
from db import (connect_db, get_total_students_count, get_students_count_today, 
                get_income_summary, get_all_students, insert_expense, get_expenses_today, 
                get_all_expenses, get_gender_stats, get_transaction_log, get_daily_transactions, 
                insert_receipt, make_backup, DB_PATH, BACKUP_DIR, delete_student, 
                delete_expense, delete_receipt, get_all_receipts, get_deletion_log,
                get_statistics_by_period, get_monthly_breakdown, get_yearly_summary)
from register import show_register_form
from pdf_generator import create_students_report_pdf, create_financial_report_pdf, create_student_admission_receipt_pdf
from deletion_manager import show_deletion_confirmation, show_student_deletion_section, show_expense_deletion_section, show_receipt_deletion_section

# إعداد الصفحة
st.set_page_config(
    page_title="نظام روضة قطر الندى الأهلية",
    page_icon="🌟",
    layout="wide",
    initial_sidebar_state="expanded"
)

# تنسيق CSS مخصص
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #1f4e79, #2d6ba3, #3b82f6);
        padding: 2.5rem;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 8px 25px rgba(31, 78, 121, 0.4);
        position: relative;
        overflow: hidden;
    }
    
    .main-header::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: linear-gradient(45deg, transparent, rgba(255,255,255,0.1), transparent);
        animation: shimmer 3s infinite;
    }
    
    @keyframes shimmer {
        0% { transform: translateX(-100%) translateY(-100%) rotate(45deg); }
        100% { transform: translateX(100%) translateY(100%) rotate(45deg); }
    }
    
    .metric-card {
        background: linear-gradient(135deg, #ffffff, #f8fafc);
        padding: 2rem;
        border-radius: 16px;
        border: 2px solid #e2e8f0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        text-align: center;
        margin: 0.5rem 0;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .metric-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 20px rgba(31, 78, 121, 0.15);
        border-color: #3b82f6;
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 4px;
        background: linear-gradient(90deg, #1f4e79, #3b82f6, #10b981);
        animation: gradientMove 3s ease infinite;
    }
    
    @keyframes gradientMove {
        0%, 100% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
    }
    
    .feature-box {
        background: linear-gradient(135deg, #f8fafc, #e2e8f0);
        border: 1px solid #cbd5e0;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    .success-box {
        background: linear-gradient(135deg, #f0fff4, #c6f6d5);
        border: 1px solid #9ae6b4;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    
    .info-box {
        background: linear-gradient(135deg, #ebf8ff, #bee3f8);
        border: 1px solid #90cdf4;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    
    .warning-box {
        background: linear-gradient(135deg, #fffbeb, #fed7aa);
        border: 1px solid #fdba74;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    
    .danger-box {
        background: linear-gradient(135deg, #fef2f2, #fecaca);
        border: 1px solid #f87171;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    
    .login-container {
        background: white;
        border-radius: 20px;
        padding: 3rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        border: 1px solid #e2e8f0;
    }
    
    .arabic-text {
        direction: rtl;
        text-align: right;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    .stats-container {
        background: white;
        border-radius: 12px;
        padding: 2rem;
        margin: 1rem 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.08);
    }
    
    .section-header {
        color: #1f4e79;
        font-weight: bold;
        border-bottom: 2px solid #1f4e79;
        padding-bottom: 0.5rem;
        margin-bottom: 1.5rem;
    }
    
    .delete-button {
        background: linear-gradient(135deg, #dc2626, #ef4444) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.5rem 1rem !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
    }
    
    .delete-button:hover {
        background: linear-gradient(135deg, #b91c1c, #dc2626) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 15px rgba(220, 38, 38, 0.3) !important;
    }
    
    .confirmation-dialog {
        background: linear-gradient(135deg, #fef2f2, #fee2e2);
        border: 2px solid #fca5a5;
        border-radius: 15px;
        padding: 2rem;
        margin: 1rem 0;
        text-align: center;
    }
    
    .stButton > button {
        border-radius: 8px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
    }
    
    .stMetric {
        background: white;
        padding: 1rem;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    .stMetric:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(0,0,0,0.15);
    }
    
    .quick-action-card {
        background: linear-gradient(135deg, #ffffff, #f8fafc);
        border: 2px solid #e2e8f0;
        border-radius: 15px;
        padding: 1.5rem;
        text-align: center;
        transition: all 0.3s ease;
        cursor: pointer;
        height: 100%;
    }
    
    .quick-action-card:hover {
        border-color: #1f4e79;
        box-shadow: 0 8px 25px rgba(31, 78, 121, 0.15);
        transform: translateY(-3px);
    }
    
    .action-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
        display: block;
    }
    
    .card-container {
        background: white;
        border-radius: 15px;
        padding: 2rem;
        margin: 1rem 0;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        border: 1px solid #e2e8f0;
    }
    
    .data-table {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    
    .sidebar-logo {
        text-align: center;
        margin-bottom: 1.5rem;
        padding: 1.5rem;
        background: linear-gradient(135deg, #f0f4f8, #e2e8f0);
        border-radius: 15px;
        border: 2px solid #cbd5e1;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
    }
    
    .deletion-warning {
        background: linear-gradient(135deg, #fef2f2, #fecaca);
        border: 2px solid #f87171;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        text-align: center;
        color: #dc2626;
        font-weight: bold;
    }
    
    .deletion-success {
        background: linear-gradient(135deg, #f0fff4, #c6f6d5);
        border: 2px solid #10b981;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        text-align: center;
        color: #047857;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# إنشاء قاعدة البيانات عند بدء التشغيل
connect_db()

# نظام تسجيل الدخول
def check_login():
    """التحقق من تسجيل الدخول"""
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    
    if not st.session_state.logged_in:
        # عرض شعار وترحيب جميل
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            # تصميم مربع تسجيل الدخول المحسن والواضح
            st.markdown("""
            <div style="background: linear-gradient(135deg, #ffffff, #f8fafc); 
                       padding: 3rem 2rem; border-radius: 25px; 
                       box-shadow: 0 15px 35px rgba(0,0,0,0.1);
                       border: 3px solid #e2e8f0; text-align: center;">
            """, unsafe_allow_html=True)
            
            # عرض اللوجو في الوسط
            logo_col1, logo_col2, logo_col3 = st.columns([1, 1, 1])
            with logo_col2:
                try:
                    st.image("logo.jpg", width=150)
                except:
                    st.markdown("""
                    <div style="background: linear-gradient(45deg, #1f4e79, #2d6ba3); 
                               width: 120px; height: 120px; border-radius: 50%; 
                               display: inline-flex; align-items: center; justify-content: center;
                               color: white; font-size: 3rem; margin: 0 auto 2rem auto;
                               box-shadow: 0 15px 30px rgba(31, 78, 121, 0.4);
                               border: 4px solid white;">
                        🌟
                    </div>
                    """, unsafe_allow_html=True)
            
            # عنوان الروضة
            st.markdown("""
            <div style="text-align: center; margin-bottom: 2rem;">
                <h1 style="color: #1f4e79; font-size: 2.5rem; margin-bottom: 0.5rem; font-weight: bold;">
                    روضة قطر الندى الأهلية
                </h1>
                <p style="color: #64748b; font-size: 1.2rem; margin: 0;">
                    نظام إدارة شامل ومتطور ✨
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # نموذج تسجيل الدخول
            with st.form("login_form"):
                st.markdown("""
                <div style="background: rgba(255, 255, 255, 0.7); 
                           padding: 2rem; border-radius: 15px; margin-bottom: 1rem;">
                """, unsafe_allow_html=True)
                
                username = st.text_input(
                    "👤 اسم المستخدم", 
                    placeholder="أدخل اسم المستخدم",
                    help="استخدم: mj"
                )
                
                password = st.text_input(
                    "🔑 كلمة المرور", 
                    type="password", 
                    placeholder="أدخل كلمة المرور",
                    help="استخدم: 0"
                )
                
                st.markdown('</div>', unsafe_allow_html=True)
                
                # زر تسجيل الدخول
                submitted = st.form_submit_button(
                    "🚀 دخول إلى النظام", 
                    use_container_width=True, 
                    type="primary"
                )
                
                # التحقق من بيانات تسجيل الدخول
                if submitted:
                    if username == "admin" and password == "1234":
                        st.session_state.logged_in = True
                        st.balloons()
                        st.success("✅ تم تسجيل الدخول بنجاح! مرحباً بك في النظام")
                        st.rerun()
                    else:
                        st.error("❌ اسم المستخدم أو كلمة المرور غير صحيحة")
            
            # معلومات إضافية
            st.markdown("""
            <div style="background: linear-gradient(135deg, #f0f9ff, #e0f2fe); 
                       padding: 1rem; border-radius: 12px; margin-top: 1rem;
                       border: 1px solid #0ea5e9;">
                <p style="color: #0369a1; margin: 0; font-size: 0.9rem; text-align: center;">
                    💡 للوصول التجريبي استخدم:<br>
                    <strong>المستخدم:</strong>  | <strong>كلمة المرور:</strong> 
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        return False
    
    return True

# التحقق من تسجيل الدخول قبل عرض التطبيق
if not check_login():
    st.stop()

# الشريط الجانبي
with st.sidebar:
    # شعار الروضة في الشريط الجانبي
    st.markdown('<div class="sidebar-logo">', unsafe_allow_html=True)
    try:
        st.image("logo.jpg", width=100)
    except:
        st.markdown("""
        <div style="background: linear-gradient(45deg, #1f4e79, #2d6ba3); 
                   width: 80px; height: 80px; border-radius: 50%; 
                   display: flex; align-items: center; justify-content: center;
                   color: white; font-size: 2rem; margin: 0 auto;
                   box-shadow: 0 8px 20px rgba(31, 78, 121, 0.4);">
            🌟
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("""
    <h3 style="text-align: center; color: #1f4e79; margin: 1rem 0 0 0; font-weight: bold;">
        روضة قطر الندى
    </h3>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # زر تسجيل الخروج
    if st.button("🚪 تسجيل خروج", use_container_width=True, type="secondary"):
        st.session_state.logged_in = False
        st.rerun()
    
    st.divider()
    
    # قائمة التنقل
    page = st.selectbox(
        "🧭 اختر القسم:",
        [
            "🏠 الرئيسية",
            "📝 تسجيل طالب جديد",
            "👥 إدارة الطلاب",
            "💰 الصرفيات والإيصالات",
            "🗑️ إدارة الحذف",
            "📊 التقارير المالية",
            "📋 سجل المعاملات",
            "💾 النسخ الاحتياطية"
        ]
    )

# المحتوى الرئيسي
if page == "🏠 الرئيسية":
    # الرأس الرئيسي
    st.markdown("""
    <div class="main-header">
        <h1 style="margin: 0; font-size: 3rem; font-weight: bold;">
            🌟 روضة قطر الندى الأهلية
        </h1>
        <p style="margin: 0.5rem 0 0 0; font-size: 1.3rem; opacity: 0.9;">
            نظام إدارة شامل ومتطور للروضة
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # اختيار الفترة الزمنية للإحصائيات
    st.markdown('<h2 class="section-header">📊 الإحصائيات حسب الفترة الزمنية</h2>', unsafe_allow_html=True)
    
    col_period, col_custom = st.columns([3, 2])
    
    with col_period:
        period_type = st.selectbox(
            "اختر الفترة الزمنية:",
            ["daily", "monthly", "yearly", "all", "custom"],
            format_func=lambda x: {
                "daily": "📅 اليوم",
                "monthly": "📆 هذا الشهر", 
                "yearly": "🗓️ هذه السنة",
                "all": "📋 جميع البيانات",
                "custom": "🔧 فترة مخصصة"
            }[x],
            index=1  # افتراضي شهري
        )
    
    start_date = end_date = None
    if period_type == "custom":
        with col_custom:
            col_start, col_end = st.columns(2)
            with col_start:
                start_date = st.date_input("من تاريخ", value=date.today().replace(day=1))
            with col_end:
                end_date = st.date_input("إلى تاريخ", value=date.today())
    
    # الحصول على الإحصائيات
    if period_type == "all":
        stats = get_statistics_by_period("all")
    else:
        stats = get_statistics_by_period(
            period_type, 
            start_date.isoformat() if start_date else None,
            end_date.isoformat() if end_date else None
        )
    
    # عرض الإحصائيات الرئيسية
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric(
            label="👥 إجمالي الطلاب",
            value=f"{stats['students']['total']:,}",
            delta=f"📊 للفترة المحددة"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric(
            label="👦 الذكور",
            value=f"{stats['students']['males']:,}",
            delta=f"{(stats['students']['males']/stats['students']['total']*100):.1f}%" if stats['students']['total'] > 0 else "0%"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric(
            label="👧 الإناث",
            value=f"{stats['students']['females']:,}",
            delta=f"{(stats['students']['females']/stats['students']['total']*100):.1f}%" if stats['students']['total'] > 0 else "0%"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric(
            label="💸 إجمالي الصرفيات",
            value=f"{stats['expenses']['total']:,.0f} د.ع",
            delta=f"📊 {stats['expenses']['count']} عملية"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.divider()
    
    # الملخص المالي
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="success-box">', unsafe_allow_html=True)
        st.metric(
            label="💰 إجمالي الإيرادات",
            value=f"{stats['summary']['total_income']:,.0f} د.ع",
            delta="رسوم + إيصالات"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="info-box">', unsafe_allow_html=True)
        st.metric(
            label="📈 المصروفات",
            value=f"{stats['summary']['total_expenses']:,.0f} د.ع",
            delta=f"{stats['expenses']['count']} عملية"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        net_color = "success-box" if stats['summary']['net_income'] >= 0 else "error-box"
        st.markdown(f'<div class="{net_color}">', unsafe_allow_html=True)
        st.metric(
            label="💹 صافي الدخل",
            value=f"{stats['summary']['net_income']:,.0f} د.ع",
            delta="الفرق بين الإيرادات والمصروفات"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.divider()
    
    # إحصائيات تفصيلية إضافية
    if period_type == "monthly":
        st.markdown('<h3 class="section-header">📅 التفصيل الشهري لهذه السنة</h3>', unsafe_allow_html=True)
        
        # الحصول على البيانات الشهرية
        monthly_data = get_monthly_breakdown()
        
        # تحضير البيانات للعرض
        months_names = [
            "يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو",
            "يوليو", "أغسطس", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر"
        ]
        
        # عرض البيانات في جدول
        monthly_df_data = []
        for month in range(1, 13):
            data = monthly_data.get(month, {})
            monthly_df_data.append({
                "الشهر": months_names[month-1],
                "طلاب جدد": data.get('students_count', 0),
                "رسوم الطلاب": f"{data.get('student_fees', 0):,.0f}",
                "إيصالات": f"{data.get('receipts', 0):,.0f}",
                "صرفيات": f"{data.get('expenses', 0):,.0f}",
                "صافي الدخل": f"{data.get('net', 0):,.0f}"
            })
        
        if monthly_df_data:
            monthly_df = pd.DataFrame(monthly_df_data)
            st.dataframe(monthly_df, use_container_width=True, hide_index=True)
    
    elif period_type == "yearly":
        st.markdown('<h3 class="section-header">🗓️ ملخص السنوات</h3>', unsafe_allow_html=True)
        
        # الحصول على الملخص السنوي
        yearly_data = get_yearly_summary()
        
        if yearly_data:
            yearly_df_data = []
            for year_info in yearly_data:
                yearly_df_data.append({
                    "السنة": year_info[0],
                    "عدد الطلاب": year_info[1],
                    "إجمالي الرسوم": f"{year_info[2]:,.0f} د.ع"
                })
            
            yearly_df = pd.DataFrame(yearly_df_data)
            st.dataframe(yearly_df, use_container_width=True, hide_index=True)
    
    st.divider()
    
    # الإجراءات السريعة
    st.markdown('<h2 class="section-header">⚡ الإجراءات السريعة</h2>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📝 تسجيل طالب جديد", use_container_width=True, type="primary"):
            st.session_state.navigation = "تسجيل طالب جديد"
            st.rerun()
    
    with col2:
        if st.button("💰 إضافة صرفية", use_container_width=True):
            st.session_state.show_expense_form = True
    
    with col3:
        if st.button("🧾 إضافة إيصال", use_container_width=True):
            st.session_state.show_receipt_form = True
    
    with col4:
        if st.button("💾 نسخة احتياطية", use_container_width=True):
            make_backup()
            st.success("✅ تم إنشاء النسخة الاحتياطية بنجاح!")
    
    # نماذج الإضافة السريعة
    if st.session_state.get('show_expense_form', False):
        with st.expander("💰 إضافة صرفية جديدة", expanded=True):
            with st.form("quick_expense_form"):
                col1, col2 = st.columns(2)
                with col1:
                    expense_amount = st.number_input("المبلغ (د.ع)", min_value=0.0, step=1.0)
                with col2:
                    expense_reason = st.text_input("البيان", placeholder="سبب الصرفية")
                
                if st.form_submit_button("💾 حفظ الصرفية", type="primary"):
                    if expense_amount > 0 and expense_reason.strip():
                        insert_expense(expense_amount, expense_reason.strip())
                        st.success("✅ تم حفظ الصرفية بنجاح!")
                        st.session_state.show_expense_form = False
                        st.rerun()
                    else:
                        st.error("❌ يرجى ملء جميع الحقول")
    
    if st.session_state.get('show_receipt_form', False):
        with st.expander("🧾 إضافة إيصال جديد", expanded=True):
            with st.form("quick_receipt_form"):
                col1, col2 = st.columns(2)
                with col1:
                    receipt_amount = st.number_input("المبلغ (د.ع)", min_value=0.0, step=1.0)
                with col2:
                    receipt_note = st.text_input("البيان", placeholder="تفاصيل الإيصال")
                
                if st.form_submit_button("💾 حفظ الإيصال", type="primary"):
                    if receipt_amount > 0 and receipt_note.strip():
                        insert_receipt(receipt_amount, receipt_note.strip())
                        st.success("✅ تم حفظ الإيصال بنجاح!")
                        st.session_state.show_receipt_form = False
                        st.rerun()
                    else:
                        st.error("❌ يرجى ملء جميع الحقول")
    
    # معاملات اليوم
    st.markdown('<h2 class="section-header">📝 معاملات اليوم</h2>', unsafe_allow_html=True)
    
    today_transactions = get_daily_transactions()
    if today_transactions:
        df = pd.DataFrame(today_transactions, columns=["نوع المعاملة", "البيان", "المبلغ"])
        df["المبلغ"] = df["المبلغ"].apply(lambda x: f"{x:,.0f} د.ع")
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("📋 لا توجد معاملات اليوم")

elif page == "📝 تسجيل طالب جديد":
    show_register_form()

elif page == "👥 إدارة الطلاب":
    st.header("👥 إدارة الطلاب")
    
    # عرض جميع الطلاب
    students = get_all_students()
    
    if students:
        st.subheader(f"📊 إجمالي الطلاب: {len(students)}")
        
        # تحويل البيانات إلى DataFrame
        df_students = pd.DataFrame(students, columns=[
            "الرقم", "اسم الطالب", "تاريخ الميلاد", "الجنس", 
            "العنوان", "رقم الهاتف", "الرسوم", "الرسوم الإضافية", "تاريخ التسجيل"
        ])
        
        # إضافة عمود المجموع
        df_students["إجمالي الرسوم"] = df_students["الرسوم"] + df_students["الرسوم الإضافية"]
        df_students["إجمالي الرسوم"] = df_students["إجمالي الرسوم"].apply(lambda x: f"{x:,.0f} د.ع")
        df_students["الرسوم"] = df_students["الرسوم"].apply(lambda x: f"{x:,.0f} د.ع")
        df_students["الرسوم الإضافية"] = df_students["الرسوم الإضافية"].apply(lambda x: f"{x:,.0f} د.ع")
        
        # البحث والفلترة
        search_term = st.text_input("🔍 البحث عن طالب", placeholder="ادخل اسم الطالب أو رقم الهاتف...")
        
        if search_term:
            # تصفية البيانات حسب البحث
            mask = df_students["اسم الطالب"].str.contains(search_term, case=False, na=False) | \
                   df_students["رقم الهاتف"].str.contains(search_term, case=False, na=False)
            df_filtered = df_students[mask]
        else:
            df_filtered = df_students
        
        # عرض الجدول
        st.dataframe(
            df_filtered.drop(columns=["الرقم"]), 
            use_container_width=True,
            hide_index=True
        )
        
        # تصدير البيانات
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📄 تصدير PDF", type="primary"):
                # تحويل البيانات للتصدير
                students_for_pdf = []
                for student in students:
                    student_dict = {
                        'اسم_الطالب': student[1],
                        'العمر': 2024 - int(student[2][:4]) if student[2] else 0,
                        'الجنس': student[3],
                        'رقم_الهاتف': student[5],
                        'رسوم_التسجيل': student[6],
                        'الرسوم_الشهرية': student[7],
                        'تاريخ_التسجيل': student[8]
                    }
                    students_for_pdf.append(student_dict)
                
                pdf_buffer = create_students_report_pdf(students_for_pdf)
                st.download_button(
                    label="⬇️ تحميل تقرير الطلاب PDF",
                    data=pdf_buffer.getvalue(),
                    file_name=f"students_report_{date.today().strftime('%Y%m%d')}.pdf",
                    mime="application/pdf"
                )
        
        with col2:
            if st.button("📊 تصدير CSV", type="secondary"):
                csv = df_students.to_csv(index=False)
                st.download_button(
                    label="⬇️ تحميل بيانات CSV",
                    data=csv.encode('utf-8-sig'),
                    file_name=f"students_data_{date.today().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
        
        # إحصائيات سريعة
        st.divider()
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_revenue = sum(student[6] + student[7] for student in students)
            st.metric("💰 إجمالي الإيرادات", f"{total_revenue:,.0f} د.ع")
        
        with col2:
            avg_fee = sum(student[6] for student in students) / len(students) if students else 0
            st.metric("📊 متوسط الرسوم", f"{avg_fee:,.0f} د.ع")
        
        with col3:
            males_count = sum(1 for student in students if student[3] == "ذكر")
            st.metric("👦 الذكور", f"{males_count:,}")
        
        with col4:
            females_count = sum(1 for student in students if student[3] == "أنثى")
            st.metric("👧 الإناث", f"{females_count:,}")
    
    else:
        st.info("📋 لا توجد بيانات طلاب")
        if st.button("➕ إضافة أول طالب", type="primary"):
            st.session_state.navigation = "تسجيل طالب جديد"
            st.rerun()

elif page == "💰 الصرفيات والإيصالات":
    st.header("💰 إدارة الصرفيات والإيصالات")
    
    tab1, tab2, tab3 = st.tabs(["💸 الصرفيات", "🧾 الإيصالات", "➕ إضافة جديد"])
    
    with tab1:
        st.subheader("💸 قائمة الصرفيات")
        expenses = get_all_expenses()
        
        if expenses:
            df_expenses = pd.DataFrame(expenses, columns=["الرقم", "المبلغ", "البيان", "التاريخ"])
            df_expenses["المبلغ"] = df_expenses["المبلغ"].apply(lambda x: f"{x:,.0f} د.ع")
            
            # البحث في الصرفيات
            search_expense = st.text_input("🔍 البحث في الصرفيات", key="search_expense")
            if search_expense:
                mask = df_expenses["البيان"].str.contains(search_expense, case=False, na=False)
                df_expenses = df_expenses[mask]
            
            st.dataframe(df_expenses.drop(columns=["الرقم"]), use_container_width=True, hide_index=True)
            
            # إحصائيات الصرفيات
            total_expenses = sum(expense[1] for expense in expenses)
            st.metric("💸 إجمالي الصرفيات", f"{total_expenses:,.0f} د.ع")
        else:
            st.info("📋 لا توجد صرفيات مسجلة")
    
    with tab2:
        st.subheader("🧾 قائمة الإيصالات")
        receipts = get_all_receipts()
        
        if receipts:
            df_receipts = pd.DataFrame(receipts, columns=["الرقم", "المبلغ", "البيان", "التاريخ"])
            df_receipts["المبلغ"] = df_receipts["المبلغ"].apply(lambda x: f"{x:,.0f} د.ع")
            
            # البحث في الإيصالات
            search_receipt = st.text_input("🔍 البحث في الإيصالات", key="search_receipt")
            if search_receipt:
                mask = df_receipts["البيان"].str.contains(search_receipt, case=False, na=False)
                df_receipts = df_receipts[mask]
            
            st.dataframe(df_receipts.drop(columns=["الرقم"]), use_container_width=True, hide_index=True)
            
            # إحصائيات الإيصالات
            total_receipts = sum(receipt[1] for receipt in receipts)
            st.metric("🧾 إجمالي الإيصالات", f"{total_receipts:,.0f} د.ع")
        else:
            st.info("📋 لا توجد إيصالات مسجلة")
    
    with tab3:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("💸 إضافة صرفية جديدة")
            with st.form("expense_form"):
                expense_amount = st.number_input("المبلغ (د.ع)", min_value=0.0, step=1.0, key="exp_amount")
                expense_reason = st.text_input("البيان", placeholder="سبب الصرفية", key="exp_reason")
                
                if st.form_submit_button("💾 حفظ الصرفية", type="primary"):
                    if expense_amount > 0 and expense_reason.strip():
                        insert_expense(expense_amount, expense_reason.strip())
                        st.success("✅ تم حفظ الصرفية بنجاح!")
                        st.rerun()
                    else:
                        st.error("❌ يرجى ملء جميع الحقول")
        
        with col2:
            st.subheader("🧾 إضافة إيصال جديد")
            with st.form("receipt_form"):
                receipt_amount = st.number_input("المبلغ (د.ع)", min_value=0.0, step=1.0, key="rec_amount")
                receipt_note = st.text_input("البيان", placeholder="تفاصيل الإيصال", key="rec_note")
                
                if st.form_submit_button("💾 حفظ الإيصال", type="primary"):
                    if receipt_amount > 0 and receipt_note.strip():
                        insert_receipt(receipt_amount, receipt_note.strip())
                        st.success("✅ تم حفظ الإيصال بنجاح!")
                        st.rerun()
                    else:
                        st.error("❌ يرجى ملء جميع الحقول")

elif page == "🗑️ إدارة الحذف":
    st.header("🗑️ إدارة الحذف الآمن")
    
    # تحذير أمني
    st.markdown("""
    <div class="deletion-warning">
        ⚠️ تحذير: عمليات الحذف نهائية ولا يمكن التراجع عنها<br>
        تأكد من صحة البيانات قبل الحذف
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4 = st.tabs(["👥 حذف الطلاب", "💸 حذف الصرفيات", "🧾 حذف الإيصالات", "📋 سجل الحذف"])
    
    with tab1:
        show_student_deletion_section()
    
    with tab2:
        show_expense_deletion_section()
    
    with tab3:
        show_receipt_deletion_section()
    
    with tab4:
        st.subheader("📋 سجل عمليات الحذف")
        deletion_log = get_deletion_log()
        
        if deletion_log:
            df_deletions = pd.DataFrame(deletion_log, columns=[
                "الرقم", "نوع العملية", "البيان", "البيانات المحذوفة", "تاريخ الحذف"
            ])
            st.dataframe(df_deletions.drop(columns=["الرقم"]), use_container_width=True, hide_index=True)
        else:
            st.info("📋 لا توجد عمليات حذف مسجلة")

elif page == "📊 التقارير المالية":
    st.header("📊 التقارير المالية")
    
    # ملخص مالي شامل
    daily_income, monthly_income, yearly_income = get_income_summary()
    expenses = get_all_expenses()
    receipts = get_all_receipts()
    
    total_expenses = sum(expense[1] for expense in expenses) if expenses else 0
    total_receipts = sum(receipt[1] for receipt in receipts) if receipts else 0
    
    # الملخص العام
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("💰 إيرادات الطلاب", f"{yearly_income:,.0f} د.ع")
    
    with col2:
        st.metric("🧾 إجمالي الإيصالات", f"{total_receipts:,.0f} د.ع")
    
    with col3:
        st.metric("💸 إجمالي الصرفيات", f"{total_expenses:,.0f} د.ع")
    
    with col4:
        net_profit = yearly_income + total_receipts - total_expenses
        st.metric("📈 صافي الربح", f"{net_profit:,.0f} د.ع")
    
    st.divider()
    
    # تقارير PDF محسنة
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📄 تقرير الطلاب PDF", type="primary"):
            students = get_all_students()
            if students:
                # تحويل بيانات الطلاب للتنسيق المطلوب
                students_data = []
                for student in students:
                    student_dict = {
                        'اسم_الطالب': student[1],
                        'العمر': student[2],
                        'الجنس': student[3],
                        'رقم_الهاتف': student[4],
                        'رسوم_التسجيل': student[5],
                        'الرسوم_الشهرية': student[6],
                        'تاريخ_التسجيل': student[7]
                    }
                    students_data.append(student_dict)
                
                pdf_buffer = create_students_report_pdf(students_data, "كشف طلاب الروضة")
                st.download_button(
                    label="⬇️ تحميل كشف الطلاب",
                    data=pdf_buffer.getvalue(),
                    file_name=f"students_report_{datetime.now().strftime('%Y%m%d')}.pdf",
                    mime="application/pdf"
                )
            else:
                st.warning("لا توجد بيانات طلاب لإنشاء التقرير")
    
    with col2:
        if st.button("📊 التقرير المالي PDF", type="primary"):
            # إعداد بيانات الصرفيات
            expenses_data = []
            for expense in expenses:
                expense_dict = {
                    'amount': expense[1],
                    'description': expense[2],
                    'date': expense[3]
                }
                expenses_data.append(expense_dict)
            
            # إعداد بيانات الإيصالات
            receipts_data = []
            for receipt in receipts:
                receipt_dict = {
                    'amount': receipt[1],
                    'description': receipt[2],
                    'date': receipt[3]
                }
                receipts_data.append(receipt_dict)
            
            pdf_buffer = create_financial_report_pdf(expenses_data, receipts_data, "التقرير المالي الشامل")
            st.download_button(
                label="⬇️ تحميل التقرير المالي",
                data=pdf_buffer.getvalue(),
                file_name=f"financial_report_{datetime.now().strftime('%Y%m%d')}.pdf",
                mime="application/pdf"
            )

elif page == "📋 سجل المعاملات":
    st.header("📋 سجل المعاملات")
    
    transactions = get_transaction_log()
    
    if transactions:
        df_transactions = pd.DataFrame(transactions, columns=[
            "التاريخ", "نوع المعاملة", "المبلغ", "البيان"
        ])
        df_transactions["المبلغ"] = df_transactions["المبلغ"].apply(lambda x: f"{x:,.0f} د.ع")
        
        # فلترة حسب نوع المعاملة
        transaction_types = ["جميع المعاملات"] + list(df_transactions["نوع المعاملة"].unique())
        selected_type = st.selectbox("🔍 فلترة حسب نوع المعاملة", transaction_types)
        
        if selected_type != "جميع المعاملات":
            df_transactions = df_transactions[df_transactions["نوع المعاملة"] == selected_type]
        
        st.dataframe(df_transactions, use_container_width=True, hide_index=True)
        
        # إحصائيات المعاملات
        st.subheader("📊 إحصائيات المعاملات")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            registrations = [t for t in transactions if t[1] == "تسجيل طالب"]
            st.metric("👥 تسجيلات الطلاب", len(registrations))
        
        with col2:
            expenses_count = [t for t in transactions if t[1] == "صرفية"]
            st.metric("💸 الصرفيات", len(expenses_count))
        
        with col3:
            receipts_count = [t for t in transactions if t[1] == "إيصال"]
            st.metric("🧾 الإيصالات", len(receipts_count))
    
    else:
        st.info("📋 لا توجد معاملات مسجلة")

elif page == "💾 النسخ الاحتياطية":
    st.header("💾 إدارة النسخ الاحتياطية")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📁 معلومات قاعدة البيانات")
        if os.path.exists(DB_PATH):
            file_size = os.path.getsize(DB_PATH) / 1024  # KB
            st.info(f"📊 حجم قاعدة البيانات: {file_size:.2f} KB")
            st.info(f"📂 مسار الملف: {DB_PATH}")
        
        if st.button("🔄 إنشاء نسخة احتياطية", type="primary", use_container_width=True):
            make_backup()
            st.success("✅ تم إنشاء النسخة الاحتياطية بنجاح!")
    
    with col2:
        st.subheader("📋 النسخ الاحتياطية الموجودة")
        if os.path.exists(BACKUP_DIR):
            backup_files = [f for f in os.listdir(BACKUP_DIR) if f.endswith('.db')]
            
            if backup_files:
                backup_files.sort(reverse=True)  # أحدث أولاً
                
                for backup_file in backup_files[:10]:  # أظهر آخر 10 نسخ
                    backup_path = os.path.join(BACKUP_DIR, backup_file)
                    backup_size = os.path.getsize(backup_path) / 1024
                    
                    st.text(f"📄 {backup_file}")
                    st.caption(f"الحجم: {backup_size:.2f} KB")
            else:
                st.info("📋 لا توجد نسخ احتياطية")
        
        st.info("💡 يتم إنشاء نسخة احتياطية تلقائياً عند كل عملية تعديل")
