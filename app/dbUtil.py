
import sys
import bcrypt
import mysql.connector
import os

mydbInstance = None

def getDbInstance():
    global mydbInstance
    if(mydbInstance):
        print("existing instance", file=sys.stderr)
        return mydbInstance
    
    db_host = os.getenv("DB_HOST")
    db_name = os.getenv("DB_DATABASE")
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_port = os.getenv("DB_PORT")

    mydbInstance = mysql.connector.connect(user=db_user, password=db_password, 
                                           host= db_host, port=db_port, 
                                           database=db_name)
    
    cursor = mydbInstance.cursor()
    cursor.execute("SET time_zone = '+01:00';")
    print("Database timezone set to +01:00", file=sys.stderr)
    cursor.execute("SELECT VERSION();")
    db_ver = cursor.fetchone()[0]
    print(f"Successfully connected to database. Database version: {db_ver}", file=sys.stderr)
    return mydbInstance

def verify_password(user_pwd: str, hashed_pwd: str):
    try:
        return bcrypt.checkpw(user_pwd.encode('utf-8'), hashed_pwd.encode('utf-8'))
    except: 
        print('Unable to verify the user password', file=sys.stderr)
        return False

def create_secure_password(pwd: str):
    try:
        hashed_password = bcrypt.hashpw(pwd.encode('utf-8'), bcrypt.gensalt())
        return hashed_password.decode('utf-8')
    except: 
        print('Unable to create the user password', file=sys.stderr)
        return False


















# mydbInstance2 = mysql.connector.connect(user='frontend', host='db', port='3306', password='frontend-secret-password', database='af-frontend')