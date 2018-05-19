# On-Basketball-Courts
a web demo about collecting informations of basketball courts, the website is builded by flask.
<br>

I'm not familiar with website development, and know little about css/js, so I just want to build a website demo using flask.
And that's also my final project in cs50 course.
<br>
## About:
I’m a huge basketball fan who found it's difficult to get an appropriate place to play basketball, so I build a website, we can use it to collect the information of basketball courts and basketball fans. Therefore, the name of the website is "On Basketball Courts”. At this website, you can upload and search the information of basketball courts, and comment these courts and communicate with others.


## Pages:
### 1.Index
You can search and upload the information of basketball courts. Of course, you can also see three table controls. They are recent 20 reserved informations, top 5 points of basketball courts, and top 5 popular of basketball courts, respectively. You can click any name of basketball courts, then the details will come out.
### 2.Search
It shows all the courts within 10km of your input place. Or you can just click the search botton. It will show all of the courts to you. If you can not find the basketball court which you want, you can upload it by yourself.
### 3.Court
You can get the location from google map, and mark something on it. Actually, I think this part is the most significant of the website. You can comment the court, give points, upload the pic, or you can send the messages about your plan, such as time and place and how many guys will play basketball with you. You can invite others to join you. Everybody can read the message which you sent on the website. Of course, if you want to mark something, please login the website. If you don’t have an account yet, register it right now. There are some test accounts(username/password), such as test/test, Kobe Bryant/Kobe Bryant, Stephen Curry/Stephen Curry, Klay Thompson/Klay Thompson.
### 4.Mine
You can check all of your messages you sent on “mine” page. By the way, you can also change your password easily.
### 5.Upload/Mark

## Build:
### Dependence
1.Flask you can find the way to install flask in http://flask.pocoo.org/docs/0.12/installation/
<br>
2.Python3.x (My Python version is 3.6.0)
<br>
3.pip https://pip.pypa.io/en/stable/installing/
4.GoogleMap API_KEY  <br>
Because some pages need to use google map, so you had better have a google map API_KEY.
<br>
https://developers.google.com/maps/documentation/javascript/get-api-key?hl=zh-cn

### Commands
export API_KEY="your googlemap API_KEY" <br>
pip install --user -r requirements.txt  <br>
flask run <br>

## Extra:
### commonds of create tables in sqlite3  
CREATE TABLE 'users' ('userId' INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,'userName' TEXT NOT NULL,'nickName' TEXT NOT NULL,'passwd' TEXT NOT NULL, 'createTime' DATETIME NOT NULL,'loginTime' DATETIME NOT NULL,'extra1' TEXT DEFAULT NULL,'extra2' TEXT DEFAULT NULL,'extra3' TEXT DEFAULT NULL)
<br>
CREATE TABLE 'fields' ('addressId' INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,'name' TEXT NOT NULL,'number' INTEGER NOT NULL,'shape' INTEGER NOT NULL,'points' NUMERIC NOT NULL, 'latitude' NUMERIC NOT NULL, 'longitude' NUMERIC NOT NULL,'userId' INTEGER NOT NULL,'mark_numbers' INTEGER NOT NULL, 'createTime' DATETIME NOT NULL,'modifyTime' DATETIME NOT NULL,'comment_numbers' INTEGER DEFAULT NULL,'address' TEXT DEFAULT NULL,'extra3' TEXT DEFAULT NULL)
<br>
CREATE TABLE 'messages' ('messageId' integer primary key autoincrement not null, 'addressId' integer not null, 'userId' integer not null, 'message' text not null, 'createTime' datetime not null, 'pic' text default null,'userName' text default null,'extra2' text default null, 'playsNumber' INTEGER DEFAULT NULL, 'playTime' DATETIME DEFAULT NULL, 'type' INTEGER DEFAULT 1, 'points' INTEGER DEFAULT NULL, 'extra1' TEXT DEFAULT NULL)
<br>

### some website framework
#### bootstrap
https://getbootstrap.com/docs/4.0/getting-started/introduction/
