# Overview

This is a comprehensive kindergarten management system for "روضة قطر الندى الأهلية" (Qatar Al-Nada National Kindergarten) built with Python and Streamlit. The system provides a complete solution for managing student registration, financial tracking, expense management, and administrative operations for a kindergarten. It features a modern Arabic interface with comprehensive reporting capabilities, data export functionality, and automated backup systems.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Frontend Architecture
- **Primary Interface**: Streamlit web application providing a modern, responsive Arabic UI
- **Layout Design**: Multi-page navigation system with expandable sidebar for easy access to different modules
- **Visual Design**: Professional interface with gradient themes, glassmorphism effects, and CSS animations
- **Language Support**: Full Arabic language interface with right-to-left text support and proper Arabic typography
- **User Experience**: Interactive forms with validation, real-time feedback, and confirmation dialogs

## Backend Architecture
- **Framework**: Python-based application using Streamlit for web serving and UI rendering
- **Database Layer**: SQLite database with direct SQL operations and automated schema management
- **Modular Design**: Separated concerns across multiple specialized modules:
  - `app.py`: Main application dashboard and navigation controller
  - `db.py`: Database operations, schema management, and data persistence
  - `register.py`: Student registration forms and validation logic
  - `deletion_manager.py`: Secure deletion operations with confirmation workflows
  - `pdf_generator.py`: Report generation with Arabic text support
- **Data Processing**: Real-time calculations for financial metrics, statistics, and analytics

## Database Design
- **Database Engine**: SQLite with automatic database creation and backup management
- **Storage Location**: User home directory (`~/RodaQaterData/`) for data persistence
- **Schema Structure**: Multiple tables including students, expenses, receipts, and transaction logs
- **Data Integrity**: Comprehensive field validation and referential integrity
- **Backup System**: Automated timestamped backups with manual backup functionality

## Core Features
- **Student Management**: Complete student lifecycle from registration to deletion with comprehensive profiles
- **Financial Tracking**: Expense management, receipt handling, and income/expense analytics
- **Reporting System**: PDF generation for student rosters and financial reports with Arabic text support
- **Data Analytics**: Real-time dashboards showing enrollment statistics, gender distribution, and financial metrics
- **Security Features**: Confirmation dialogs for deletions and transaction logging for audit trails
- **Export Capabilities**: CSV and PDF export functionality for data portability

## Security Architecture
- **Data Protection**: Confirmation dialogs for all destructive operations
- **Audit Trail**: Transaction logging and deletion tracking for accountability
- **Backup Strategy**: Automated and manual backup systems to prevent data loss
- **Input Validation**: Form validation and data sanitization throughout the application

# External Dependencies

## Core Python Libraries
- **streamlit**: Web application framework for the main user interface
- **pandas**: Data manipulation and analysis for handling student and financial data
- **sqlite3**: Built-in Python database interface for data persistence
- **datetime**: Date and time handling for registration tracking and financial records

## PDF Generation Libraries
- **reportlab**: PDF document generation with Arabic text support
- **reportlab.lib**: Layout utilities, styles, and formatting for professional reports
- **reportlab.platypus**: High-level document building with tables and structured content
- **reportlab.pdfbase**: Font management and Arabic typography support

## System Libraries
- **os**: File system operations for database and backup management
- **shutil**: File operations for backup creation and data management
- **io**: In-memory file operations for PDF generation and data processing

## Optional Font Dependencies
- **Arabic Font Files**: System fonts for proper Arabic text rendering in PDF reports
- **TTF Font Support**: TrueType font handling for multilingual document generation