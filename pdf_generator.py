"""
نظام إنشاء تقارير PDF محسن للنصوص العربية
"""

from reportlab.lib.pagesizes import A4, letter
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
from datetime import datetime
import os
import io

def register_arabic_fonts():
    """تسجيل الخطوط العربية المتاحة"""
    try:
        # محاولة استخدام خط عربي
        pdfmetrics.registerFont(TTFont('Arabic', '/System/Library/Fonts/Arial.ttf'))
        return 'Arabic'
    except:
        try:
            pdfmetrics.registerFont(TTFont('Arabic', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))
            return 'Arabic'
        except:
            try:
                pdfmetrics.registerFont(TTFont('Arabic', '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf'))
                return 'Arabic'
            except:
                # استخدام خط افتراضي
                return 'Helvetica'

def create_students_report_pdf(students_data, title="كشف طلاب الروضة"):
    """إنشاء تقرير PDF للطلاب مع تحسين التنسيق"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=A4, 
        rightMargin=1.5*cm, 
        leftMargin=1.5*cm,
        topMargin=2*cm, 
        bottomMargin=2*cm
    )
    
    elements = []
    styles = getSampleStyleSheet()
    
    # تسجيل الخطوط
    font_name = register_arabic_fonts()
    
    # أنماط مخصصة
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontName=font_name,
        fontSize=16,
        textColor=HexColor('#1f4e79'),
        alignment=TA_CENTER,
        spaceAfter=20,
        spaceBefore=10
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontName=font_name,
        fontSize=12,
        textColor=HexColor('#374151'),
        alignment=TA_CENTER,
        spaceAfter=10
    )
    
    # إضافة الشعار
    try:
        if os.path.exists("logo.jpg"):
            logo = Image("logo.jpg", width=2.5*cm, height=2.5*cm)
            logo.hAlign = 'CENTER'
            elements.append(logo)
            elements.append(Spacer(1, 10))
    except:
        pass
    
    # العناوين
    elements.append(Paragraph("روضة قطر الندى الأهلية", title_style))
    elements.append(Paragraph(title, subtitle_style))
    elements.append(Paragraph(f"تاريخ التقرير: {datetime.now().strftime('%Y-%m-%d')}", subtitle_style))
    elements.append(Spacer(1, 20))
    
    # إنشاء الجدول
    if students_data and len(students_data) > 0:
        # إعداد العناوين
        headers = [
            'م',
            'اسم الطالب', 
            'العمر',
            'الجنس',
            'رقم الهاتف',
            'رسوم التسجيل',
            'الرسوم الشهرية',
            'تاريخ التسجيل'
        ]
        
        # إعداد البيانات
        table_data = [headers]
        
        for idx, student in enumerate(students_data, 1):
            # تنظيف البيانات وضمان عدم وجود قيم فارغة
            name = str(student.get('اسم_الطالب', 'غير محدد'))
            age = str(student.get('العمر', '-'))
            gender = str(student.get('الجنس', '-'))
            phone = str(student.get('رقم_الهاتف', '-'))
            reg_fee = student.get('رسوم_التسجيل', 0)
            monthly_fee = student.get('الرسوم_الشهرية', 0)
            reg_date = str(student.get('تاريخ_التسجيل', '-'))
            
            row = [
                str(idx),
                name,
                age,
                gender,
                phone,
                f"{reg_fee} د.ع" if reg_fee else "0 د.ع",
                f"{monthly_fee} د.ع" if monthly_fee else "0 د.ع",
                reg_date
            ]
            table_data.append(row)
        
        # إنشاء الجدول مع أعمدة متوازنة
        col_widths = [1*cm, 3*cm, 1.2*cm, 1.2*cm, 2.5*cm, 2*cm, 2*cm, 2.5*cm]
        table = Table(table_data, colWidths=col_widths, repeatRows=1)
        
        # تنسيق الجدول
        table.setStyle(TableStyle([
            # تنسيق الرأس
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#1f4e79')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, 0), font_name),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('FONTNAME', (0, 1), (-1, -1), font_name),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            
            # تنسيق البيانات
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('LINEBELOW', (0, 0), (-1, 0), 2, HexColor('#1f4e79')),
            
            # تلوين الصفوف بالتناوب
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, HexColor('#f8fafc')])
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 20))
        
        # إحصائيات موجزة
        total_students = len(students_data)
        total_registration = sum(float(student.get('رسوم_التسجيل', 0)) for student in students_data)
        total_monthly = sum(float(student.get('الرسوم_الشهرية', 0)) for student in students_data)
        
        # جدول الإحصائيات
        summary_title = Paragraph("الإحصائيات المالية", subtitle_style)
        elements.append(summary_title)
        
        summary_data = [
            ['البيان', 'القيمة'],
            ['إجمالي عدد الطلاب', f"{total_students} طالب"],
            ['إجمالي رسوم التسجيل', f"{total_registration:,.0f} د.ع"],
            ['إجمالي الرسوم الشهرية', f"{total_monthly:,.0f} د.ع"],
            ['المتوقع السنوي', f"{total_monthly * 12:,.0f} د.ع"]
        ]
        
        summary_table = Table(summary_data, colWidths=[6*cm, 4*cm])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#1f4e79')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('BACKGROUND', (0, 1), (-1, -1), HexColor('#f0f9ff')),
            ('TEXTCOLOR', (0, 1), (-1, -1), HexColor('#1f4e79')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, -1), font_name),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('LINEBELOW', (0, 0), (-1, 0), 2, HexColor('#1f4e79'))
        ]))
        
        elements.append(summary_table)
    else:
        # رسالة عدم وجود بيانات
        no_data_style = ParagraphStyle(
            'NoData',
            parent=styles['Normal'],
            fontName=font_name,
            fontSize=14,
            textColor=colors.red,
            alignment=TA_CENTER
        )
        elements.append(Paragraph("لا توجد بيانات طلاب للعرض", no_data_style))
    
    # إنشاء PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer

def create_financial_report_pdf(expenses_data, receipts_data, title="التقرير المالي"):
    """إنشاء تقرير مالي مفصل"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=A4, 
        rightMargin=1.5*cm, 
        leftMargin=1.5*cm,
        topMargin=2*cm, 
        bottomMargin=2*cm
    )
    
    elements = []
    styles = getSampleStyleSheet()
    font_name = register_arabic_fonts()
    
    # أنماط مخصصة
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontName=font_name,
        fontSize=16,
        textColor=HexColor('#1f4e79'),
        alignment=TA_CENTER,
        spaceAfter=20
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontName=font_name,
        fontSize=12,
        textColor=HexColor('#374151'),
        alignment=TA_CENTER,
        spaceAfter=15
    )
    
    # الشعار والعناوين
    try:
        if os.path.exists("logo.jpg"):
            logo = Image("logo.jpg", width=2.5*cm, height=2.5*cm)
            logo.hAlign = 'CENTER'
            elements.append(logo)
            elements.append(Spacer(1, 10))
    except:
        pass
    
    elements.append(Paragraph("روضة قطر الندى الأهلية", title_style))
    elements.append(Paragraph(title, subtitle_style))
    elements.append(Paragraph(f"تاريخ التقرير: {datetime.now().strftime('%Y-%m-%d')}", subtitle_style))
    elements.append(Spacer(1, 20))
    
    # قسم الإيصالات
    if receipts_data:
        elements.append(Paragraph("الإيصالات والإيرادات", subtitle_style))
        
        receipts_headers = ['م', 'البيان', 'المبلغ', 'التاريخ']
        receipts_table_data = [receipts_headers]
        
        total_receipts = 0
        for idx, receipt in enumerate(receipts_data, 1):
            amount = float(receipt.get('amount', 0))
            total_receipts += amount
            
            row = [
                str(idx),
                str(receipt.get('description', '')),
                f"{amount:,.0f} د.ع",
                str(receipt.get('date', ''))
            ]
            receipts_table_data.append(row)
        
        # إضافة سطر الإجمالي
        receipts_table_data.append(['', 'الإجمالي', f"{total_receipts:,.0f} د.ع", ''])
        
        receipts_table = Table(receipts_table_data, colWidths=[1*cm, 6*cm, 3*cm, 3*cm])
        receipts_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#059669')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('BACKGROUND', (0, -1), (-1, -1), HexColor('#d1fae5')),
            ('TEXTCOLOR', (0, -1), (-1, -1), HexColor('#059669')),
            ('FONTNAME', (0, 0), (-1, -1), font_name),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, HexColor('#f0fdf4')])
        ]))
        
        elements.append(receipts_table)
        elements.append(Spacer(1, 20))
    
    # قسم المصروفات
    if expenses_data:
        elements.append(Paragraph("المصروفات والتكاليف", subtitle_style))
        
        expenses_headers = ['م', 'البيان', 'المبلغ', 'التاريخ']
        expenses_table_data = [expenses_headers]
        
        total_expenses = 0
        for idx, expense in enumerate(expenses_data, 1):
            amount = float(expense.get('amount', 0))
            total_expenses += amount
            
            row = [
                str(idx),
                str(expense.get('description', '')),
                f"{amount:,.0f} د.ع",
                str(expense.get('date', ''))
            ]
            expenses_table_data.append(row)
        
        # إضافة سطر الإجمالي
        expenses_table_data.append(['', 'الإجمالي', f"{total_expenses:,.0f} د.ع", ''])
        
        expenses_table = Table(expenses_table_data, colWidths=[1*cm, 6*cm, 3*cm, 3*cm])
        expenses_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#dc2626')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('BACKGROUND', (0, -1), (-1, -1), HexColor('#fee2e2')),
            ('TEXTCOLOR', (0, -1), (-1, -1), HexColor('#dc2626')),
            ('FONTNAME', (0, 0), (-1, -1), font_name),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, HexColor('#fef2f2')])
        ]))
        
        elements.append(expenses_table)
        elements.append(Spacer(1, 20))
    
    # الملخص المالي
    total_receipts = sum(float(r.get('amount', 0)) for r in receipts_data) if receipts_data else 0
    total_expenses = sum(float(e.get('amount', 0)) for e in expenses_data) if expenses_data else 0
    net_balance = total_receipts - total_expenses
    
    summary_title = Paragraph("الملخص المالي", subtitle_style)
    elements.append(summary_title)
    
    balance_color = HexColor('#059669') if net_balance >= 0 else HexColor('#dc2626')
    balance_bg = HexColor('#d1fae5') if net_balance >= 0 else HexColor('#fee2e2')
    
    financial_summary = [
        ['البيان', 'المبلغ'],
        ['إجمالي الإيرادات', f"{total_receipts:,.0f} د.ع"],
        ['إجمالي المصروفات', f"{total_expenses:,.0f} د.ع"],
        ['الرصيد الصافي', f"{net_balance:,.0f} د.ع"]
    ]
    
    summary_table = Table(financial_summary, colWidths=[6*cm, 4*cm])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#1f4e79')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('BACKGROUND', (0, 1), (1, 2), HexColor('#f8fafc')),
        ('BACKGROUND', (0, 3), (1, 3), balance_bg),
        ('TEXTCOLOR', (0, 3), (1, 3), balance_color),
        ('FONTNAME', (0, 0), (-1, -1), font_name),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('LINEBELOW', (0, 0), (-1, 0), 2, HexColor('#1f4e79'))
    ]))
    
    elements.append(summary_table)
    
    # إنشاء PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer

def create_student_admission_receipt_pdf(student_data):
    """إنشاء إيصال قبول للطالب"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=A4, 
        rightMargin=2*cm, 
        leftMargin=2*cm,
        topMargin=2*cm, 
        bottomMargin=2*cm
    )
    
    elements = []
    styles = getSampleStyleSheet()
    font_name = register_arabic_fonts()
    
    # أنماط مخصصة للإيصال
    title_style = ParagraphStyle(
        'ReceiptTitle',
        parent=styles['Heading1'],
        fontName=font_name,
        fontSize=18,
        textColor=HexColor('#1f4e79'),
        alignment=TA_CENTER,
        spaceAfter=15
    )
    
    subtitle_style = ParagraphStyle(
        'ReceiptSubtitle',
        parent=styles['Heading2'],
        fontName=font_name,
        fontSize=14,
        textColor=HexColor('#059669'),
        alignment=TA_CENTER,
        spaceAfter=20
    )
    
    normal_style = ParagraphStyle(
        'ReceiptNormal',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=11,
        textColor=colors.black,
        alignment=TA_RIGHT,
        spaceAfter=8
    )
    
    # الشعار والعنوان
    try:
        if os.path.exists("logo.jpg"):
            logo = Image("logo.jpg", width=3*cm, height=3*cm)
            logo.hAlign = 'CENTER'
            elements.append(logo)
            elements.append(Spacer(1, 10))
    except:
        pass
    
    # عنوان الروضة
    elements.append(Paragraph("روضة قطر الندى الأهلية", title_style))
    elements.append(Paragraph("إيصال قبول طالب", subtitle_style))
    
    # معلومات الإيصال
    receipt_info = f"رقم الإيصال: {datetime.now().strftime('%Y%m%d%H%M%S')}"
    receipt_date = f"تاريخ الإيصال: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    
    elements.append(Paragraph(receipt_info, normal_style))
    elements.append(Paragraph(receipt_date, normal_style))
    elements.append(Spacer(1, 20))
    
    # بيانات الطالب في جدول منسق
    student_info_data = [
        ['البيان', 'القيمة'],
        ['اسم الطالب', str(student_data.get('اسم_الطالب', ''))],
        ['العمر', f"{student_data.get('العمر', '')} سنة"],
        ['الجنس', str(student_data.get('الجنس', ''))],
        ['رقم الهاتف', str(student_data.get('رقم_الهاتف', ''))],
        ['اسم ولي الأمر', str(student_data.get('اسم_ولي_الأمر', ''))],
        ['العنوان', str(student_data.get('العنوان', ''))],
        ['تاريخ التسجيل', str(student_data.get('تاريخ_التسجيل', ''))]
    ]
    
    student_table = Table(student_info_data, colWidths=[4*cm, 8*cm])
    student_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#1f4e79')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('BACKGROUND', (0, 1), (-1, -1), HexColor('#f8fafc')),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 0), (-1, -1), font_name),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (0, -1), 'CENTER'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('LINEBELOW', (0, 0), (-1, 0), 2, HexColor('#1f4e79'))
    ]))
    
    elements.append(student_table)
    elements.append(Spacer(1, 20))
    
    # الرسوم المالية
    financial_title = Paragraph("الرسوم المالية", subtitle_style)
    elements.append(financial_title)
    
    reg_fee = student_data.get('رسوم_التسجيل', 0)
    monthly_fee = student_data.get('الرسوم_الشهرية', 0)
    
    financial_data = [
        ['البيان', 'المبلغ'],
        ['رسوم التسجيل', f"{reg_fee:,.0f} د.ع"],
        ['الرسوم الشهرية', f"{monthly_fee:,.0f} د.ع"],
        ['إجمالي الرسوم السنوية', f"{reg_fee + (monthly_fee * 12):,.0f} د.ع"]
    ]
    
    financial_table = Table(financial_data, colWidths=[6*cm, 4*cm])
    financial_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#059669')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('BACKGROUND', (0, 1), (0, 2), HexColor('#f0fdf4')),
        ('BACKGROUND', (0, 3), (-1, 3), HexColor('#d1fae5')),
        ('TEXTCOLOR', (0, 1), (-1, -1), HexColor('#059669')),
        ('FONTNAME', (0, 0), (-1, -1), font_name),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('LINEBELOW', (0, 0), (-1, 0), 2, HexColor('#059669')),
        ('LINEBELOW', (0, 2), (-1, 2), 1, HexColor('#059669'))
    ]))
    
    elements.append(financial_table)
    elements.append(Spacer(1, 30))
    
    # شروط وأحكام
    terms_title = Paragraph("الشروط والأحكام", subtitle_style)
    elements.append(terms_title)
    
    terms_text = """
    • يجب دفع الرسوم الشهرية في بداية كل شهر
    • في حالة الغياب المستمر لأكثر من أسبوع يرجى إشعار الإدارة
    • الالتزام بمواعيد الحضور والانصراف المحددة
    • تطبيق التعليمات والقوانين الخاصة بالروضة
    • هذا الإيصال يؤكد قبول الطالب رسمياً في الروضة
    """
    
    terms_style = ParagraphStyle(
        'Terms',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=9,
        textColor=HexColor('#374151'),
        alignment=TA_RIGHT,
        rightIndent=20
    )
    
    elements.append(Paragraph(terms_text, terms_style))
    elements.append(Spacer(1, 20))
    
    # توقيع الإدارة
    signature_data = [
        ['', ''],
        ['توقيع ولي الأمر', 'توقيع الإدارة'],
        ['', ''],
        ['التاريخ: ___________', 'التاريخ: ___________']
    ]
    
    signature_table = Table(signature_data, colWidths=[6*cm, 6*cm])
    signature_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), font_name),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LINEABOVE', (0, 1), (-1, 1), 1, colors.black),
        ('SPAN', (0, 0), (-1, 0)),
        ('SPAN', (0, 2), (-1, 2))
    ]))
    
    elements.append(signature_table)
    
    # تذييل الصفحة
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=8,
        textColor=HexColor('#6b7280'),
        alignment=TA_CENTER
    )
    
    elements.append(Spacer(1, 20))
    elements.append(Paragraph("نشكركم لثقتكم في روضة قطر الندى الأهلية", footer_style))
    elements.append(Paragraph("للاستفسارات يرجى التواصل مع الإدارة", footer_style))
    
    # إنشاء PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer