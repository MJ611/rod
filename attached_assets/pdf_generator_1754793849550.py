import streamlit as st
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.lib import colors
from reportlab.pdfbase import pdfutils
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.colors import HexColor
import pandas as pd
from datetime import datetime
import os
import io

# تسجيل خط عربي (إذا كان متوفر)
def register_arabic_fonts():
    try:
        # محاولة استخدام خط عربي إذا كان متوفرا
        pdfmetrics.registerFont(TTFont('Arabic', '/System/Library/Fonts/Arial Unicode MS.ttf'))
        return True
    except:
        try:
            pdfmetrics.registerFont(TTFont('Arabic', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))
            return True
        except:
            return False

def create_students_report_pdf(students_data, title="كشف طلاب الروضة"):
    """إنشاء تقرير PDF لكشف الطلاب"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm,
                           topMargin=2*cm, bottomMargin=2*cm)
    
    elements = []
    styles = getSampleStyleSheet()
    
    # تسجيل الخطوط العربية
    has_arabic = register_arabic_fonts()
    
    # إنشاء أنماط مخصصة
    title_style = styles['Heading1'].clone('TitleStyle')
    title_style.alignment = TA_CENTER
    title_style.fontSize = 18
    title_style.spaceAfter = 20
    if has_arabic:
        title_style.fontName = 'Arabic'
    
    header_style = styles['Heading2'].clone('HeaderStyle')
    header_style.alignment = TA_CENTER
    header_style.fontSize = 14
    header_style.spaceAfter = 15
    if has_arabic:
        header_style.fontName = 'Arabic'
    
    # شعار الروضة (إذا كان متوفرا)
    try:
        if os.path.exists("logo.jpg"):
            logo = Image("logo.jpg", width=3*cm, height=3*cm)
            logo.hAlign = 'CENTER'
            elements.append(logo)
            elements.append(Spacer(1, 20))
    except:
        pass
    
    # عنوان التقرير
    elements.append(Paragraph("روضة قطر الندى الأهلية", title_style))
    elements.append(Paragraph(title, header_style))
    elements.append(Paragraph(f"تاريخ التقرير: {datetime.now().strftime('%Y-%m-%d %H:%M')}", header_style))
    elements.append(Spacer(1, 20))
    
    # إنشاء جدول البيانات
    if students_data and len(students_data) > 0:
        # تحضير البيانات للجدول
        headers = ['رقم التسلسل', 'اسم الطالب', 'العمر', 'الجنس', 'رقم الهاتف', 'رسوم التسجيل', 'الرسوم الشهرية', 'تاريخ التسجيل']
        
        table_data = [headers]
        
        for idx, student in enumerate(students_data, 1):
            row = [
                str(idx),
                student.get('اسم_الطالب', ''),
                str(student.get('العمر', '')),
                student.get('الجنس', ''),
                student.get('رقم_الهاتف', ''),
                f"{student.get('رسوم_التسجيل', 0)} د.ع",
                f"{student.get('الرسوم_الشهرية', 0)} د.ع",
                student.get('تاريخ_التسجيل', '')
            ]
            table_data.append(row)
        
        # إنشاء الجدول
        table = Table(table_data, colWidths=[1.5*cm, 4*cm, 1.5*cm, 1.5*cm, 3*cm, 2.5*cm, 2.5*cm, 2.5*cm])
        
        # تنسيق الجدول
        table.setStyle(TableStyle([
            # تنسيق الرأس
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#1f4e79')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            
            # تنسيق البيانات
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            
            # حدود الجدول
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            
            # تلوين الصفوف بالتناوب
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, HexColor('#f8fafc')])
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 20))
        
        # إحصائيات موجزة
        total_students = len(students_data)
        total_registration = sum(student.get('رسوم_التسجيل', 0) for student in students_data)
        total_monthly = sum(student.get('الرسوم_الشهرية', 0) for student in students_data)
        
        summary_data = [
            ['إجمالي عدد الطلاب', f"{total_students} طالب"],
            ['إجمالي رسوم التسجيل', f"{total_registration:.0f} د.ع"],
            ['إجمالي الرسوم الشهرية', f"{total_monthly:.0f} د.ع"],
            ['المتوقع الشهري', f"{total_monthly:.0f} د.ع"],
            ['المتوقع السنوي', f"{total_monthly * 12:.0f} د.ع"]
        ]
        
        summary_table = Table(summary_data, colWidths=[8*cm, 4*cm])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), HexColor('#f0f9ff')),
            ('TEXTCOLOR', (0, 0), (-1, -1), HexColor('#1f4e79')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, HexColor('#1f4e79')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        elements.append(Paragraph("الإحصائيات المالية", header_style))
        elements.append(summary_table)
    else:
        elements.append(Paragraph("لا توجد بيانات طلاب للعرض", header_style))
    
    # إنشاء PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer

def create_financial_report_pdf(income_data, expenses_data, title="التقرير المالي"):
    """إنشاء تقرير PDF مالي"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm,
                           topMargin=2*cm, bottomMargin=2*cm)
    
    elements = []
    styles = getSampleStyleSheet()
    
    # تسجيل الخطوط العربية
    has_arabic = register_arabic_fonts()
    
    # إنشاء أنماط مخصصة
    title_style = styles['Heading1'].clone('TitleStyle')
    title_style.alignment = TA_CENTER
    title_style.fontSize = 18
    title_style.spaceAfter = 20
    
    header_style = styles['Heading2'].clone('HeaderStyle')
    header_style.alignment = TA_CENTER
    header_style.fontSize = 14
    header_style.spaceAfter = 15
    
    # شعار الروضة
    try:
        if os.path.exists("logo.jpg"):
            logo = Image("logo.jpg", width=3*cm, height=3*cm)
            logo.hAlign = 'CENTER'
            elements.append(logo)
            elements.append(Spacer(1, 20))
    except:
        pass
    
    # عنوان التقرير
    elements.append(Paragraph("روضة قطر الندى الأهلية", title_style))
    elements.append(Paragraph(title, header_style))
    elements.append(Paragraph(f"تاريخ التقرير: {datetime.now().strftime('%Y-%m-%d %H:%M')}", header_style))
    elements.append(Spacer(1, 30))
    
    # الملخص المالي
    total_income = sum(income_data.values()) if income_data else 0
    total_expenses = sum(expense['المبلغ'] for expense in expenses_data) if expenses_data else 0
    net_profit = total_income - total_expenses
    
    financial_summary = [
        ['البند', 'المبلغ (د.ع)'],
        ['إجمالي الإيرادات', f"{total_income:.0f}"],
        ['إجمالي المصروفات', f"{total_expenses:.0f}"],
        ['صافي الربح', f"{net_profit:.0f}"]
    ]
    
    summary_table = Table(financial_summary, colWidths=[8*cm, 4*cm])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#1f4e79')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('BACKGROUND', (0, 1), (-1, -1), HexColor('#f8fafc')),
        ('TEXTCOLOR', (0, 1), (-1, -1), HexColor('#1f4e79')),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 2, HexColor('#1f4e79')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    
    elements.append(Paragraph("الملخص المالي", header_style))
    elements.append(summary_table)
    elements.append(Spacer(1, 30))
    
    # تفاصيل المصروفات إذا كانت موجودة
    if expenses_data and len(expenses_data) > 0:
        expense_headers = ['التاريخ', 'البيان', 'المبلغ (د.ع)', 'الفئة']
        expense_table_data = [expense_headers]
        
        for expense in expenses_data:
            row = [
                expense.get('التاريخ', ''),
                expense.get('البيان', ''),
                f"{expense.get('المبلغ', 0):.0f}",
                expense.get('الفئة', '')
            ]
            expense_table_data.append(row)
        
        expense_table = Table(expense_table_data, colWidths=[3*cm, 6*cm, 3*cm, 4*cm])
        expense_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#dc2626')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        elements.append(Paragraph("تفاصيل المصروفات", header_style))
        elements.append(expense_table)
    
    # إنشاء PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer