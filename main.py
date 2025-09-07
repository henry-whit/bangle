from flask import Flask,render_template,session,redirect,request
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import os
import json
app = Flask(__name__)
app.secret_key = 'fjjUs8*jd8{@]d'
cred = credentials.Certificate(json.loads(os.environ.get('ps')))
#cred = credentials.Certificate("C:\\Users\\hdoub\\Downloads\\private-server-ab543-firebase-adminsdk-fbsvc-8f5a4e61e3.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

def checkfm(email):
    pass
#main page 
@app.route('/')
def main():
    if not session.get("username"):
        return render_template('index.html',logged="false")
    return render_template('index.html',logged="true",user=session.get("username"))

#home page 
@app.route('/home')
def home():
    if not session.get('username'):
        return redirect('/login')
    lb = db.collection('Users').document(session.get('email')).collection('Projects').get()
    bangles = []
    for item in lb:
        bangles.append(item.id)
    while len(bangles) >3:
        bangles.remove(bangles[len(bangles)-1])
    return render_template('home.html',user=session.get("username"),bangles=bangles)

#sign up 
@app.route('/signup',methods = ['GET','POST'])
def signup():
    if request.method == 'GET':
        return render_template('signup.html')
    email= request.form.get('email').lower()
    user = db.collection('Users').document(email)
    if user.get().to_dict():
        return {"message":"Email in use"}
    tag = ''
    for l in email:
        if l == '@':
            continue
        tag = tag + l
    user.set({"name":request.form.get('dsp'),"password":request.form.get('password'),"tag":tag})
    return redirect('/login')

#log out
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

#sign in 
@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'GET':
        if session.get('username'):
            return redirect('/home')
        return render_template('login.html')
    user = db.collection('Users').document(request.form.get('email').lower()).get().to_dict()
    if not user:
        return redirect('/login')
    if user['password'] == request.form.get('password'):
        session["username"] = user["name"]
        session["email"] = request.form.get('email')
        return redirect('/home')
    return redirect('/login')

#edit a bangle 
@app.route('/edit/<bg>')
def edit(bg):
    if not session.get('username'):
        return redirect('/login')
    user = db.collection('Users').document(session.get("email")).collection('Projects').document(bg).get().to_dict()
    if user:
        session['project'] = bg
        return render_template('editor.html',user=session.get("username"),code=user["code"],title=bg,url=f"https://bangle-app-fxgs.onrender.com/sites/{session.get('username')}/{bg}")
    return 'Error: no such site'

#get a public site 
@app.route('/sites/<user>/<st>')
def site(user,st):
    site = db.collection('Users').document(user).collection('Projects').document(st).get().to_dict()
    if not site:
        return 'Sorry, we can\'t find that site on our database.'
    return site['code']

#add a site to the database 
@app.route('/addsite',methods=['POST'])
def add():
    if not session.get('username'):
        return redirect('/login')
    if not session.get('project'):
        return {"message":"sync error. try copying your code and refreshing the page."}
    project = db.collection('Users').document(session.get('email')).collection('Projects').document(session.get('project'))
    if not project.get().to_dict():
        return {"message":"sync error: copy your code and reload the page."}
    project.set({"code":request.get_json().get('code')},merge=True)
    return {"message":"saved!"}

@app.route('/makesite',methods=['POST'])
def make():
    if not session.get('username'):
        return redirect('/login')
    name = request.form.get('bn').lower()
    proj = db.collection('Users').document(session.get('email')).collection('Projects').document(name)
    if proj.get().to_dict():
        return redirect('/library')
    proj.set({"code":"","description":request.form.get('desc')})
    return redirect(f"/edit/{name}")

@app.route('/library')
def library():
    if not session.get('username'):
        return redirect('/login')
    lb = db.collection('Users').document(session.get('email')).collection('Projects').get()
    bangles = []
    for item in lb:
        bangles.append(item.id)
    return render_template('library.html',bangles=bangles,user=session.get('username'))

@app.route('/delete')
def delete():
    if not session.get('username'):
        return redirect('/login')
    if not session.get('project'):
        return {"message":"failed to sync: reload this page and try again"}
    proj = db.collection('Users').document(session.get('email')).collection('Projects').document(session.get('project'))
    proj.delete()
    return redirect('/library')

@app.route('/account')
def rd():
    return redirect('/account/password')

@app.route('/account/<tp>')
def account(tp):
    t = tp
    if not session.get('username'):
        return redirect('/login')
    return render_template('account.html',details=t,user=session.get('username'))

@app.route('/changepw',methods=['POST'])
def changepw():
    if not session.get('username'):
        return redirect('/login')
    user = db.collection('Users').document(session.get('email'))
    print(user.get().to_dict())
    if user.get().to_dict()["password"] == request.form.get('curr'):
        user.set({'password':request.form.get('np')},merge=True)
    return redirect('/account/password')

@app.route('/changeds',methods=['POST'])
def changeds():
    if not session.get('username'):
        return redirect('/login')
    user = db.collection('Users').document(session.get('email'))
    user.set({"name":request.form.get('ds')},merge=True)
    return redirect('/account/username')

@app.route('/delacc',methods=['POST'])
def delacc():
    if not session.get('username'):
        return redirect('/login')
    user = db.collection('Users').document(session.get('email'))
    if user.collection('Projects').get().to_dict():
        for proj in user.collection('Projects').get():
            proj.get().delete()
    user.get('password').delete()
    user.get('name').delete()
    user.delete()
    session.clear()
    return redirect('/')
 
@app.route('/users/<user>')
def get_user(user):
    usr = db.collection('Users').document(user)
    if not usr.get().to_dict():
        return 'Error: user not found'
    us = usr.get().to_dict()
    return render_template('user.html',username=us["name"],user = session.get('user'),email=usr.id)

@app.route('/search')
def search():
    user = request.args.get('query')
    users = db.collection('Users').get()
    print(users)
    queries = []
    for u in users:
        usr = u.to_dict()
        if u.id.startswith(user) or usr["name"].startswith(user):
            queries.append({"name":usr["name"],"email":u.id})
        print(queries)
    return queries

if __name__ == '__main__':
    app.run()