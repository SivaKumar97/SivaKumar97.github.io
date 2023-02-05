import mysql.connector
import openpyxl
import csv
import os
import gspread
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from googleapiclient.errors import HttpError
import shutil
import patoolib
import time
import io
import pandas as pd

DATABASE_NAME = 'sha_project'
MV_TABLE_NAME = 'movie_info'
EMAIL = 'sivakumar9550.001@gmail.com'
FILE_NAME='SS_INFO.xlsx'
SCOPES = ['https://www.googleapis.com/auth/drive']
FOLDER_PATH = 'D:\Sha Project\Form Project'
FOLDER_NAME='Form Project'
DEST_FILE_PATH='D:\Sha Project\Form Project.rar'
credentials = Credentials.from_service_account_file('service_account.json', scopes=SCOPES)
PERCENT = 0
def getConnection(dbExist=False):
    if dbExist:
        return mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        use_pure=True,
        database=DATABASE_NAME
        )
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        use_pure=True
        )

def commitNdClose(cnx,cursor):
    cnx.commit()
    cursor.close()
    cnx.close()

def checkDBExist(cursor):
    check_db = f"SHOW DATABASES LIKE '{DATABASE_NAME}'"
    cursor.execute(check_db)
    result = cursor.fetchone()
    if result is None:
        create_db = f"CREATE DATABASE {DATABASE_NAME}"
        cursor.execute(create_db)

def createIntialDatas():
    cnx  = getConnection()
    cursor  = cnx.cursor()
    createTable(cursor,cnx)

def createTable(cursor,cnx):
    checkDBExist(cursor)
    use_db = f"USE {DATABASE_NAME}"
    cursor.execute(use_db)
    # Create the table
    table = f"""CREATE TABLE {MV_TABLE_NAME} (
        id int NOT NULL AUTO_INCREMENT unique primary key,
        name VARCHAR(255) NOT NULL,
        actName VARCHAR(255) NOT NULL,
        imageLink VARCHAR(255) NOT NULL,
        downloadLink VARCHAR(255) NOT NULL,
        subLink VARCHAR(255) NOT NULL,
        rating INT NOT NULL
    );"""
    cursor.execute(table)
    commitNdClose(cnx,cursor)

def dropDataBase():
    cnx  = getConnection()
    cursor  = cnx.cursor()
    cursor.execute('drop database sha_project')
    commitNdClose(cnx,cursor)


def addMvRow(payload):
    cnx  = getConnection(True)
    cursor  = cnx.cursor()
    name = payload["name"]
    actName = payload["actName"]
    imageLink = payload["img"]
    downloadLink = payload["downloadLink"]
    subLink = payload["subLink"]
    rating = int(payload["rating"])

    # Insert the values into the table
    query = f"INSERT INTO {MV_TABLE_NAME} (name, actName, imageLink, downloadLink, subLink, rating) VALUES (%s, %s, %s, %s, %s, %s)"
    values = (name, actName, imageLink, downloadLink, subLink, rating)
    cursor.execute(query, values)
    row  = getOneData(cursor)
    commitNdClose(cnx,cursor)
    response=getRowObj([row])
    return response

def updateMovieRow(payload):
    cnx  = getConnection(True)
    cursor  = cnx.cursor()
    id = payload["mvId"]
    name = payload["name"]
    actName = payload["actName"]
    imageLink = payload["img"]
    downloadLink = payload["downloadLink"]
    subLink = payload["subLink"]
    rating = int(payload["rating"])
    query = (
        f"UPDATE {MV_TABLE_NAME} SET "
        "name = %s, actName = %s, imageLink = %s, downloadLink = %s, subLink = %s, rating = %s "
        "WHERE id = %s"
    )
    cursor.execute(query, (name, actName, imageLink, downloadLink, subLink, rating, id))
    row  = getOneData(cursor,id)
    commitNdClose(cnx,cursor)
    response=getRowObj([row])
    return response

def getOneData(cursor, id=False):
    if id:
        print("if executed")
        select_query = (
        f"SELECT * FROM {MV_TABLE_NAME} "
        f"WHERE id = {id}"
        )
    else:
        print("else executed")
        select_query = (
        f"SELECT * FROM {MV_TABLE_NAME} "
        "WHERE id = LAST_INSERT_ID()"
        )
    cursor.execute(select_query)
    result = cursor.fetchone()
    return result

def getMovieDetails(field,type):
    cnx  = getConnection(True)
    cursor  = cnx.cursor()
    sortBy = f"ORDER BY {field} {type}" if field else ""
    cursor.execute(f"SELECT * FROM {MV_TABLE_NAME} {sortBy};")
    rows = cursor.fetchall()
    response = getRowObj(rows)
    commitNdClose(cnx,cursor)
    return response

def searchMovieDetail(value):
    cnx  = getConnection(True)
    cursor  = cnx.cursor()
    sql = f"SELECT * FROM {MV_TABLE_NAME} WHERE name like '%{value}%'"
    cursor.execute(sql)
    rows = cursor.fetchall()
    response = getRowObj(rows)
    commitNdClose(cnx,cursor)
    return response

def deleteMovieDetail(id):
    cnx  = getConnection(True)
    cursor  = cnx.cursor()
    sql = f"DELETE FROM {MV_TABLE_NAME} WHERE id = '{id}'"
    print("Sql Qurey : ",sql)
    cursor.execute(sql)
    commitNdClose(cnx,cursor)

def getRowObj(rows):
    response = []
    for row in rows:
        response.append({
                "mvId": row[0],
                "name": row[1],
                "actName": row[2],
                "img": row[3],
                "downloadLink": row[4],
                "subLink": row[5],
                "rating": row[6]
        })
    return response

def get_file_id(service, file_name):
    query = "name='" + file_name + "'"
    results = service.files().list(q=query, fields="nextPageToken, files(id, name)").execute()
    files = results.get("files", [])
    if len(files) > 0:
        return files[0]['id']
    else:
        return None

def uploadLive():
    data = getMovieDetails("","")
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    if data:
        data = getRowObj([('Movie ID','Name','Act Name','Image Link','Download Link','Sub Link','Rating')]) + data
        for row_index, row in enumerate(data, start=1):
            for col_index, cell in enumerate(row, start=1):
                sheet.cell(row=row_index, column=col_index, value=row[cell])
    else:
        print("There is no data available for export")
        return {'responseText': 'failure', 'message' : 'There is no data available for export'}
    filename = FILE_NAME
    workbook.save(filename)
    mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    service = build('drive', 'v3', credentials=credentials)
    file = uploadFile(service,filename,mimetype,filename)
    print(f"File ID: {file.get('id')}")
    share_file(service, file.get('id'))
    deleteExistFile(filename)

def uploadFile(service,filename,mimetype,filePath):
    file_id = get_file_id(service, filename)
    if file_id:
        file_metadata = {'name': filename, mimetype: mimetype}
        media = MediaFileUpload(filePath, mimetype)
        file = service.files().update(fileId=file_id, body=file_metadata, media_body=media, fields='id').execute()
    else:
        file_metadata = {'name': filename,mimetype: mimetype}
        media = MediaFileUpload(filePath, mimetype)
        file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    return file
   
def share_file(service, file_id, email=EMAIL):
    file = service.files().get(fileId=file_id, fields='id, permissions').execute()
    permissions = file.get('permissions', [])
    new_permission = {
        'type': 'user',
        'role': 'writer',
        'emailAddress': email
    }
    permissions.append(new_permission)
    service.permissions().create(fileId=file_id, body=new_permission, fields='id').execute()
    print('Shared Files Successfully')

def deleteAllServiceFiles():
    service = build('drive', 'v3', credentials=credentials)

    # Get all the files in the Google Drive
    results = service.files().list(fields="nextPageToken, files(id, name)").execute()
    items = results.get("files", [])
    print("Items : ",items)

    # Loop through all the files and delete them
    for item in items:
        file_id = item['id']
        service.files().delete(fileId=file_id).execute()

    print("All files deleted")

def progress_update():
    global PERCENT
    folder_path = FOLDER_PATH
    destination_file = DEST_FILE_PATH
    source_size = 0
    for dirpath, dirnames, filenames in os.walk(folder_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            source_size += os.path.getsize(fp)
    if os.path.exists(destination_file):
        while PERCENT < 99:
            dest_size = os.path.getsize(destination_file)
            NEW_PERCENT = dest_size / (source_size/(source_size/104857600)) * 100
            if NEW_PERCENT > 100:
                yield f"{PERCENT}"
            elif PERCENT == 100:
                yield f"{PERCENT}"
            else:
                PERCENT = NEW_PERCENT
                yield f"{PERCENT}"
            time.sleep(1.0)
    print("End of Progress---",PERCENT)
    PERCENT = 0

def deleteExistFile(destination_file=DEST_FILE_PATH):
    if os.path.exists(destination_file):
        os.remove(destination_file)

def uploadProject():
    global PERCENT
    PERCENT = 0
    folder_path = FOLDER_PATH
    destination_file=DEST_FILE_PATH
    patoolib.create_archive(destination_file, (folder_path,))
    PERCENT = 100
    print("Folder compressed to:", folder_path)
    service = build('drive', 'v3', credentials=credentials)
    file = uploadFile(service,f'{FOLDER_NAME}.rar','application/epub+zip',DEST_FILE_PATH)
    print(f"File ID: {file.get('id')}")
    share_file(service, file.get('id'))
    deleteExistFile()

def importMvDetails():
    service = build('drive', 'v3', credentials=credentials)
    results = service.files().list(q=f"name='{FILE_NAME}' and mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'", fields="nextPageToken, files(id, name)").execute()
    items = results.get("files", [])
    print("itesm :",items)
    if not items:
        print(f"No file found with name '{FILE_NAME}'.")
    else:
        file_id = items[0]["id"]
        request = service.files().get_media(fileId=file_id)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print("Download in progress")
        fh.seek(0)
        print("Download Completed")
        with open(FILE_NAME, "wb") as f:
            f.write(fh.read())
            print("Writing Completed")
        df = pd.read_excel(FILE_NAME)
        data = df.to_dict('records')
        cnx  = getConnection(True)
        cursor  = cnx.cursor()
        for record in data:
           query = f"INSERT INTO {MV_TABLE_NAME} (name, actName, imageLink, downloadLink, subLink, rating) VALUES (%s, %s, %s, %s, %s, %s)"
           values = ("" if pd.isna(record['Name']) else record["Name"],"" if pd.isna(record['Act Name']) else record["Act Name"], "" if pd.isna(record['Image Link']) else record["Image Link"], "" if pd.isna(record['Download Link']) else record["Download Link"]  ,"" if pd.isna(record['Sub Link']) else record["Sub Link"], record["Rating"])
           cursor.execute(query, values)
        commitNdClose(cnx,cursor)
        return getMovieDetails("","")


    