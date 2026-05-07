import re
from tkinter import messagebox, StringVar

class RegexValidator:
    @staticmethod
    def validate_email(email):
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.fullmatch(pattern, email)), pattern
    
    @staticmethod
    def validate_phone(phone):
        pattern = r'^(\+\d{1,3}\s?)?(\d{2,3}[\s-]?)?\d{3,4}[\s-]?\d{3,4}$'
        return bool(re.fullmatch(pattern, phone)), pattern
    
    @staticmethod
    def validate_url(url):
        pattern = r'^(https?:\/\/)?([\da-z\.-]+)\.([a-z\.]{2,6})([\/\w \.-]*)*\/?$'
        return bool(re.fullmatch(pattern, url)), pattern
    
    @staticmethod
    def validate_date(date):
        pattern = r'^(\d{2}\/\d{2}\/\d{4})|(\d{4}-\d{2}-\d{2})$'
        return bool(re.fullmatch(pattern, date)), pattern
    
    @staticmethod
    def validate_password(password):
        pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'
        return bool(re.fullmatch(pattern, password)), pattern


