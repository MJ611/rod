import streamlit as st
import pandas as pd
import os
from datetime import date
from db import connect_db, get_total_students_count, get_students_count_today, get_income_summary, get_all_students, insert_expense, get_expenses_today, get_all_expenses, get_gender_stats, get_transaction_log, get_daily_transactions, insert_receipt, make_backup, DB_PATH, BACKUP_DIR
from register import show_register_form
from pdf_generator import create_students_report_pdf, create_financial_report_pdf

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
    
    .progress-indicator {
        background: linear-gradient(90deg, #e2e8f0, #1f4e79);
        height: 4px;
        border-radius: 2px;
        margin: 1rem 0;
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
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
    }
    
    .floating-element {
        animation: float 3s ease-in-out infinite;
    }
    
    .gradient-text {
        background: linear-gradient(45deg, #1f4e79, #2d6ba3, #3b82f6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        background-size: 200% 200%;
        animation: gradientShift 4s ease infinite;
    }
    
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    .glass-effect {
        background: rgba(255, 255, 255, 0.25);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 15px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    }
    
    .sparkle {
        position: relative;
        overflow: hidden;
    }
    
    .sparkle::before {
        content: '✨';
        position: absolute;
        top: 10px;
        right: 10px;
        animation: sparkleAnimation 2s linear infinite;
    }
    
    @keyframes sparkleAnimation {
        0%, 100% { opacity: 0.5; transform: scale(0.8); }
        50% { opacity: 1; transform: scale(1.2); }
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
                    help="استخدم: admin"
                )
                
                password = st.text_input(
                    "🔑 كلمة المرور", 
                    type="password", 
                    placeholder="أدخل كلمة المرور",
                    help="استخدم: 1234"
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
                        # time.sleep(1)  # إزالة التأخير لتحسين الأداء
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
                    <strong>المستخدم:</strong> admin | <strong>كلمة المرور:</strong> 1234
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

# العنوان الرئيسي المحسن مع اللوجو
col1, col2, col3 = st.columns([1, 4, 1])

with col2:
    # عرض اللوجو والعنوان في الوسط مع تخطيط جميل
    st.markdown("""
    <div style="text-align: center; padding: 2rem; 
               background: linear-gradient(135deg, #f8fafc, #e2e8f0); 
               border-radius: 20px; margin-bottom: 2rem;
               box-shadow: 0 10px 30px rgba(0,0,0,0.1);
               border: 2px solid #e2e8f0;">
    """, unsafe_allow_html=True)
    
    # اللوجو في الوسط
    logo_center_col1, logo_center_col2, logo_center_col3 = st.columns([1, 1, 1])
    with logo_center_col2:
        try:
            st.image("logo.jpg", width=180)
        except:
            st.markdown("""
            <div style="background: linear-gradient(45deg, #1f4e79, #2d6ba3); 
                       width: 140px; height: 140px; border-radius: 50%; 
                       display: inline-flex; align-items: center; justify-content: center;
                       color: white; font-size: 3.5rem; margin: 0 auto;
                       box-shadow: 0 20px 40px rgba(31, 78, 121, 0.4);
                       border: 8px solid white;">
                🌟
            </div>
            """, unsafe_allow_html=True)
    
    # العنوان تحت اللوجو
    st.markdown("""
    <div class="main-header" style="text-align: center; margin-top: 1.5rem;">
        <h1 style="margin: 0; font-size: 2.8rem; background: linear-gradient(45deg, #1f4e79, #2d6ba3);
                   -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                   background-clip: text; font-weight: bold;">
            روضة قطر الندى الأهلية
        </h1>
        <p style="margin: 1rem 0 0 0; font-size: 1.3rem; color: #64748b;
                  font-weight: 500; letter-spacing: 1px;">
            نظام إدارة متكامل للطلاب والمالية ✨
        </p>
    </div>
    </div>
    """, unsafe_allow_html=True)

# الشريط الجانبي المحسن
with st.sidebar:
    # عرض اللوجو في الشريط الجانبي
    st.markdown('<div class="sidebar-logo">', unsafe_allow_html=True)
    sidebar_logo_col1, sidebar_logo_col2, sidebar_logo_col3 = st.columns([1, 1, 1])
    with sidebar_logo_col2:
        try:
            st.image("logo.jpg", width=100)
        except:
            st.markdown("""
            <div style="background: linear-gradient(45deg, #1f4e79, #2d6ba3); 
                       width: 80px; height: 80px; border-radius: 50%; 
                       display: inline-flex; align-items: center; justify-content: center;
                       color: white; font-size: 2rem; margin: 0 auto;
                       box-shadow: 0 8px 20px rgba(31, 78, 121, 0.4);
                       border: 3px solid white;">
                🌟
            </div>
            """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div style="text-align: center; padding: 1rem; background: linear-gradient(135deg, #f8fafc, #e2e8f0); 
                border-radius: 12px; margin-bottom: 1rem;">
        <h2 style="color: #1f4e79; margin-bottom: 0.5rem;">📋 القائمة الرئيسية</h2>
        <p style="color: #64748b; margin: 0; font-size: 0.9rem;">اختر الصفحة المطلوبة</p>
    </div>
    """, unsafe_allow_html=True)
    
    page = st.radio(
        "اختر الصفحة",
        ["🏠 الصفحة الرئيسية", "📝 تسجيل طالب جديد", "👥 قائمة الطلاب", "💸 الصرفيات", 
         "🧾 الإيصالات", "📋 كشف الحساب", "📈 التقارير", "💾 النسخ الاحتياطي"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    # معلومات المستخدم
    st.markdown("""
    <div class="info-box">
        <p style="margin: 0; text-align: center;">
            <strong>👤 المستخدم:</strong> مدير النظام<br>
            <strong>🕐 الجلسة:</strong> نشطة
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # زر تسجيل الخروج
    if st.button("🚪 تسجيل الخروج", use_container_width=True, type="secondary"):
        st.session_state.logged_in = False
        st.rerun()

if page == "🏠 الصفحة الرئيسية":
    st.markdown('<div class="section-header"><h2>📊 لوحة المعلومات الرئيسية</h2></div>', unsafe_allow_html=True)
    
    # الحصول على البيانات
    total_students = get_total_students_count()
    today_students = get_students_count_today()
    daily_income, monthly_income, yearly_income = get_income_summary()
    daily_income = daily_income or 0
    monthly_income = monthly_income or 0
    yearly_income = yearly_income or 0
    daily_expenses = get_expenses_today()
    net_daily = daily_income - daily_expenses
    
    # بطاقات الإحصائيات المحسنة مع تأثيرات بصرية
    st.markdown('<div class="card-container sparkle">', unsafe_allow_html=True)
    st.markdown('<h3 class="gradient-text">📊 لوحة المؤشرات الرئيسية</h3>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="👥 إجمالي الطلاب",
            value=total_students,
            delta=f"+{today_students} اليوم" if today_students > 0 else None
        )
    
    with col2:
        st.metric(
            label="💰 الإيرادات اليومية",
            value=f"{daily_income:.0f} د.ع",
            delta=f"من {today_students} طلاب" if today_students > 0 else None
        )
    
    with col3:
        st.metric(
            label="💸 الصرفيات اليومية",
            value=f"{daily_expenses:.0f} د.ع"
        )
    
    with col4:
        st.metric(
            label="💵 الصافي اليومي",
            value=f"{net_daily:.0f} د.ع",
            delta="ربح جيد" if net_daily > 0 else "انتباه!" if net_daily < 0 else "متوازن"
        )
    
    # شريط التقدم البصري
    if net_daily > 0:
        progress_color = "#10b981"
        status_text = "الأداء المالي ممتاز ✨"
    elif net_daily < 0:
        progress_color = "#ef4444"
        status_text = "يحتاج مراجعة المصروفات ⚠️"
    else:
        progress_color = "#6b7280"
        status_text = "الأداء متوازن 📊"
    
    st.markdown(f"""
    <div style="background: {progress_color}; height: 6px; border-radius: 3px; margin: 1rem 0;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);"></div>
    <p style="text-align: center; color: {progress_color}; font-weight: bold; margin: 0;">{status_text}</p>
    """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # بطاقات الإجراءات السريعة المحسنة مع تأثيرات جمالية
    st.markdown('<div class="card-container glass-effect">', unsafe_allow_html=True)
    st.markdown('<h3 class="gradient-text floating-element">⚡ الإجراءات السريعة</h3>', unsafe_allow_html=True)
    
    action_col1, action_col2, action_col3 = st.columns(3)
    
    with action_col1:
        st.markdown("""
        <div class="quick-action-card">
            <span class="action-icon">📝</span>
            <h4 style="color: #1f4e79; margin: 0 0 0.5rem 0;">تسجيل طالب جديد</h4>
            <p style="color: #64748b; margin: 0; font-size: 0.9rem;">إضافة طالب جديد للنظام</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🆕 تسجيل الآن", use_container_width=True, type="primary", key="register"):
            st.rerun()
    
    with action_col2:
        st.markdown("""
        <div class="quick-action-card">
            <span class="action-icon">💸</span>
            <h4 style="color: #1f4e79; margin: 0 0 0.5rem 0;">إضافة صرفية</h4>
            <p style="color: #64748b; margin: 0; font-size: 0.9rem;">تسجيل المصروفات اليومية</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("💳 إضافة صرفية", use_container_width=True, key="expense"):
            st.rerun()
    
    with action_col3:
        st.markdown("""
        <div class="quick-action-card">
            <span class="action-icon">📈</span>
            <h4 style="color: #1f4e79; margin: 0 0 0.5rem 0;">عرض التقارير</h4>
            <p style="color: #64748b; margin: 0; font-size: 0.9rem;">تحليل الأداء المالي</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("📊 عرض التقارير", use_container_width=True, key="reports"):
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # بطاقة دليل الاستخدام المحسنة
    st.markdown('<div class="card-container">', unsafe_allow_html=True)
    
    with st.expander("📋 دليل الاستخدام السريع", expanded=False):
        guide_col1, guide_col2 = st.columns(2)
        
        with guide_col1:
            st.markdown("""
            **🚀 البدء السريع:**
            - 📝 تسجيل طالب جديد من القائمة الجانبية
            - 👥 عرض قائمة الطلاب والبحث فيها
            - 💸 تسجيل المصروفات اليومية
            - 🧾 إضافة إيصالات الدفع
            """)
        
        with guide_col2:
            st.markdown("""
            **📊 التقارير والإدارة:**
            - 📈 عرض التقارير المالية التفصيلية
            - 📋 مراجعة كشف الحساب الشامل
            - 💾 إدارة النسخ الاحتياطية
            - ⚙️ مراقبة الأداء العام
            """)
    
    # إحصائيات سريعة إضافية
    if total_students > 0:
        st.markdown("### 📈 نظرة سريعة")
        
        quick_col1, quick_col2, quick_col3 = st.columns(3)
        
        with quick_col1:
            avg_daily = monthly_income / 30 if monthly_income > 0 else 0
            st.info(f"**متوسط الإيرادات اليومية:** {avg_daily:.0f} د.ع")
        
        with quick_col2:
            efficiency = (net_daily / daily_income * 100) if daily_income > 0 else 0
            st.success(f"**كفاءة الأداء اليوم:** {efficiency:.1f}%")
        
        with quick_col3:
            monthly_target = total_students * 50  # هدف افتراضي
            progress_percentage = (monthly_income / monthly_target * 100) if monthly_target > 0 else 0
            st.warning(f"**تحقيق الهدف الشهري:** {min(progress_percentage, 100):.1f}%")
    
    st.markdown('</div>', unsafe_allow_html=True)

elif page == "📝 تسجيل طالب جديد":
    st.markdown('<div class="section-header"><h2>📝 تسجيل طالب جديد</h2></div>', unsafe_allow_html=True)
    st.markdown('<div class="feature-box">', unsafe_allow_html=True)
    show_register_form()
    st.markdown('</div>', unsafe_allow_html=True)

elif page == "👥 قائمة الطلاب":
    st.markdown('<div class="section-header"><h2>👥 قائمة الطلاب المسجلين</h2></div>', unsafe_allow_html=True)
    
    students = get_all_students()
    
    if not students:
        st.info("📝 لا توجد بيانات طلاب مسجلة حالياً")
        st.markdown("### يمكنك البدء بتسجيل طلاب جدد من صفحة التسجيل")
    else:
        # إحصائيات سريعة في الأعلى
        st.markdown('<div class="stats-container">', unsafe_allow_html=True)
        st.markdown("### 📊 إحصائيات عامة")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_count = len(students)
            st.metric("إجمالي الطلاب", total_count)
        
        with col2:
            male_count = len([s for s in students if s[3] == "ذكر"])
            female_count = len([s for s in students if s[3] == "أنثى"])
            st.metric("الذكور", male_count)
            st.metric("الإناث", female_count)
        
        with col3:
            total_fees = sum([s[6] + s[7] for s in students])  # الرسوم الأساسية + الإضافية
            st.metric("إجمالي الرسوم", f"{total_fees:.0f} د.ع")
        
        with col4:
            avg_fee = total_fees / total_count if total_count > 0 else 0
            st.metric("متوسط الرسوم", f"{avg_fee:.0f} د.ع")
        
        st.markdown('</div>', unsafe_allow_html=True)
        st.divider()
        
        # فلتر وبحث
        st.markdown('<div class="feature-box">', unsafe_allow_html=True)
        st.markdown("### 🔍 البحث والتصفية")
        
        search_col1, search_col2 = st.columns(2)
        
        with search_col1:
            search_name = st.text_input("البحث بالاسم", placeholder="أدخل اسم الطالب...")
        
        with search_col2:
            gender_filter = st.selectbox("تصفية حسب الجنس", ["الكل", "ذكر", "أنثى"])
        
        # تطبيق الفلاتر
        filtered_students = students
        
        if search_name:
            filtered_students = [s for s in filtered_students if search_name.lower() in s[1].lower()]
        
        if gender_filter != "الكل":
            filtered_students = [s for s in filtered_students if s[3] == gender_filter]
        
        st.write(f"عدد النتائج: {len(filtered_students)} من {total_count}")
        
        # تحويل البيانات إلى DataFrame
        if filtered_students:
            df = pd.DataFrame(filtered_students)
            df.columns = [
                "الرقم", "الاسم", "تاريخ الميلاد", "الجنس", "السكن", 
                "الهاتف", "القسط", "الأجور الإضافية", "تاريخ التسجيل"
            ]
            
            # خيارات العرض
            show_columns = st.multiselect(
                "اختر الأعمدة المراد عرضها:",
                list(df.columns),
                default=["الاسم", "الجنس", "الهاتف", "القسط", "تاريخ التسجيل"]
            )
            
            if show_columns:
                # عرض الجدول مع الأعمدة المحددة
                st.dataframe(df[show_columns], use_container_width=True, height=400)
                
                # أزرار التصدير
                st.subheader("📥 تصدير البيانات")
                
                export_col1, export_col2 = st.columns(2)
                
                with export_col1:
                    csv = df[show_columns].to_csv(index=False).encode('utf-8-sig')
                    st.download_button(
                        label="📄 تحميل كملف CSV",
                        data=csv,
                        file_name=f"students_list_{pd.Timestamp.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )
                
                with export_col2:
                    # إنشاء كشف PDF للطلاب
                    if st.button("🖨️ طباعة كشف PDF", use_container_width=True, type="secondary"):
                        try:
                            # تحضير البيانات للـ PDF
                            pdf_data = []
                            for student in filtered_students:
                                student_dict = {
                                    'اسم_الطالب': student[1],
                                    'العمر': student[2] if len(str(student[2])) < 10 else 'غير محدد',
                                    'الجنس': student[3],
                                    'رقم_الهاتف': student[5],
                                    'رسوم_التسجيل': float(student[6]) if student[6] else 0,
                                    'الرسوم_الشهرية': float(student[7]) if student[7] else 0,
                                    'تاريخ_التسجيل': student[8]
                                }
                                pdf_data.append(student_dict)
                            
                            pdf_buffer = create_students_report_pdf(pdf_data, "كشف طلاب الروضة")
                            
                            st.download_button(
                                label="📄 تحميل كشف الطلاب (PDF)",
                                data=pdf_buffer.getvalue(),
                                file_name=f"students_report_{pd.Timestamp.now().strftime('%Y%m%d_%H%M')}.pdf",
                                mime="application/pdf",
                                use_container_width=True
                            )
                            st.success("✅ تم إنشاء كشف PDF بنجاح!")
                        except Exception as e:
                            st.error(f"❌ خطأ في إنشاء PDF: {str(e)}")
                
                # عرض إحصائيات الطلاب المفلترين
                if len(filtered_students) != total_count:
                    st.divider()
                    st.markdown("### 📊 إحصائيات النتائج المفلترة")
                    
                    stats_col1, stats_col2, stats_col3 = st.columns(3)
                    
                    with stats_col1:
                        filtered_male = len([s for s in filtered_students if s[3] == "ذكر"])
                        st.metric("👨 الذكور", filtered_male)
                    
                    with stats_col2:
                        filtered_female = len([s for s in filtered_students if s[3] == "أنثى"])
                        st.metric("👩 الإناث", filtered_female)
                    
                    with stats_col3:
                        filtered_total_fees = sum([s[6] + s[7] for s in filtered_students])
                        st.metric("💰 إجمالي الرسوم", f"{filtered_total_fees:.0f} د.ع")
            else:
                st.warning("يرجى اختيار عمود واحد على الأقل للعرض")
        else:
            st.info("لا توجد نتائج تطابق معايير البحث")

elif page == "💸 الصرفيات":
    st.markdown('<div class="section-header"><h2>💸 إدارة الصرفيات</h2></div>', unsafe_allow_html=True)
    
    # إضافة صرفية جديدة
    st.markdown('<div class="feature-box">', unsafe_allow_html=True)
    st.markdown("### ➕ إضافة صرفية جديدة")
    
    with st.form("expense_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            amount = st.number_input("مبلغ الصرفية (د.ع) *", min_value=0.0, value=0.0, step=1.0, format="%.2f")
        
        with col2:
            expense_category = st.selectbox("فئة الصرفية", [
                "مرافق عامة", "رواتب", "صيانة", "مستلزمات", "أخرى"
            ])
        
        reason = st.text_area("سبب الصرفية *", placeholder="أدخل سبب أو وصف الصرفية...", height=100)
        
        submitted = st.form_submit_button("💾 إضافة الصرفية", use_container_width=True, type="primary")
        
        if submitted:
            if amount <= 0:
                st.error("❌ يرجى إدخال مبلغ صحيح")
            elif not reason.strip():
                st.error("❌ يرجى إدخال سبب الصرفية")
            else:
                try:
                    insert_expense(amount, f"{reason.strip()} - الفئة: {expense_category}")
                    st.success(f"✅ تم إضافة صرفية بمبلغ {amount:.2f} د.ع - فئة: {expense_category}")
                    st.balloons()
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ حدث خطأ أثناء إضافة الصرفية: {str(e)}")
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.divider()
    
    # عرض الصرفيات
    st.markdown('<div class="stats-container">', unsafe_allow_html=True)
    st.markdown("### 📋 قائمة الصرفيات")
    
    expenses = get_all_expenses()
    
    if not expenses:
        st.info("📝 لا توجد صرفيات مسجلة حالياً")
    else:
        # تحويل البيانات إلى DataFrame
        df = pd.DataFrame(expenses)
        df.columns = ["الرقم", "المبلغ", "السبب", "التاريخ"]
        
        # عرض الجدول المحسن
        st.markdown('<div class="data-table">', unsafe_allow_html=True)
        st.dataframe(df, use_container_width=True, height=300)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # إحصائيات سريعة
        st.subheader("📊 إحصائيات الصرفيات")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            today_expenses = get_expenses_today()
            st.metric("💸 صرفيات اليوم", f"{today_expenses:.0f} د.ع")
        
        with col2:
            total_expenses = sum([e[1] for e in expenses])
            st.metric("💰 إجمالي الصرفيات", f"{total_expenses:.0f} د.ع")
        
        with col3:
            avg_expense = total_expenses / len(expenses) if expenses else 0
            st.metric("📈 متوسط الصرفية", f"{avg_expense:.0f} د.ع")
        
        st.markdown('</div>', unsafe_allow_html=True)

elif page == "🧾 الإيصالات":
    st.markdown('<div class="section-header"><h2>🧾 إدارة الإيصالات</h2></div>', unsafe_allow_html=True)
    
    # إضافة إيصال جديد
    st.markdown('<div class="feature-box">', unsafe_allow_html=True)
    st.markdown("### ➕ إضافة إيصال جديد")
    
    with st.form("receipt_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            amount = st.number_input("مبلغ الإيصال (د.ع) *", min_value=0.0, value=0.0, step=1.0, format="%.2f")
        
        with col2:
            payment_method = st.selectbox("طريقة الدفع", [
                "نقد", "تحويل بنكي", "شيك", "بطاقة"
            ])
        
        note = st.text_area("ملاحظات الإيصال *", placeholder="أدخل ملاحظة أو وصف الإيصال...", height=100)
        
        submitted = st.form_submit_button("💾 إضافة الإيصال", use_container_width=True, type="primary")
        
        if submitted:
            if amount <= 0:
                st.error("❌ يرجى إدخال مبلغ صحيح")
            elif not note.strip():
                st.error("❌ يرجى إدخال ملاحظة الإيصال")
            else:
                try:
                    insert_receipt(amount, f"{note.strip()} - طريقة الدفع: {payment_method}")
                    st.success(f"✅ تم إضافة إيصال بمبلغ {amount:.2f} د.ع - طريقة الدفع: {payment_method}")
                    st.balloons()
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ حدث خطأ أثناء إضافة الإيصال: {str(e)}")
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.divider()
    
    # عرض الإيصالات
    st.markdown('<div class="stats-container">', unsafe_allow_html=True)
    st.markdown("### 📋 قائمة الإيصالات")
    
    # استعلام قاعدة البيانات للحصول على الإيصالات
    try:
        import sqlite3
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT id, amount, note, date FROM receipts ORDER BY date DESC")
        receipts_data = cur.fetchall()
        conn.close()
        
        if not receipts_data:
            st.info("📝 لا توجد إيصالات مسجلة حالياً")
        else:
            # تحويل البيانات إلى DataFrame
            receipts = pd.DataFrame(receipts_data)
            receipts.columns = ["الرقم", "المبلغ", "الملاحظة", "التاريخ"]
            
            # عرض الجدول المحسن
            st.markdown('<div class="data-table">', unsafe_allow_html=True)
            st.dataframe(receipts, use_container_width=True, height=300)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # إحصائيات سريعة
            st.markdown("### 📊 إحصائيات الإيصالات")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                total_receipts_count = len(receipts)
                st.metric("📄 عدد الإيصالات", total_receipts_count)
            
            with col2:
                total_receipts_amount = receipts["المبلغ"].sum()
                st.metric("💰 إجمالي مبلغ الإيصالات", f"{total_receipts_amount:.0f} د.ع")
            
            with col3:
                avg_receipt = total_receipts_amount / len(receipts) if len(receipts) > 0 else 0
                st.metric("📈 متوسط الإيصال", f"{avg_receipt:.0f} د.ع")
        
        st.markdown('</div>', unsafe_allow_html=True)
                
    except Exception as e:
        st.markdown('<div class="warning-box">', unsafe_allow_html=True)
        st.error(f"❌ حدث خطأ في تحميل البيانات: {str(e)}")
        st.markdown('</div>', unsafe_allow_html=True)

elif page == "📋 كشف الحساب":
    st.markdown('<div class="section-header"><h2>📋 كشف الحساب (سجل المعاملات)</h2></div>', unsafe_allow_html=True)
    
    # الحصول على سجل المعاملات
    transactions = get_transaction_log()
    
    if not transactions:
        st.info("📝 لا توجد معاملات مسجلة في النظام")
        st.markdown("### سيتم تسجيل المعاملات تلقائياً عند:")
        st.write("• تسجيل طلاب جدد (إيرادات)")
        st.write("• إضافة صرفيات (مصروفات)")
    else:
        # إحصائيات سريعة
        st.markdown('<div class="stats-container">', unsafe_allow_html=True)
        st.markdown("### 📊 ملخص المعاملات")
        
        col1, col2, col3, col4 = st.columns(4)
        
        total_transactions = len(transactions)
        income_transactions = [t for t in transactions if t[1] == "إيراد"]
        expense_transactions = [t for t in transactions if t[1] == "صرف"]
        
        with col1:
            st.metric("📋 إجمالي المعاملات", total_transactions)
        
        with col2:
            st.metric("📈 معاملات الإيرادات", len(income_transactions))
        
        with col3:
            st.metric("💸 معاملات الصرفيات", len(expense_transactions))
        
        with col4:
            total_amount = sum([float(t[2]) for t in transactions if t[1] == "إيراد"]) - sum([float(t[2]) for t in transactions if t[1] == "صرف"])
            st.metric("💰 صافي المعاملات", f"{total_amount:.0f} د.ع")
        
        st.markdown('</div>', unsafe_allow_html=True)
        st.divider()
        
        # فلترة المعاملات
        st.subheader("🔍 تصفية المعاملات")
        
        filter_col1, filter_col2 = st.columns(2)
        
        with filter_col1:
            transaction_type_filter = st.selectbox("نوع المعاملة", ["الكل", "إيراد", "صرف"])
        
        with filter_col2:
            search_description = st.text_input("البحث في الوصف", placeholder="ابحث في وصف المعاملة...")
        
        # تطبيق الفلاتر
        filtered_transactions = transactions
        
        if transaction_type_filter != "الكل":
            filtered_transactions = [t for t in filtered_transactions if t[1] == transaction_type_filter]
        
        if search_description:
            filtered_transactions = [t for t in filtered_transactions if search_description.lower() in t[3].lower()]
        
        st.write(f"عدد النتائج: {len(filtered_transactions)} من {total_transactions}")
        
        # عرض الجدول
        if filtered_transactions:
            df = pd.DataFrame(filtered_transactions)
            df.columns = ["التاريخ", "نوع المعاملة", "المبلغ (د.ع)", "الوصف"]
            
            # تلوين الصفوف حسب نوع المعاملة
            def highlight_transactions(row):
                if row['نوع المعاملة'] == 'إيراد':
                    return ['background-color: #e8f5e8'] * len(row)
                elif row['نوع المعاملة'] == 'صرف':
                    return ['background-color: #ffeaea'] * len(row)
                else:
                    return [''] * len(row)
            
            # عرض الجدول المحسن مع التنسيق
            st.markdown('<div class="data-table">', unsafe_allow_html=True)
            styled_df = df.style.apply(highlight_transactions, axis=1)
            st.dataframe(styled_df, use_container_width=True, height=400)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # زر التصدير
            st.subheader("📥 تصدير البيانات")
            csv = df.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="📄 تحميل كشف الحساب كملف CSV",
                data=csv,
                file_name=f"transaction_log_{pd.Timestamp.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
            
        else:
            st.info("لا توجد معاملات تطابق معايير البحث")

elif page == "💾 النسخ الاحتياطي":
    st.markdown('<div class="section-header"><h2>💾 النسخ الاحتياطي للنظام</h2></div>', unsafe_allow_html=True)
    
    st.markdown('<div class="info-box">', unsafe_allow_html=True)
    st.markdown("### 📋 معلومات النسخ الاحتياطي")
    st.info("يتم إنشاء نسخة احتياطية تلقائياً عند كل عملية تسجيل طالب أو إضافة صرفية أو إيصال")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### ℹ️ تشمل النسخة الاحتياطية:")
        st.write("• بيانات جميع الطلاب المسجلين")
        st.write("• سجل جميع الصرفيات")
        st.write("• سجل جميع الإيصالات")
        st.write("• سجل جميع المعاملات")
    
    with col2:
        st.markdown("### 📁 موقع النسخ الاحتياطية:")
        st.write("📂 مجلد `backup/`")
        st.write("🕐 يتم حفظها بالتاريخ والوقت")
        st.write("📝 تنسيق الملف: `backup_YYYY-MM-DD_HH-MM-SS.db`")
    
    st.divider()
    
    # إنشاء نسخة احتياطية يدوية
    st.subheader("🆘 إنشاء نسخة احتياطية يدوياً")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if st.button("📥 إنشاء نسخة احتياطية الآن", use_container_width=True, type="primary"):
            try:
                make_backup()
                st.success("✅ تم إنشاء النسخة الاحتياطية بنجاح!")
                st.balloons()
            except Exception as e:
                st.error(f"❌ حدث خطأ أثناء إنشاء النسخة الاحتياطية: {str(e)}")
    
    st.divider()
    
    # عرض النسخ الاحتياطية المتوفرة
    st.subheader("📋 النسخ الاحتياطية المتوفرة")
    
    if os.path.exists(BACKUP_DIR):
        backup_files = [f for f in os.listdir(BACKUP_DIR) if f.endswith('.db')]
        
        if backup_files:
            backup_files.sort(reverse=True)  # ترتيب من الأحدث إلى الأقدم
            
            st.write(f"عدد النسخ الاحتياطية المتوفرة: **{len(backup_files)}**")
            
            # عرض النسخ في جدول
            backup_data = []
            for backup_file in backup_files:
                file_path = os.path.join(BACKUP_DIR, backup_file)
                file_size = os.path.getsize(file_path) / 1024  # بالكيلوبايت
                modification_time = os.path.getmtime(file_path)
                formatted_time = pd.to_datetime(modification_time, unit='s').strftime('%Y-%m-%d %H:%M:%S')
                
                backup_data.append({
                    "اسم الملف": backup_file,
                    "تاريخ الإنشاء": formatted_time,
                    "حجم الملف (KB)": f"{file_size:.1f}"
                })
            
            backup_df = pd.DataFrame(backup_data)
            st.dataframe(backup_df, use_container_width=True)
            
        else:
            st.info("📝 لا توجد نسخ احتياطية متوفرة حالياً")
    else:
        st.info("📂 مجلد النسخ الاحتياطية غير موجود")

elif page == "📈 التقارير":
    st.markdown('<div class="section-header"><h2>📈 التقارير والإحصائيات</h2></div>', unsafe_allow_html=True)
    
    # إحصائيات الجنس
    st.markdown('<div class="stats-container">', unsafe_allow_html=True)
    st.markdown("### 👶 إحصائيات الجنس")
    
    males, females = get_gender_stats()
    total_students = get_total_students_count()
    
    if total_students > 0:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("👦 الذكور", males)
        
        with col2:
            st.metric("👧 الإناث", females)
        
        with col3:
            male_percentage = (males/total_students)*100
            st.metric("نسبة الذكور", f"{male_percentage:.1f}%")
        
        with col4:
            female_percentage = (females/total_students)*100
            st.metric("نسبة الإناث", f"{female_percentage:.1f}%")
            
    else:
        st.info("لا توجد بيانات طلاب لعرض إحصائيات الجنس")
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.divider()
    
    st.markdown('<div class="feature-box">', unsafe_allow_html=True)
    st.markdown("### 📈 التقارير المالية")
    
    # الحصول على بيانات الإيرادات والصرفيات
    daily_income, monthly_income, yearly_income = get_income_summary()
    daily_income = daily_income or 0
    monthly_income = monthly_income or 0
    yearly_income = yearly_income or 0
    
    daily_expenses = get_expenses_today()
    net_daily = daily_income - daily_expenses
    
    # عرض التقارير في أعمدة
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.subheader("💰 الإيرادات اليومية")
        st.metric("المبلغ المحصل اليوم", f"{daily_income:.0f} د.ع")
        
        today_count = get_students_count_today()
        if today_count > 0:
            avg_per_student = daily_income / today_count
            st.write(f"متوسط الرسوم لكل طالب: {avg_per_student:.0f} د.ع")
    
    with col2:
        st.subheader("💸 الصرفيات اليومية")
        st.metric("الصرفيات اليوم", f"{daily_expenses:.0f} د.ع")
    
    with col3:
        st.subheader("💵 الصافي اليومي")
        color = "normal" if net_daily >= 0 else "inverse"
        st.metric("الصافي اليوم", f"{net_daily:.0f} د.ع", delta=None)
        if net_daily < 0:
            st.error("⚠️ الصرفيات أكبر من الإيرادات")
        elif net_daily > 0:
            st.success("✅ ربح جيد اليوم")
    
    with col4:
        st.subheader("📊 الإيرادات الشهرية")
        st.metric("المبلغ الشهري", f"{monthly_income:.0f} د.ع")
        
        # نسبة الإيرادات اليومية من الشهرية
        if monthly_income > 0:
            daily_percentage = (daily_income / monthly_income) * 100
            st.write(f"نسبة إيرادات اليوم: {daily_percentage:.1f}%")
    
    st.divider()
    
    # تقرير تفصيلي إضافي
    st.subheader("📈 تقرير مالي تفصيلي")
    
    col5, col6 = st.columns(2)
    
    with col5:
        st.write("**الإيرادات السنوية**")
        st.metric("المبلغ السنوي", f"{yearly_income:.0f} د.ع")
        
        # نسبة الإيرادات الشهرية من السنوية
        if yearly_income > 0:
            monthly_percentage = (monthly_income / yearly_income) * 100
            st.write(f"نسبة إيرادات الشهر: {monthly_percentage:.1f}%")
    
    with col6:
        st.write("**تحليل الأداء**")
        if daily_income > 0:
            expense_ratio = (daily_expenses / daily_income) * 100
            st.write(f"نسبة الصرفيات من الإيرادات: {expense_ratio:.1f}%")
            
            if expense_ratio < 30:
                st.success("🎯 نسبة صرفيات ممتازة")
            elif expense_ratio < 50:
                st.warning("⚡ نسبة صرفيات معقولة")
            else:
                st.error("🚨 نسبة صرفيات عالية")
    
    st.markdown("---")
    
    # ملخص إضافي
    st.subheader("📋 ملخص شامل")
    total_students = get_total_students_count()
    
    summary_data = {
        "المؤشر": [
            "إجمالي عدد الطلاب",
            "الطلاب المسجلين اليوم",
            "متوسط الرسوم السنوية لكل طالب",
            "إجمالي الإيرادات المتوقعة"
        ],
        "القيمة": [
            f"{total_students} طالب",
            f"{get_students_count_today()} طالب",
            f"{yearly_income/total_students:.0f} د.ع" if total_students > 0 else "0 د.ع",
            f"{yearly_income:.0f} د.ع"
        ]
    }
    
    summary_df = pd.DataFrame(summary_data)
    st.table(summary_df)
    
    # إضافة زر طباعة التقرير المالي
    st.divider()
    st.subheader("🖨️ طباعة التقارير")
    
    report_col1, report_col2 = st.columns(2)
    
    with report_col1:
        if st.button("📊 طباعة التقرير المالي PDF", use_container_width=True, type="primary"):
            try:
                # تحضير بيانات الإيرادات
                income_data = get_income_summary()
                
                # تحضير بيانات المصروفات
                expenses = get_all_expenses()
                expenses_data = []
                if expenses:
                    for expense in expenses:
                        expenses_data.append({
                            'التاريخ': expense[3],
                            'البيان': expense[2],
                            'المبلغ': expense[1],
                            'الفئة': 'غير محدد'
                        })
                
                # إنشاء PDF للتقرير المالي
                pdf_buffer = create_financial_report_pdf(income_data, expenses_data, "التقرير المالي الشامل")
                
                st.download_button(
                    label="📄 تحميل التقرير المالي (PDF)",
                    data=pdf_buffer.getvalue(),
                    file_name=f"financial_report_{pd.Timestamp.now().strftime('%Y%m%d_%H%M')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
                st.success("✅ تم إنشاء التقرير المالي PDF بنجاح!")
            except Exception as e:
                st.error(f"❌ خطأ في إنشاء التقرير المالي: {str(e)}")
    
    with report_col2:
        st.info("📋 التقرير المالي يحتوي على:\n- ملخص الإيرادات والمصروفات\n- تفاصيل جميع العمليات المالية\n- تحليل الأداء المالي")
    
    st.markdown('</div>', unsafe_allow_html=True)

# تذييل الصفحة الجميل مع اللوجو والإحصائيات
st.markdown("---")

footer_col1, footer_col2, footer_col3 = st.columns([1, 2, 1])

with footer_col2:
    # معلومات النظام
    system_info_col1, system_info_col2 = st.columns(2)
    
    with system_info_col1:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #f0f9ff, #e0f2fe); 
                   padding: 1rem; border-radius: 12px; text-align: center;
                   border: 1px solid #0ea5e9; margin-bottom: 1rem;">
            <h4 style="color: #0369a1; margin: 0 0 0.5rem 0;">📊 إحصائيات النظام</h4>
            <p style="margin: 0; color: #0284c7; font-size: 0.9rem;">
                النظام يعمل بكفاءة عالية
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with system_info_col2:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #f0fdf4, #dcfce7); 
                   padding: 1rem; border-radius: 12px; text-align: center;
                   border: 1px solid #22c55e; margin-bottom: 1rem;">
            <h4 style="color: #15803d; margin: 0 0 0.5rem 0;">🔒 الأمان</h4>
            <p style="margin: 0; color: #16a34a; font-size: 0.9rem;">
                البيانات محمية ومشفرة
            </p>
        </div>
        """, unsafe_allow_html=True)

    
    # تذييل الصفحة الرئيسي
    st.markdown("""
    <div style="padding: 2rem; 
               background: linear-gradient(135deg, #1f4e79, #2d6ba3); 
               border-radius: 15px; 
               color: white; 
               text-align: center;
               box-shadow: 0 4px 15px rgba(31, 78, 121, 0.3);">
        <h3 style="margin: 0 0 1rem 0; font-size: 1.5rem;">🌟 روضة قطر الندى الأهلية</h3>
        <p style="margin: 0; opacity: 0.9; font-size: 1rem;">
            نظام إدارة متكامل وحديث | تم التطوير بعناية ❤️
        </p>
        <hr style="border: none; height: 1px; background: rgba(255,255,255,0.3); margin: 1rem 0;">
        <p style="margin: 0; font-size: 0.9rem; opacity: 0.8;">
            © 2025 جميع الحقوق محفوظة | النسخة 2.1 المحسنة
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # اللوجو في التذييل
    footer_logo_col1, footer_logo_col2, footer_logo_col3 = st.columns([1, 1, 1])
    with footer_logo_col2:
        try:
            st.image("logo.jpg", width=80)
        except:
            st.markdown("""
            <div style="background: linear-gradient(45deg, #1f4e79, #2d6ba3); 
                       width: 60px; height: 60px; border-radius: 50%; 
                       display: inline-flex; align-items: center; justify-content: center;
                       color: white; font-size: 1.5rem; margin: 0 auto;
                       box-shadow: 0 5px 15px rgba(31, 78, 121, 0.3);
                       border: 2px solid white;">
                🌟
            </div>
            """, unsafe_allow_html=True)
