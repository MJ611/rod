import streamlit as st
from datetime import date
from db import insert_student

def show_register_form():
    """عرض نموذج تسجيل طالب جديد"""
    st.header("📝 تسجيل طالب جديد")
    
    # معلومات إضافية
    st.info("💡 يرجى ملء جميع الحقول المطلوبة بدقة لضمان صحة البيانات")
    
    with st.form("student_registration_form", clear_on_submit=True):
        # قسم المعلومات الشخصية
        st.subheader("👤 المعلومات الشخصية")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # الاسم الرباعي
            name = st.text_input("الاسم الرباعي *", placeholder="أدخل الاسم الرباعي للطالب")
            
            # الجنس
            gender = st.selectbox("الجنس *", options=["ذكر", "أنثى"])
        
        with col2:
            # تاريخ الميلاد
            birthdate = st.date_input("تاريخ الميلاد *", value=date(2020, 1, 1))
            
            # رقم الهاتف
            phone = st.text_input("رقم الهاتف *", placeholder="أدخل رقم الهاتف")
        
        # العنوان
        address = st.text_input("العنوان *", placeholder="أدخل عنوان السكن")
        
        st.divider()
        
        # قسم المعلومات المالية
        st.subheader("💰 المعلومات المالية")
        
        col3, col4 = st.columns(2)
        
        with col3:
            # القسط
            fee = st.number_input("قسط الطالب (د.ع) *", min_value=0.0, value=0.0, step=1.0, 
                                format="%.2f")
        
        with col4:
            # الأجور الإضافية
            extra_fee = st.number_input("الأجور الإضافية (د.ع)", min_value=0.0, value=0.0, 
                                      step=1.0, format="%.2f")
        
        # عرض المجموع
        total_amount = fee + extra_fee
        if total_amount > 0:
            st.success(f"💵 إجمالي المبلغ: {total_amount:.2f} د.ع")
        
        st.divider()
        
        # تاريخ التسجيل
        st.subheader("📅 معلومات التسجيل")
        register_date = st.date_input("تاريخ التسجيل", value=date.today())
        
        # زر الحفظ
        submitted = st.form_submit_button("💾 حفظ البيانات", use_container_width=True, 
                                        type="primary")
        
        if submitted:
            # التحقق من الحقول المطلوبة
            errors = []
            
            if not name.strip():
                errors.append("الاسم الرباعي")
            if not address.strip():
                errors.append("العنوان")
            if not phone.strip():
                errors.append("رقم الهاتف")
            if fee <= 0:
                errors.append("قسط الطالب")
            
            if errors:
                st.error(f"❌ يرجى ملء الحقول التالية: {', '.join(errors)}")
                return
            
            try:
                # حفظ البيانات
                insert_student(
                    name=name.strip(),
                    birthdate=birthdate.strftime('%Y-%m-%d'),
                    gender=gender,
                    address=address.strip(),
                    phone=phone.strip(),
                    fee=fee,
                    extra_fee=extra_fee,
                    register_date=register_date.strftime('%Y-%m-%d')
                )
                
                st.success("✅ تم حفظ بيانات الطالب بنجاح!")
                st.balloons()
                
                # إنشاء إيصال قبول PDF
                student_data = {
                    'اسم_الطالب': name.strip(),
                    'العمر': str(date.today().year - birthdate.year),
                    'الجنس': gender,
                    'رقم_الهاتف': phone.strip(),
                    'اسم_ولي_الأمر': '',  # يمكن إضافته لاحقاً
                    'العنوان': address.strip(),
                    'رسوم_التسجيل': fee,
                    'الرسوم_الشهرية': extra_fee,
                    'تاريخ_التسجيل': register_date.strftime('%Y-%m-%d')
                }
                
                # استيراد دالة إنشاء PDF
                from pdf_generator import create_student_admission_receipt_pdf
                
                try:
                    pdf_buffer = create_student_admission_receipt_pdf(student_data)
                    
                    # عرض زر تحميل PDF
                    st.download_button(
                        label="📄 تحميل إيصال القبول",
                        data=pdf_buffer.getvalue(),
                        file_name=f"إيصال_قبول_{name.replace(' ', '_')}_{register_date.strftime('%Y%m%d')}.pdf",
                        mime="application/pdf",
                        type="secondary",
                        use_container_width=True
                    )
                except Exception as e:
                    st.warning(f"تم حفظ البيانات بنجاح، لكن حدث خطأ في إنشاء إيصال PDF: {str(e)}")
                
                # عرض ملخص البيانات المحفوظة
                st.info(f"""
                📋 **ملخص البيانات المحفوظة:**
                - **الاسم**: {name}
                - **الجنس**: {gender}
                - **تاريخ الميلاد**: {birthdate.strftime('%Y-%m-%d')}
                - **الهاتف**: {phone}
                - **القسط**: {fee:.2f} د.ع
                - **الأجور الإضافية**: {extra_fee:.2f} د.ع
                - **المجموع**: {total_amount:.2f} د.ع
                """)
                
                # تأخير إعادة التحميل للسماح بتحميل PDF
                if st.button("🔄 تسجيل طالب آخر", type="primary"):
                    st.rerun()
                
            except Exception as e:
                st.error(f"❌ حدث خطأ أثناء حفظ البيانات: {str(e)}")
                st.write("يرجى المحاولة مرة أخرى أو التواصل مع المسؤول")
