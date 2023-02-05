from flask import Flask, request, jsonify, Response
from mysql_query import createIntialDatas,progress_update,importMvDetails, deleteExistFile, uploadLive,uploadProject, dropDataBase,addMvRow, getMovieDetails, updateMovieRow, searchMovieDetail,deleteMovieDetail
from flask_cors import CORS
app = Flask(__name__)
CORS(app)

#Path API Route
@app.route('/getPath')
def paths():
    return {"notepad":{"name":"notepad","path":"C:\\\\Program Files (x86)\\\\Notepad++\\\\notepad++.exe"},"discord":{"name":"discord","path":"C:\\\\Users\\\\ashut\\\\AppData\\\\Local\\\\Discord\\\\app-1.0.9003\\\\Discord.exe"},"calculator":{"name":"calculator","path":"C:\\\\Windows\\\\System32\\\\calc.exe"},"enhancement":{"name":"enhancement","path":"C:\\\\Users\\\\shahin-zt381\\\\Desktop\\\\SHORTCUTS\\\\CMDFiles\\\\SHA_ENHANCEMENT_R.bat"},"enhancement with":{"name":"enhancement with","path":"C:\\\\Users\\\\shahin-zt381\\\\Desktop\\\\SHORTCUTS\\\\CMDFiles\\\\SHA_ENHANCEMENT_RUN.bat"},"react":{"name":"react","path":"C:\\\\Users\\\\shahin-zt381\\\\Desktop\\\\SHORTCUTS\\\\CMDFiles\\\\SHA_REACT_R.bat"},"react with":{"name":"react with","path":"C:\\\\Users\\\\shahin-zt381\\\\Desktop\\\\SHORTCUTS\\\\CMDFiles\\\\SHA_REACT_RUN.bat"},"unittest":{"name":"unittest","path":"C:\\\\Users\\\\shahin-zt381\\\\Desktop\\\\SHORTCUTS\\\\CMDFiles\\\\UNITTEST.bat"},"unittest with":{"name":"unittest with","path":"C:\\\\Users\\\\shahin-zt381\\\\Desktop\\\\SHORTCUTS\\\\CMDFiles\\\\UNITTEST_RUN.bat"},"feature npm":{"name":"feature npm","path":"C:\\\\Users\\\\shahin-zt381\\\\Desktop\\\\SHORTCUTS\\\\CMDFiles\\\\SHA_FEATURE_NPM.bat"},"feature logs":{"name":"feature logs","path":"C:\\\\Users\\\\shahin-zt381\\\\Desktop\\\\SHORTCUTS\\\\CMDFiles\\\\SHA_FEATURE_LOGS.bat"},"enhancement npm":{"name":"enhancement npm","path":"C:\\\\Users\\\\shahin-zt381\\\\Desktop\\\\SHORTCUTS\\\\CMDFiles\\\\SHA_ENHANCEMENT_NPM"},"enhancement logs":{"name":"enhancement logs","path":"C:\\\\Users\\\\shahin-zt381\\\\Desktop\\\\SHORTCUTS\\\\CMDFiles\\\\SHA_ENHANCEMENT_LOGS.bat"},"enhancement docs":{"name":"enhancement docs","path":"C:\\\\Users\\\\shahin-zt381\\\\Desktop\\\\SHORTCUTS\\\\CMDFiles\\\\SHA_ENHANCEMENT_DOCS.bat"},"cook with comali":{"name":"cook with comali","path":"C:\\\\Users\\\\shahin-zt381\\\\Desktop\\\\SHORTCUTS\\\\CMDFiles\\\\MYFILES_CWC.bat"},"myfiles":{"name":"myfiles","path":"C:\\\\Users\\\\shahin-zt381\\\\Desktop\\\\SHORTCUTS\\\\CMDFiles\\\\MYFILES.bat"},"image to text":{"name":"image to text","path":"C:\\\\Users\\\\shahin-zt381\\\\Desktop\\\\SHORTCUTS\\\\CMDFiles\\\\IMGTEXT.bat"},"eclipse":{"name":"eclipse","path":"C:\\\\Users\\\\shahin-zt381\\\\Desktop\\\\SHORTCUTS\\\\CMDFiles\\\\ECLIPSE.bat"},"docker":{"name":"docker","path":"C:\\\\Users\\\\shahin-zt381\\\\Desktop\\\\SHORTCUTS\\\\CMDFiles\\\\DOCKER.bat"},"vlc media":{"name":"vlc media","path":"C:\\\\Program Files\\\\VideoLAN\\\\VLC\\\\vlc.exe"}}

#Create Database
@app.route('/api/v1/creatInitial')
def createInitial():
    try :
        createIntialDatas()
        print("Created Successfully")
        return {
            'responseText' : 'success'
        }
    except Exception as error:
        print("An error occured", error)
    return {
        'responseText': 'failure'
    }
@app.route('/api/v1/dropDB')
def dropDB():
    try :
        dropDataBase()
        print("DB Dropped Successfully")
        return {
            'responseText' : 'success'
        }
    except Exception as error:
        print("An error occured", error)
    return {
        'responseText': 'failure'
    }
@app.route('/api/v1/addMvDetails', methods=['POST'])
def addMvDetails():
    payload = request.get_json()
    try:
        mvDetails = addMvRow(payload)
        return {
            'responseText': 'success',
            'response' : 200,
            'mvDetails' : mvDetails
         }
    except Exception as error:
        print("An error occured", error)
    return {
            'responseText': 'failure'
         }
@app.route('/api/v1/getMvDetails')
def getMvDetails():
    field = request.args.get("field")
    type = request.args.get("type")
    try:
        mvDetails = getMovieDetails(field,type)
        return {
            'responseText': 'success',
            'response' : 200,
            'mvDetails' : mvDetails
         }
    except Exception as error:
        print("An error occured", error)
    return {
            'responseText': 'failure'
         }
@app.route('/api/v1/updateMvDetails', methods=['POST'])
def updateMvDetails():
    payload = request.get_json()
    try:
        mvDetails = updateMovieRow(payload)
        return {
            'responseText': 'success',
            'response' : 200,
            'mvDetails' : mvDetails
         }
    except Exception as error:
        print("An error occured", error)
    return {
            'responseText': 'failure'
         }

@app.route('/api/v1/searchMv')
def searchMvDetails():
    query = request.args.get("searchStr")
    try:
        mvDetails = searchMovieDetail(query)
        return {
            'responseText': 'success',
            'response' : 200,
            'mvDetails' : mvDetails
         }
    except Exception as error:
        print("An error occured", error)
    return {
            'responseText': 'failure'
         }

@app.route("/api/v1/deleteDv/<id>", methods=["DELETE"])
def deleteMvDetail(id):
    try:
        deleteMovieDetail(id)
        return {
            'responseText': 'success',
            'response' : 200
         }
    except Exception as error:
        print("An error occured", error)
    return {
            'responseText': 'failure'
         }

@app.route("/api/v1/exportMv", methods=["POST"])
def exportMvDetails():
    try:
        uploadLive()
        return {
            'responseText': 'success',
            'response' : 200
         }
    except Exception as error:
        print("An error occured", error)
    return {
        'responseText': 'failure'
        }

@app.route("/api/v1/exportProject", methods=["POST"])
def exportProject():
    try:
        uploadProject()
        return {
            'responseText': 'success',
            'response' : 200
         }
    except Exception as error:
        print("An error occured", error)
    return {
        'responseText': 'failure'
        }

@app.route("/api/v1/importMv", methods=["POST"])
def importMv():
    try:
        mvDetails = importMvDetails()
        return {
            'responseText': 'success',
            'response' : 200,
            'mvDetails' : mvDetails
         }
    except Exception as error:
        print("An error occured", error)
    return {
        'responseText': 'failure'
        }
@app.route("/api/v1/percentage")
def getPercentage():
    try:
        return Response(progress_update(), content_type='text/event-stream')
        # status ='completed' if percent > 92 else 'inprogress'
        # return {
        #     'responseText': 'success',
        #     'response' : 200,
        #     'status' : status,
        #     'percent' : percent
        #  }
    except Exception as error:
        print("An error occured", error)
    return {
        'responseText': 'failure'
        }



if __name__ == '__main__':
    app.run(debug=True)