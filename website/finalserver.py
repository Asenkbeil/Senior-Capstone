from flask import Flask, render_template, request, jsonify
import sqlite3
import uuid
import json
from PIL import Image
import base64
import os

#connect to database
conn = sqlite3.connect('Thesisdb.sqlite')
db = conn.cursor()

#create tables
db.execute("CREATE TABLE IF NOT EXISTS Images (uuid blob, imagepath blob)")
conn.commit()
conn.close()

app = Flask(__name__)

#handles posts from the console application
@app.route('/picture/post', methods=['POST'])
def post_picture():
    r = request

    #connect to database again
    conn = sqlite3.connect('Thesisdb.sqlite')
    db = conn.cursor() 

    id = uuid.uuid4() #creates random id
    #check if random id is used or not
    while(True):
        searchid = (str(id),)
        db.execute("SELECT Images.uuid FROM Images WHERE uuid = ?", searchid)
        if(db.fetchone() == None):
            break
        else:
            id = uuid.uuid4()
            #print(id)

    img = r.data#encoded string
    imagepath = "static/" + str(id) + ".jpg"
    #print(imagepath)
    image = open(imagepath, "wb")#creates jpg file
    image.write(base64.b64decode(img))#writes string to file
    image.close()
    
    imagepath = str(id) + ".jpg"

    #insert imagepath and id into database
    insert = (str(id), imagepath)
    db.execute("INSERT INTO Images VALUES(?,?)", insert)
    conn.commit()

    #close database
    conn.close()

    #prepare response with id
    #print('about to send that yung response')
    response = {'url': 'http://127.0.0.1:5000/picture/' + str(id)}
    return jsonify(response)


@app.route('/picture/namechange', methods=['POST'])
def nameChange():
    #get request
    r = request
    
    #connect to database
    conn = sqlite3.connect('Thesisdb.sqlite')
    db = conn.cursor() 

    #check if name has been used
    newid = r.form['userinput']
    searchnewid = (newid,)
    db.execute("SELECT Images.uuid FROM Images WHERE uuid = ?", searchnewid)
    #if it has not
    if(db.fetchone() == None):
        #change id and filepath in database
        uuid = r.form['uuid']
        searchuuid = (uuid,)
        #delete row
        db.execute("DELETE FROM Images WHERE uuid = ?", searchuuid)
        conn.commit()

        #create new row
        searchnewfilepath = newid + '.jpg'
        
        #insertvals = (newid, searchnewfilepath)
        #print(insertvals)
        db.execute("INSERT INTO Images (uuid, picture) VALUES (?,?)", (newid, searchnewfilepath))
        conn.commit()

        #change filename on disk
        oldfilepath = 'static/' + uuid + '.jpg'
        newfilepath = 'static/' + newid + '.jpg'
        exists = os.path.isfile(oldfilepath)
        if(exists):
            os.rename(oldfilepath, newfilepath)

        #close database
        conn.close()

        #send response saying good
        return 'good'

    #else send response saying bad (client will have to retry)
    else:
        #close database
        conn.close()

        #response
        return 'bad'
    


@app.route('/picture/<string:id>/')
def picture(id):
    #open database
    conn = sqlite3.connect('Thesisdb.sqlite')
    db = conn.cursor()

    #query to find image with correct id
    searchid = (id,)
    db.execute("SELECT Images.picture FROM Images WHERE Images.uuid = ?", searchid)
    picture = db.fetchone()
    picture = picture[0] #fetchone() returns a tuple, we only want the first value

    #the picture variable is the filepath to the wanted image
    
    conn.close()#close database
    print(picture)
    return render_template('picture.html', picture = picture)


app.run()
