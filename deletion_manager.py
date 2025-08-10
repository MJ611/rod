import streamlit as st
import pandas as pd
from db import (get_all_students, get_all_expenses, get_all_receipts, 
                delete_student, delete_expense, delete_receipt)

def show_deletion_confirmation(item_type, item_data, delete_function, item_id):
    """عرض نافذة تأكيد الحذف الآمن"""
    
    # عرض تحذير قوي ومميز
    st.markdown("""
    <div style="background: linear-gradient(135deg, #fef2f2, #fee2e2); 
               border: 3px solid #dc2626; border-radius: 15px; 
               padding: 2rem; margin: 1rem 0; text-align: center;
               box-shadow: 0 8px 25px rgba(220, 38, 38, 0.3);">
        <h2 style="color: #dc2626; margin: 0; font-size: 1.8rem;">
            ⚠️ تأكيد الحذف النهائي
        </h2>
        <p style="color: #7f1d1d; font-weight: bold; margin: 1rem 0; font-size: 1.1rem;">
            هذه العملية نهائية ولا يمكن التراجع عنها!<br>
            سيتم حذف البيانات نهائياً من النظام
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # عرض تفاصيل العنصر
    if item_type == "طالب":
        st.info(f"""
        **تفاصيل الطالب المراد حذفه:**
        - **الاسم**: {item_data[1]}
        - **الجنس**: {item_data[3]}
        - **الهاتف**: {item_data[5]}
        - **الرسوم**: {item_data[6]:.0f} د.ع
        - **الرسوم الإضافية**: {item_data[7]:.0f} د.ع
        - **تاريخ التسجيل**: {item_data[8]}
        """)
    
    elif item_type == "صرفية":
        st.info(f"""
        **تفاصيل الصرفية المراد حذفها:**
        - **البيان**: {item_data[2]}
        - **المبلغ**: {item_data[1]:.0f} د.ع
        - **التاريخ**: {item_data[3]}
        """)
    
    elif item_type == "إيصال":
        st.info(f"""
        **تفاصيل الإيصال المراد حذفه:**
        - **البيان**: {item_data[2]}
        - **المبلغ**: {item_data[1]:.0f} د.ع
        - **التاريخ**: {item_data[3]}
        """)
    
    # أزرار التأكيد
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("❌ إلغاء", use_container_width=True):
            st.session_state.confirm_deletion = None
            st.rerun()
    
    with col3:
        if st.button("🗑️ تأكيد الحذف", use_container_width=True, type="primary"):
            try:
                # تنفيذ عملية الحذف
                success = delete_function(item_id)
                
                if success:
                    st.markdown("""
                    <div class="deletion-success">
                        ✅ تم حذف البيانات بنجاح!<br>
                        تم إنشاء نسخة احتياطية تلقائياً
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.session_state.confirm_deletion = None
                    st.balloons()
                    
                    # تأخير قصير ثم إعادة تحميل
                    import time
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("❌ فشل في حذف البيانات!")
                    
            except Exception as e:
                st.error(f"❌ حدث خطأ أثناء الحذف: {str(e)}")

def show_student_deletion_section():
    """عرض قسم حذف الطلاب"""
    st.subheader("👥 حذف بيانات الطلاب")
    
    students = get_all_students()
    
    if not students:
        st.info("📋 لا توجد بيانات طلاب للحذف")
        return
    
    # التحقق من وجود تأكيد حذف في الجلسة
    confirm_deletion = st.session_state.get('confirm_deletion')
    if confirm_deletion and confirm_deletion.get('type') == 'student':
        item_data = st.session_state.confirm_deletion['data']
        item_id = st.session_state.confirm_deletion['id']
        show_deletion_confirmation("طالب", item_data, delete_student, item_id)
        return
    
    # عرض قائمة الطلاب
    df_students = pd.DataFrame(students, columns=[
        "الرقم", "اسم الطالب", "تاريخ الميلاد", "الجنس", 
        "العنوان", "رقم الهاتف", "الرسوم", "الرسوم الإضافية", "تاريخ التسجيل"
    ])
    
    # البحث في الطلاب
    search_student = st.text_input("🔍 البحث عن طالب للحذف", placeholder="ادخل اسم الطالب أو رقم الهاتف...")
    
    if search_student:
        mask = df_students["اسم الطالب"].str.contains(search_student, case=False, na=False) | \
               df_students["رقم الهاتف"].str.contains(search_student, case=False, na=False)
        filtered_students = [students[i] for i in df_students[mask].index]
    else:
        filtered_students = students
    
    if filtered_students:
        st.write(f"📊 عدد الطلاب: {len(filtered_students)}")
        
        # عرض الطلاب مع أزرار الحذف
        for student in filtered_students:
            with st.container():
                # مربع معلومات الطالب مع خلفية ملونة
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #f8fafc, #e2e8f0); 
                           border: 1px solid #cbd5e0; border-radius: 12px; 
                           padding: 1rem; margin: 0.5rem 0;">
                """, unsafe_allow_html=True)
                
                col1, col2, col3 = st.columns([4, 2, 1])
                
                with col1:
                    st.write(f"**👤 {student[1]}**")
                    st.write(f"📱 {student[5]} | 🏠 {student[4][:20]}{'...' if len(student[4]) > 20 else ''}")
                    st.caption(f"📅 مسجل في: {student[8]} | جنس: {student[3]}")
                
                with col2:
                    total_amount = student[6] + student[7]
                    st.metric("💰 إجمالي الرسوم", f"{total_amount:.0f} د.ع")
                    if student[7] > 0:
                        st.caption(f"أساسي: {student[6]:.0f} + إضافي: {student[7]:.0f}")
                    else:
                        st.caption(f"الرسوم الأساسية فقط")
                
                with col3:
                    st.markdown("<br>", unsafe_allow_html=True)  # مساحة
                    if st.button(f"🗑️ حذف", key=f"delete_student_{student[0]}", 
                               help=f"حذف الطالب: {student[1]}", type="secondary"):
                        st.session_state.confirm_deletion = {
                            'type': 'student',
                            'data': student,
                            'id': student[0]
                        }
                        st.rerun()
                
                st.markdown("</div>", unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)
    else:
        st.info("🔍 لم يتم العثور على طلاب مطابقين للبحث")

def show_expense_deletion_section():
    """عرض قسم حذف الصرفيات"""
    st.subheader("💸 حذف الصرفيات")
    
    expenses = get_all_expenses()
    
    if not expenses:
        st.info("📋 لا توجد صرفيات للحذف")
        return
    
    # التحقق من وجود تأكيد حذف في الجلسة
    if st.session_state.get('confirm_deletion', {}).get('type') == 'expense':
        item_data = st.session_state.confirm_deletion['data']
        item_id = st.session_state.confirm_deletion['id']
        show_deletion_confirmation("صرفية", item_data, delete_expense, item_id)
        return
    
    # البحث في الصرفيات
    search_expense = st.text_input("🔍 البحث في الصرفيات", placeholder="ادخل البيان أو المبلغ...")
    
    filtered_expenses = expenses
    if search_expense:
        filtered_expenses = [exp for exp in expenses 
                           if search_expense.lower() in exp[2].lower() or 
                           search_expense in str(exp[1])]
    
    if filtered_expenses:
        st.write(f"📊 عدد الصرفيات: {len(filtered_expenses)}")
        
        # عرض الصرفيات مع أزرار الحذف
        for expense in filtered_expenses:
            with st.container():
                # مربع معلومات الصرفية مع خلفية ملونة
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #fef2f2, #fee2e2); 
                           border: 1px solid #fca5a5; border-radius: 12px; 
                           padding: 1rem; margin: 0.5rem 0;">
                """, unsafe_allow_html=True)
                
                col1, col2, col3 = st.columns([4, 2, 1])
                
                with col1:
                    st.write(f"**💸 {expense[2]}**")
                    st.caption(f"📅 تاريخ الصرفية: {expense[3]}")
                
                with col2:
                    st.metric("💰 المبلغ", f"{expense[1]:.0f} د.ع")
                
                with col3:
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.button(f"🗑️ حذف", key=f"delete_expense_{expense[0]}", 
                               help=f"حذف الصرفية: {expense[2]}", type="secondary"):
                        st.session_state.confirm_deletion = {
                            'type': 'expense',
                            'data': expense,
                            'id': expense[0]
                        }
                        st.rerun()
                
                st.markdown("</div>", unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)
    else:
        st.info("🔍 لم يتم العثور على صرفيات مطابقة للبحث")

def show_receipt_deletion_section():
    """عرض قسم حذف الإيصالات"""
    st.subheader("🧾 حذف الإيصالات")
    
    receipts = get_all_receipts()
    
    if not receipts:
        st.info("📋 لا توجد إيصالات للحذف")
        return
    
    # التحقق من وجود تأكيد حذف في الجلسة
    if st.session_state.get('confirm_deletion', {}).get('type') == 'receipt':
        item_data = st.session_state.confirm_deletion['data']
        item_id = st.session_state.confirm_deletion['id']
        show_deletion_confirmation("إيصال", item_data, delete_receipt, item_id)
        return
    
    # البحث في الإيصالات
    search_receipt = st.text_input("🔍 البحث في الإيصالات", placeholder="ادخل البيان أو المبلغ...")
    
    filtered_receipts = receipts
    if search_receipt:
        filtered_receipts = [rec for rec in receipts 
                           if search_receipt.lower() in rec[2].lower() or 
                           search_receipt in str(rec[1])]
    
    if filtered_receipts:
        st.write(f"📊 عدد الإيصالات: {len(filtered_receipts)}")
        
        # عرض الإيصالات مع أزرار الحذف
        for receipt in filtered_receipts:
            with st.container():
                # مربع معلومات الإيصال مع خلفية ملونة
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #f0fff4, #c6f6d5); 
                           border: 1px solid #68d391; border-radius: 12px; 
                           padding: 1rem; margin: 0.5rem 0;">
                """, unsafe_allow_html=True)
                
                col1, col2, col3 = st.columns([4, 2, 1])
                
                with col1:
                    st.write(f"**🧾 {receipt[2]}**")
                    st.caption(f"📅 تاريخ الإيصال: {receipt[3]}")
                
                with col2:
                    st.metric("💰 المبلغ", f"{receipt[1]:.0f} د.ع")
                
                with col3:
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.button(f"🗑️ حذف", key=f"delete_receipt_{receipt[0]}", 
                               help=f"حذف الإيصال: {receipt[2]}", type="secondary"):
                        st.session_state.confirm_deletion = {
                            'type': 'receipt',
                            'data': receipt,
                            'id': receipt[0]
                        }
                        st.rerun()
                
                st.markdown("</div>", unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)
    else:
        st.info("🔍 لم يتم العثور على إيصالات مطابقة للبحث")
