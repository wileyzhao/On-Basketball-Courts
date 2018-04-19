import os
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from passlib.apps import custom_app_context as pwd_context
from tempfile import mkdtemp
from passlib.context import CryptContext
import datetime
import time
import json
from flask_uploads import UploadSet, configure_uploads, IMAGES, patch_request_class
from werkzeug.utils import secure_filename
import time
from helpers import *
import math
from sql import *
# configure application
app = Flask(__name__)

# ensure responses aren't cached
if app.config["DEBUG"]:
    @app.after_request
    def after_request(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response

# custom filter
app.jinja_env.filters["usd"] = usd

# configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = True
app.config["SESSION_TYPE"] = "filesystem"

UPLOAD_FOLDER = '/home/ubuntu/workspace/tmp'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
UPLOADS_DEFAULT_DEST = '/home/ubuntu/workspace/tmp'


Session(app)


# configure CS50 Library to use SQLite database
db = SQL("sqlite:///finalProject.db")
flag = False

@app.route("/")
#@login_required
def index():
    items = {}

    point_lists = db.execute("SELECT addressId,name,number,points,mark_numbers,comment_numbers,address FROM fields order by points desc limit 5")
    for point_list in point_lists:
        point_list['message_numbers'] = point_list['mark_numbers'] + point_list['comment_numbers']
        point_list['url'] = request.url_root +'courts?addressId=' + str(point_list['addressId'])
    items['point_lists'] = point_lists

    comments_lists = db.execute("SELECT addressId,name,number,points,mark_numbers,comment_numbers,address FROM fields order by mark_numbers+comment_numbers desc limit 5")
    for comments_list in comments_lists:
        comments_list['message_numbers'] = comments_list['mark_numbers'] + comments_list['comment_numbers']
        comments_list['url'] = request.url_root +'courts?addressId=' + str(comments_list['addressId'])
    items['comments_lists'] = comments_lists

    createTime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    mark_lists = db.execute("SELECT fields.name,fields.addressId,messages.messageId,messages.message,messages.userName,messages.type,messages.playsNumber,messages.playTime FROM messages inner join fields on fields.addressId = messages.addressId WHERE messages.playTime > :createTime and messages.type = 1 ORDER BY messages.playTime limit 20 ", createTime = createTime)
    for mark_list in mark_lists:
        mark_list['url'] = request.url_root +'courts?addressId=' + str(mark_list['addressId'])
    items['mark_lists'] = mark_lists

    return render_template("index.html", items=items)


@app.route("/search", methods=["GET", "POST"])
def search():
    if request.method == "POST":
        address = request.form.get("address")
        if  not address:
            address = ""
        viewpoint = request.form.get("viewpoint")
        items = {}
        print(viewpoint)
        if __is__json(viewpoint):
            viewpoint_json = json.loads(viewpoint)
            slat = viewpoint_json['latitude']
            slong = viewpoint_json['longitude']
            name = viewpoint_json['name']
            #search distance <5km
            minlat, maxlat, minlng, maxlng = __get_area(slat, slong, dis=10)
            if not os.environ.get("API_KEY"):
                raise RuntimeError("API_KEY not set")
            items['key'] = os.environ.get("API_KEY")
            #rows = db.execute("SELECT addressId,address,number,points,modifyTime,latitude,longitude,mark_numbers,comment_numbers FROM fields  WHERE address like :address", address='%'+address+'%')
            rows = db.execute("SELECT addressId,name,number,points,modifyTime,latitude,longitude,mark_numbers,comment_numbers FROM fields  WHERE address like :address or ( :minlat < latitude and latitude < :maxlat and :minlng < longitude and longitude < :maxlng)", address='%'+name+'%', minlat=minlat,maxlat=maxlat,minlng=minlng,maxlng=maxlng)
        else:
            rows = db.execute("SELECT addressId,name,number,points,modifyTime,latitude,longitude,mark_numbers,comment_numbers FROM fields  WHERE address like :address", address='%'+address+'%')

        for row in rows:
            row['url'] =request.url_root +'courts?addressId=' + str(row['addressId'])
            row['time'] = row['modifyTime']
            row['name'] = row['name']
            row['message_numbers'] = row['comment_numbers'] + row['mark_numbers']
        items['rows'] = rows
        return render_template("search.html", items=items)
    else:
        return redirect(url_for("index"))#render_template("index.html")


@app.route("/courts", methods=["GET", "POST"])
def courts():
    items = {}
    if request.method == "GET":
        addressId = request.values.get("addressId")
        rows = db.execute("SELECT addressId,name,address,number,points,modifyTime,latitude,longitude,comment_numbers,mark_numbers FROM fields  WHERE addressId = :addressId", addressId = addressId)

        items['name'] = rows[0]['name']
        items['address'] = rows[0]['address']
        items['number'] = rows[0]['number']
        items['points'] = rows[0]['points']
        items['addressId'] = addressId
        items['longitude'] = rows[0]['longitude']
        items['latitude'] = rows[0]['latitude']
        items['message_numbers'] = rows[0]['comment_numbers'] + rows[0]['mark_numbers']

        rows = db.execute("SELECT messageId,addressId,userId,message,createTime,points,userName,pic,type,playsNumber,playTime FROM messages  WHERE addressId = :addressId ORDER BY createTime desc", addressId = addressId)
        messages = []
        for row in rows:
            messages.append(row)
        items['messages'] = messages

        if not os.environ.get("API_KEY"):
            raise RuntimeError("API_KEY not set")
        items['key'] = os.environ.get("API_KEY")

        return render_template("courts.html", item=items)
    else:
        return redirect(url_for("index"))#render_template("index.html")



@app.route("/premark", methods=["GET", "POST"])
@login_required
def premark():
    item = {}
    if request.method == "GET":
        addressId = request.values.get("addressId")
        rows = db.execute("SELECT addressId,name,address,number,points,modifyTime FROM fields  WHERE addressId = :addressId", addressId = addressId)
        if len(rows) != 0:
            item['name'] = rows[0]['name']
            item['address'] = rows[0]['address']
            item['addressId'] = addressId
            return render_template("mark.html", item=item)
        else:
            return redirect(url_for("index"))#render_template("index.html")
    else:
        return redirect(url_for("index"))#render_template("index.html")

@app.route("/mark", methods=["GET", "POST"])
@login_required
def mark():
    if request.method == "POST":
        addressId = request.form.get("addressId")
        type = request.form.get("myradio")
        points = request.form.get("points")
        playsNumber = request.form.get("playsNumber")
        playTime = request.form.get("playTime")
        message = request.form.get("message")

        userId = session["user_id"]
        userName = session["user_name"]
        if points == '':
            points = 0
        elif int(points) < 0 and int(points) >10:
            points = 0
        else:
            points = int(points)
        if playsNumber == '':
            playsNumber = 0
        elif int(playsNumber) < 0 and int(playsNumber) >50:
            playsNumber = 0
        else:
            playsNumber = int(playsNumber)

        if playTime and playTime != '':
            playTime = playTime.replace('T',' ',1)

        photo = request.files['photo']
        picUrl = "none"
        # if user does not select photo, browser also
        # submit a empty part without filename
        if photo.filename == '':
            print("No selected photo")
            #return redirect(url_for("preupload"))
        if photo and allowed_file(photo.filename):
            #filename = secure_filename(photo.filename)
            filename = str(int(time.time())) + '_'+str(userId)+'_' + secure_filename(photo.filename)
            app.config['UPLOAD_FOLDER'] = os.getcwd()+'/static/photos'
            photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            picUrl = request.url_root + 'static/photos/' + filename

        createTime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        rows = db.execute("INSERT INTO messages (\"addressId\", \"userId\", \"message\", \"createTime\", \"pic\", \"userName\", \"playsNumber\", \"playTime\", \"type\", \"points\") values (:addressId,:userId,:message,:createTime,:pic,:userName,:playsNumber,:playTime,:type,:points)", addressId=addressId,userId=userId,message=message,createTime=createTime,pic=picUrl,userName=userName,playsNumber=playsNumber,playTime=playTime,type=type,points=points)

        rows = db.execute("SELECT addressId,address,mark_numbers,comment_numbers,points FROM fields  WHERE addressId = :addressId", addressId = addressId)

        if int(type) == 0:
            comment_numbers = rows[0]["comment_numbers"] + 1
            points_fields = (rows[0]["points"] * rows[0]["comment_numbers"] + points) / comment_numbers
            points_fields = round(points_fields, 2)
            rows = db.execute("update fields set comment_numbers = :comment_numbers,points = :points_fields where addressId = :addressId",comment_numbers=comment_numbers,points_fields=points_fields,addressId=addressId)
        elif int(type) == 1:
            mark_numbers = rows[0]["mark_numbers"] + 1
            rows = db.execute("update fields set mark_numbers = :mark_numbers where addressId = :addressId",mark_numbers=mark_numbers,addressId=addressId)

        return redirect(url_for("courts", addressId = addressId))
    else:
        return redirect(url_for("index"))#render_template("index.html")


@app.route("/preupload", methods=["GET", "POST"])
@login_required
def preupload():
    return render_template("upload.html")



@app.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    if request.method == "POST":
        address = request.form.get("address")
        points = request.form.get("points")
        pictures = request.form.get("pictures")
        numbers = request.form.get("numbers")
        message = request.form.get("message")

        type = request.form.get("myradio")
        playsNumber = request.form.get("playsNumber")
        playTime = request.form.get("playTime")
        viewpoint = request.form.get("viewpoint")
        if __is__json(viewpoint):
            viewpoint_json = json.loads(viewpoint)
            slat = viewpoint_json['latitude']
            slong = viewpoint_json['longitude']
            name = viewpoint_json['name']
        else:
            slat = 0
            slong = 0
            name = "error"
            flash("have no location")
            return redirect(url_for("preupload"))

        minlat, maxlat, minlng, maxlng = __get_area(slat, slong, dis=0.05)
        rows = db.execute("SELECT addressId,name,number,points,modifyTime,latitude,longitude,mark_numbers,comment_numbers FROM fields  WHERE address like :address or ( :minlat < latitude and latitude < :maxlat and :minlng < longitude and longitude < :maxlng)", address='%'+name+'%', minlat=minlat,maxlat=maxlat,minlng=minlng,maxlng=maxlng)
        if len(rows) >= 1:
            flash("Has the same fields already.")
            return redirect(url_for("courts", addressId = rows[0]['addressId']))

        userId = session["user_id"]
        userName = session["user_name"]
        if points == '':
            points = 0
        elif int(points) < 0 and int(points) >10:
            points = 0
        else:
            points = int(points)
        if numbers == '':
            numbers = 0
        elif int(numbers) < 0 and int(numbers) >50:
            numbers = 0
        else:
            numbers = int(numbers)
        if type == '':
            type = 0
        if 'photo' not in request.files:
            print("No photo part")
            #return redirect(url_for("preupload"))
        photo = request.files['photo']
        picUrl = "none"
        # if user does not select photo, browser also
        # submit a empty part without filename
        if photo.filename == '':
            print("No selected photo")
            #return redirect(url_for("preupload"))
        if photo and allowed_file(photo.filename):
            #filename = secure_filename(photo.filename)
            filename = str(int(time.time())) + '_'+str(userId)+'_' + secure_filename(photo.filename)
            app.config['UPLOAD_FOLDER'] = os.getcwd()+'/static/photos'
            photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            picUrl = request.url_root + 'static/photos/' + filename
        createTime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        shape = 'whole test'
        comment_numbers = 1
        mark_numbers = 0
        addressId = db.execute("INSERT INTO fields (\"address\", \"number\", \"shape\", \"points\", \"latitude\", \"longitude\", \"userId\", \"comment_numbers\", \"createTime\", \"modifyTime\",\"name\",\"mark_numbers\") values (:address,:number,:shape,:points,:latitude,:longitude,:userId,:comment_numbers,:createTime,:modifyTime,:name,:mark_numbers)", address=address,number=numbers,points=points,shape=shape,latitude=slat,longitude=slong,userId=userId,comment_numbers=comment_numbers,createTime=createTime,modifyTime=createTime,name=name,mark_numbers=mark_numbers)
        messageId = db.execute("INSERT INTO messages (\"addressId\", \"userId\", \"message\", \"createTime\", \"pic\", \"userName\", \"playsNumber\", \"playTime\", \"type\", \"points\") values (:addressId,:userId,:message,:createTime,:pic,:userName,:playsNumber,:playTime,:type,:points)", addressId=addressId,userId=userId,message=message,createTime=createTime,pic=picUrl,userName=userName,playsNumber=playsNumber,playTime=playTime,type=type,points=points)
        return redirect(url_for("courts", addressId = addressId))
    else:
        return redirect(url_for("index")) #render_template("index.html")


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in."""
    # forget any user_id
    session.clear()
    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        next = url_for("index")
        # ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username")
        # ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password")
        if request.form.get("next"):
            next = request.form.get("next")

        # query database for username
        rows = db.execute("SELECT * FROM users WHERE userName = :userName", userName=request.form.get("username"))

        # ensure username exists and password is correct
        if len(rows) != 1 or not pwd_context.verify(request.form.get("password"), rows[0]["passwd"]):
            return apology("invalid username and/or password")
        # remember which user has logged in
        session["user_id"] = rows[0]["userId"]
        session["user_name"] = rows[0]["userName"]
        if next == "None":
            return redirect(url_for("mine"))
        # redirect user to home page
        return redirect(next)

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        next = request.values.get("next")
        return render_template("login.html",next = next)


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user."""
    # forget any user_id
    session.clear()
    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username")
        elif "\'" in request.form.get("username") or ";" in request.form.get("username"):
            return apology("username can't contain ' or ;")
        # ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password")

        elif not request.form.get("password_1"):
            return apology("must provide password(again)")
        if not request.form.get("nickname"):
            nickname = request.form.get("username")
        elif "\'" in request.form.get("nickname") or ";" in request.form.get("nickname"):
            return apology("nickname can't contain ' or ;")
        else:
            nickname = request.form.get("nickname")
        if request.form.get("password") != request.form.get("password_1"):
            return apology("password(again) must equit password")

        myctx = CryptContext(["sha256_crypt"])
        passwd = myctx.hash(request.form.get("password"))

        createTime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # query database for username
        userId = db.execute("INSERT INTO users (\"userName\",\"passwd\",\"nickName\", \"createTime\", \"loginTime\") VALUES (:userName, :passwd, :nickName, :createTime, :loginTime)",userName=request.form.get("username"), passwd=passwd, nickName=nickname, createTime = createTime, loginTime = createTime)
        # ensure username exists and password is correct
        if userId == 0:
            return apology("invalid username and/or password")

        # remember which user has logged in
        session["user_id"] = userId
        session["user_name"] = request.form.get("username")


        # redirect user to home page
        return redirect(url_for("mine"))

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


@app.route("/mine", methods=["GET", "POST"])
@login_required
def mine():
    user_id=session["user_id"]
    item = {}
    rows = db.execute("SELECT * FROM users WHERE userId = :id", id=user_id)
    item['name'] = rows[0]['userName']
    item['nickName'] = rows[0]['nickName']
    item['createTime'] = rows[0]['createTime']
    item['loginTime'] = rows[0]['loginTime']

    rows = db.execute("SELECT fields.name,fields.addressId,messages.messageId,messages.message,messages.createTime,messages.points,messages.type,messages.playsNumber,messages.playTime,messages.pic FROM messages inner join fields on fields.addressId = messages.addressId WHERE messages.userId = :userId ORDER BY messages.createTime desc", userId = user_id)
    item['message_numbers'] = len(rows)
    messages = []
    for row in rows:
        row['url'] =request.url_root +'courts?addressId=' + str(row['addressId'])
        messages.append(row)
    item['messages'] = messages
    return render_template("mine.html",item = item)

@app.route("/change", methods=["GET", "POST"])
@login_required
def change():
    user_id=session["user_id"]
    if request.method == "POST":
        # ensure username was submitted

        # ensure password was submitted
        if not request.form.get("password"):
            return apology("must provide password")

        elif not request.form.get("password_1"):
            return apology("must provide password(again)")

        if request.form.get("password") != request.form.get("password_1"):
            return apology("password(again) must equit password")

        myctx = CryptContext(["sha256_crypt"])
        passwd = myctx.hash(request.form.get("password"))

        loginTime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        rows = db.execute("update users set passwd = :passwd,loginTime = :loginTime where userId = :user_id",passwd=passwd,loginTime=loginTime,user_id=user_id)
        if rows != 1:
            return apology("change passwd is failed!")
        return redirect(url_for("mine"))


@app.route("/logout")
def logout():
    """Log user out."""

    # forget any user_id
    session.clear()

    # redirect user to login form
    return redirect(url_for("login"))

@app.route("/help")
def help():
    """How it works."""

    # redirect user to login form
    return render_template("help.html")


def __get_area(latitude, longitude, dis):
    r = 6371.137
    dlng = 2 * math.asin(math.sin(dis / (2 * r)) / math.cos(latitude * math.pi / 180))
    dlng = dlng * 180 / math.pi

    dlat = dis / r
    dlat = dlat * 180 / math.pi

    minlat = latitude - dlat
    maxlat = latitude + dlat
    minlng = longitude - dlng
    maxlng = longitude + dlng
    return minlat, maxlat, minlng, maxlng


def __is__json(str):
    try:
        json.loads(str)
        return True
    except:
        return False