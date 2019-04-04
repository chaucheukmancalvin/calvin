from flask import Flask, render_template, url_for, redirect, request, session
import os
from sqlalchemy.orm import sessionmaker
from tabledef import *
from werkzeug import secure_filename
from datetime import datetime, date
import re
from flask_mail import Mail, Message

#########################
# Get and echo database #
#########################

engine = create_engine('sqlite:///205.db', echo=True)

########################
# upload image setting #
########################

UPLOAD_FOLDER = os.getcwd() + '/static' + '/uploadimg'
ALLOWED_EXTENSTIONS = set(['png', 'jpg', 'jpeg'])

###############
# app setting #
###############

app = Flask(__name__)
mail = Mail(app)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = '205project2019@gmail.com'
app.config['MAIL_PASSWORD'] = '205project'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail=Mail(app)

#############################
# upload image type allowed #
#############################

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSTIONS
#########
# index #
#########

@app.route('/')
def index():
    if not session.get('logged_in'):
        return render_template('loginhomepage.html')        
    else:
        return render_template('loginhomepage.html', name=session['username'])

#########################################################
# other render_template return without a lot of setting #
#########################################################

@app.route('/component')
def component():
    return render_template('logincomponent.html')
@app.route('/product')
def product():
    return render_template('loginproduct.html')
@app.route('/secondhand')
def secondhand():
    return render_template('loginsecondhand.html')
@app.route('/aboutus')
def aboutus():
    return render_template('loginaboutus.html')
@app.route('/advertisement')
def advertisement():
    return render_template('loginadvertisement.html')
@app.route('/contactus')
def contactus():
    return render_template('logincontactus.html')
@app.route('/admin')
def admin():
    return render_template('admin.html')

##################
# Login finction #
##################

@app.route('/login', methods=['POST'])
def do_login():
 
    POST_USERNAME = str(request.form['username'])
    POST_PASSWORD = str(request.form['password'])
 
    Session = sessionmaker(bind=engine)
    s = Session()
    query = s.query(User).filter(User.username.in_([POST_USERNAME]), User.password.in_([POST_PASSWORD]))
    result = query.first()
    query1 = s.query(Admin).filter(Admin.username.in_([POST_USERNAME]), Admin.password.in_([POST_PASSWORD]))
    result1 = query1.first()

    if result:
        session['logged_in'] = True
        session['error'] = False
        session['username'] = POST_USERNAME  
        return index()
    elif result1:
        session['logged_in'] =True
        session['error'] = False
        return admin()
    else: 
        session['error'] = True
        return redirect(url_for('loginerror'))

###################
# error for login #
###################

@app.route('/loginerror')
def loginerror():
    return index()

###################
# logout function #
###################

@app.route('/logout')
def logout():
    session['logged_in'] = False
    session.pop('username', None)
    session.pop('id', None)
    session['error'] = False
    return redirect(url_for('index'))


#####################
# register function #
#####################


@app.route('/register',methods=['POST'])
def do_register():
    session['error'] = False
    POST_USERNAME = str(request.form['username'])
    POST_PASSWORD = str(request.form['password'])
    POST_EMAIL = str(request.form['email'])
    try:
        POST_CREDITCARD = int(request.form['creditcardNo'])
    except Exception:
        session['error'] = True
        return redirect(url_for('registererror1'))
    
    if len(str(POST_CREDITCARD)) == 16:
        if re.match("[^@]+@[^@]+\.[^@]+", POST_EMAIL):
            Session = sessionmaker(bind=engine)
            s = Session()
            query = s.query(User).filter(User.username.in_([POST_USERNAME]))
            query1 = s.query(User).filter(User.creditcardNo.in_([POST_CREDITCARD]))
            query2 = s.query(Admin).filter(Admin.username.in_([POST_USERNAME]))
            query3 = s.query(User).filter(User.email.in_([POST_EMAIL]))
            result = query.first()
            result1 = query1.first()
            result2 = query2.first()
            result3 = query3.first()
            if result:
                session['error'] = True                                                                                    
                return redirect(url_for('registererror'))
            elif result1:
                session['error'] =True
                return redirect(url_for('registererror1'))
            elif POST_PASSWORD == "" or POST_USERNAME == "":
                session['error'] = True
                return redirect(url_for('registererror2'))
            elif result2:
                session['error'] = True
                return redirect(url_for('registererror'))
            elif result3:
                session['error'] = True
                return redirect(url_for('registererror3'))
            else:
                session['error'] = False
                user = User(username=POST_USERNAME, password=POST_PASSWORD, email=POST_EMAIL, creditcardNo=POST_CREDITCARD)
                s.add(user)
                s.commit()
                return index()
        else:
            session['error'] = True
            return redirect(url_for('registererror3'))
    else:
        session['error'] = True
        return redirect(url_for('registererror1'))

#######################
# errors for register #
#######################

@app.route('/registererror')
def registererror():
    session['error'] = True
    return index()

@app.route('/registererror1')
def registererror1():
    session['error'] = True
    return index()

@app.route('/registererror2')
def registererror2():
    session['error'] = True
    return index()

@app.route('/registererror3')
def registererror3():
    session['error'] = True
    return index()

############################
# change username function #
############################

@app.route('/changeusername',methods=['POST'])
def changeusername():
    session['error'] = False
    POST_USERNAME = str(request.form['username'])
    name = session['username']
    Session = sessionmaker(bind=engine)
    s = Session()
    query = s.query(User).filter(User.username.in_([POST_USERNAME]))
    result = query.first()
    query1 = s.query(Admin).filter(Admin.username.in_([POST_USERNAME]))
    result1 = query1.first()
    if result:
        session['error'] = True                                                                                    
        return redirect(url_for('changeusernameerror')) 
    elif POST_USERNAME == "":
        session['error'] = True
        return redirect(url_for('changeusernameerror1'))
    elif result1:
        session['error'] = True
        return redirect(url_for('changeusernameerror'))
    else:
        session['error'] = False    
        try:
            query2 = s.query(Sell).filter(Sell.username.in_([name])).all()
            for i in query2:
                s.query(Sell).filter(Sell.username.in_([i.username])).first().username = POST_USERNAME
                s.commit()
        except Exception:
            pass
        try:
            query3 = s.query(Product).filter(Product.username.in_([name])).all()
            for i in query3:
                s.query(Product).filter(Product.username.in_([i.username])).first().username = POST_USERNAME
                s.commit()
        except Exception:
            pass
        try:
            query4 = s.query(Component).filter(Component.username.in_([name])).all()
            for i in query4:
                s.query(Component).filter(Component.username.in_([i.username])).first().username = POST_USERNAME
                s.commit()
        except Exception:
            pass
        s.query(User).filter(User.username.in_([name])).first().username = POST_USERNAME
        s.commit()
        session.pop('username',None)
        session['username'] = POST_USERNAME
        return index()

#######################################
# errors for change username function #
#######################################

@app.route('/changeusernameerror')
def changeusernameerror():
    return index()

@app.route('/changeusernameerror1')
def changeusernameerror1():
    return index()

############################
# change password function #
############################

@app.route('/changepassword',methods=['POST'])
def changepassword():
    session['error'] = False
    POST_PASSWORD = str(request.form['password'])
    POST_PASSWORDOLD = str(request.form['passwordold'])
    name = session['username']
    Session = sessionmaker(bind=engine)
    s = Session()
    query = s.query(User).filter(User.password.in_([POST_PASSWORDOLD]),User.username.in_([session['username']))
    result = query.first()
    if POST_PASSWORD == "" or POST_PASSWORDOLD == "":
        session['error'] = True                                                                 
        return redirect(url_for('changepassworderror'))
    elif result:
        session['error'] = False  
        s.query(User).filter(User.username.in_([name])).first().password = POST_PASSWORD
        s.commit()                                                                          
        return index()
    else:
        session['error'] = True                                                                 
        return redirect(url_for('changepassworderror1'))

##############################
# errors for change password #
##############################

@app.route('/changepassworderror')
def changepassworderror():
    return index()

@app.route('/changepassworderror1')
def changepassworderror1():
    return index()
        
#############################################        
# upload sell secondhand request with image #
#############################################  

@app.route('/upload1', methods=['POST'])
def upload_file1():
    session['error'] = False
    POST_DETAIL = str(request.form['detail'])
    try:
        file = request.files['file']
    except Exception:
        session['error'] = True
        return redirect(url_for('secondhanderror1'))

    try:
        POST_PRICE = int(request.form['price'])
    except Exception:
        session['error'] = True
        return redirect(url_for('secondhanderror2'))

    Session = sessionmaker(bind=engine)
    s = Session()
    
    if POST_DETAIL == "" or POST_PRICE == "":
        session['error'] = True
        return redirect(url_for('secondhanderror3'))
    elif 'file' not in request.files:
        session['error'] = True
        return redirect(url_for('secondhanderror1'))
    elif file and allowed_file(file.filename):
        session['error'] = False
        sell = Sell(detail=POST_DETAIL, price=POST_PRICE, username=session['username'], modle="A", state="admin not confirm")
        s.add(sell)
        s.commit()
        session['id'] = s.query(Sell).order_by(Sell.id.desc()).first().id
        filename = str(session['id']) + '.' + secure_filename(file.filename).split('.')[-1]
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))     
        return secondhand()
    else: 
        session['error'] =True
        return redirect(url_for('secondhanderror1'))

@app.route('/upload2', methods=['POST'])
def upload_file2():
    session['error'] = False
    POST_DETAIL = str(request.form['detail'])

    try:
        file = request.files['file']
    except Exception:
        session['error'] = True
        return redirect(url_for('secondhanderror1'))

    try:
        POST_PRICE = int(request.form['price'])
    except Exception:
        session['error'] = True
        return redirect(url_for('secondhanderror2'))

    Session = sessionmaker(bind=engine)
    s = Session()
    if POST_DETAIL == "" or POST_PRICE == "":
        session['error'] = True
        return redirect(url_for('secondhanderror3'))
    elif 'file' not in request.files:
        session['error'] = True
        return redirect(url_for('secondhanderror1'))
    elif file and allowed_file(file.filename):
        session['error'] = False
        sell = Sell(detail=POST_DETAIL, price=POST_PRICE, username=session['username'], modle="B", state="admin not confirm")
        s.add(sell)
        s.commit()
        session['id'] = s.query(Sell).order_by(Sell.id.desc()).first().id
        filename = str(session['id']) + '.' + secure_filename(file.filename).split('.')[-1]
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return secondhand()
    else:
        session['error'] =True
        return redirect(url_for('secondhanderror1'))

@app.route('/upload3', methods=['POST'])
def upload_file3():
    session['error'] = False
    POST_DETAIL = str(request.form['detail'])

    try:
        file = request.files['file']
    except Exception:
        session['error'] = True
        return redirect(url_for('secondhanderror1'))

    try:
        POST_PRICE = int(request.form['price'])
    except Exception:
        session['error'] = True
        return redirect(url_for('secondhanderror2'))

    Session = sessionmaker(bind=engine)
    s = Session()
    if POST_DETAIL == "" or POST_PRICE == "":
        session['error'] = True
        return redirect(url_for('secondhanderror3'))
    elif 'file' not in request.files:
        session['error'] = True
        return redirect(url_for('secondhanderror1'))
    elif file and allowed_file(file.filename):
        session['error'] = False
        sell = Sell(detail=POST_DETAIL, price=POST_PRICE, username=session['username'], modle="C", state="admin not confirm")
        s.add(sell)
        s.commit()
        session['id'] = s.query(Sell).order_by(Sell.id.desc()).first().id
        filename = str(session['id']) + '.' + secure_filename(file.filename).split('.')[-1]
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return secondhand()
    else:
        session['error'] =True
        return redirect(url_for('secondhanderror1'))

@app.route('/upload4', methods=['POST'])
def upload_file4():
    session['error'] = False
    POST_DETAIL = str(request.form['detail'])

    try:
        file = request.files['file']
    except Exception:
        session['error'] = True
        return redirect(url_for('secondhanderror1'))

    try:
        POST_PRICE = int(request.form['price'])
    except Exception:
        session['error'] = True
        return redirect(url_for('secondhanderror2'))

    Session = sessionmaker(bind=engine)
    s = Session()
    if POST_DETAIL == "" or POST_PRICE == "":
        session['error'] = True
        return redirect(url_for('secondhanderror3'))
    elif 'file' not in request.files:
        session['error'] = True
        return redirect(url_for('secondhanderror1'))
    elif file and allowed_file(file.filename):
        session['error'] = False
        sell = Sell(detail=POST_DETAIL, price=POST_PRICE, username=session['username'], modle="D", state="admin not confirm")
        s.add(sell)
        s.commit()
        session['id'] = s.query(Sell).order_by(Sell.id.desc()).first().id
        filename = str(session['id']) + '.' + secure_filename(file.filename).split('.')[-1]
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return secondhand()
    else:
        session['error'] =True
        return redirect(url_for('secondhanderror1'))

@app.route('/upload5', methods=['POST'])
def upload_file5():
    session['error'] = False
    POST_DETAIL = str(request.form['detail'])

    try:
        file = request.files['file']
    except Exception:
        session['error'] = True
        return redirect(url_for('secondhanderror1'))

    try:
        POST_PRICE = int(request.form['price'])
    except Exception:
        session['error'] = True
        return redirect(url_for('secondhanderror2'))

    Session = sessionmaker(bind=engine)
    s = Session()
    if POST_DETAIL == "" or POST_PRICE == "":
        session['error'] = True
        return redirect(url_for('secondhanderror3'))
    elif 'file' not in request.files:
        session['error'] = True
        return redirect(url_for('secondhanderror1'))
    elif file and allowed_file(file.filename):
        session['error'] = False
        sell = Sell(detail=POST_DETAIL, price=POST_PRICE, username=session['username'], modle="E", state="admin not confirm")
        s.add(sell)
        s.commit()
        session['id'] = s.query(Sell).order_by(Sell.id.desc()).first().id
        filename = str(session['id']) + '.' + secure_filename(file.filename).split('.')[-1]
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return secondhand()
    else:
        session['error'] =True
        return redirect(url_for('secondhanderror1'))

@app.route('/upload6', methods=['POST'])
def upload_file6():
    session['error'] = False
    POST_DETAIL = str(request.form['detail'])
    
    try:
        file = request.files['file']
    except Exception:
        session['error'] = True
        return redirect(url_for('secondhanderror1'))

    try:
        POST_PRICE = int(request.form['price'])
    except Exception:
        session['error'] = True
        return redirect(url_for('secondhanderror2'))

    Session = sessionmaker(bind=engine)
    s = Session()
    if POST_DETAIL == "" or POST_PRICE == "":
        session['error'] = True
        return redirect(url_for('secondhanderror3'))
    elif 'file' not in request.files:
        session['error'] = True
        return redirect(url_for('secondhanderror1'))
    elif file and allowed_file(file.filename):
        session['error'] = False
        sell = Sell(detail=POST_DETAIL, price=POST_PRICE, username=session['username'], modle="F", state="admin not confirm")
        s.add(sell)
        s.commit()
        session['id'] = s.query(Sell).order_by(Sell.id.desc()).first().id
        filename = str(session['id']) + '.' + secure_filename(file.filename).split('.')[-1]
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return secondhand()
    else:
        session['error'] =True
        return redirect(url_for('secondhanderror1'))

#############################################
# errors for upload sell secondhand request #
#############################################

@app.route('/secondhanderror1')
def secondhanderror1():
    return secondhand()

@app.route('/secondhanderror2')
def secondhanderror2():
    return secondhand()

@app.route('/secondhanderror3')
def secondhanderror3():
    return secondhand()


###################################################################
# a page show information of the sell secondhand request for user #
###################################################################

@app.route('/sellinfo')
def sellinfo():
    Session = sessionmaker(bind=engine)
    s = Session()
    POST_USERNAME = session['username']
    List=[]
    query = s.query(Sell).filter(Sell.username.in_([POST_USERNAME])).all()
    for i in query:
        a=0
        try:
            f = open('static/uploadimg/' + str(i.id)  + '.' + 'png')
            f.close()
            a=1   
        except Exception:
            try:
                f = open('static/uploadimg/' + str(i.id)  + '.' + 'jpg')
                f.close()
                a=2
            except Exception:
                try:
                    f = open( 'static/uploadimg/' + str(i.id)  + '.' + 'jepg')
                    f.close()
                    a=3
                except Exception:
                    break
        if a == 1:
            List.append('png')
            
        elif a == 2:
            List.append('jpg')
        elif a == 3:
            List.append('jepg')
        else:
            print('error')
    print (List)
    return render_template('sellinfo.html', query=query ,List=List)

####################################################################
# a page show information of the sell secondhand request for admin #
####################################################################

@app.route('/adminsellinfo')
def adminsellinfo():
    Session = sessionmaker(bind=engine)
    s = Session()
    List = []
    query = s.query(Sell).all()
    for i in query:
        a=0
        try:
            f = open('static/uploadimg/' + str(i.id)  + '.' + 'png')
            f.close()
            a=1   
        except Exception:
            try:
                f = open('static/uploadimg/' + str(i.id)  + '.' + 'jpg')
                f.close()
                a=2
            except Exception:
                try:
                    f = open('static/uploadimg/' + str(i.id)  + '.' + 'jepg')
                    f.close()
                    a=3
                except Exception:
                    break
        if a == 1:
            List.append('png')
        elif a == 2:
            List.append('jpg')
        elif a == 3:
            List.append('jepg')
        else:
            pass
    print (List)
    return render_template('adminsellinfo.html', query=query ,List=List)
    
#################################################################
# a function for admin to request a purchase for the secondhand #
#################################################################

@app.route('/statechange', methods=['POST'])
def statechange():
    Session = sessionmaker(bind=engine)
    s = Session()
    query1 = s.query(Sell).all()
    for i in query1:
        b = 0
        try:
            POST_ID = request.form[str(i.id)]
            b = 1
        except Exception:
            b = 0
        print (b)
        if b == 1:
            s.query(Sell).filter(Sell.id.in_([i.id])).first().state = str('confirm')
            s.commit()
            break 
        elif b == 0 or b ==" ":
            pass
    return adminsellinfo()

##############################
# confirm to sell the device #
##############################

@app.route('/confirmsell', methods=['POST'])
def confirmsell():
    Session = sessionmaker(bind=engine)
    s = Session()
    POST_USERNAME = session['username']
    query1 = s.query(Sell).filter(Sell.username.in_([POST_USERNAME])).all()
    for i in query1:
        b = 0
        try:
            POST_ID = request.form['confirm'+str(i.id)]
            b = 1
        except Exception:
            b = 0
        print (b)
        if b == 1:
            try:
                POST_DATETIME = datetime.strptime(request.form['date'+str(i.id)],'%Y-%m-%d')
                POST_DATE = POST_DATETIME.date()
                if POST_DATE > datetime.strptime(str(date.today()),'%Y-%m-%d').date(): 
                    s.query(Sell).filter(Sell.id.in_([i.id])).first().date = POST_DATE
                    s.query(Sell).filter(Sell.id.in_([i.id])).first().state = str('Done')
                    s.commit()
                else:
                    return redirect(url_for('dateerror'))    
            except Exception:
                return redirect(url_for('dateerror'))
                  
        elif b == 0 or b ==" ":
            pass
    return sellinfo()
#############################
# error for confirm to sell #
#############################

@app.route('/dateerror')
def dateerror():
    return sellinfo()

############################################
# cancle the request of selling secondhand #
############################################

@app.route('/canclesell')
def canclesell():
    Session = sessionmaker(bind=engine)
    
    s = Session()
    POST_USERNAME = session['username']
    query1 = s.query(Sell).filter(Sell.username.in_([POST_USERNAME])).all()
    
    for i in query1:
        b = 0
        try:
            POST_ID = request.form['cancle'+str(i.id)]
            b = 1
        except Exception:
            b = 0
        print (b)
        if b == 1:
            s.query(Sell).filter(Sell.id.in_([i.id])).first().state = str('Cancle')
            s.commit()
            break    
        elif b == 0 or b ==" ":
            pass
    return sellinfo()

###################################################################
# sort for the latest record of request sell secondhand for admin #
###################################################################


@app.route('/sortadmin')
def sortadmin():
    Session = sessionmaker(bind=engine)
    s = Session()
    List = []
    query = s.query(Sell).order_by(Sell.id.desc()).all()
    for i in query:
        a=0
        try:
            f = open('static/uploadimg/' + str(i.id)  + '.' + 'png')
            f.close()
            a=1   
        except Exception:
            try:
                f = open('static/uploadimg/' + str(i.id)  + '.' + 'jpg')
                f.close()
                a=2
            except Exception:
                try:
                    f = open('static/uploadimg/' + str(i.id)  + '.' + 'jepg')
                    f.close()
                    a=3
                except Exception:
                    break
        if a == 1:
            List.append('png')
        elif a == 2:
            List.append('jpg')
        elif a == 3:
            List.append('jepg')
        else:
            pass
    print (List)
    return render_template('adminsellinfo.html', query=query ,List=List)

##################################################################
# sort for the latest record of request sell secondhand for user #
##################################################################

@app.route('/sort')
def sort():
    Session = sessionmaker(bind=engine)
    s = Session()
    List= []
    POST_USERNAME = session['username']
    query = s.query(Sell).filter(Sell.username.in_([POST_USERNAME])).order_by(Sell.id.desc()).all()
    for i in query:
        a=0
        try:
            f = open('static/uploadimg/' + str(i.id)  + '.' + 'png')
            f.close()
            a=1   
        except Exception:
            try:
                f = open('static/uploadimg/' + str(i.id)  + '.' + 'jpg')
                f.close()
                a=2
            except Exception:
                try:
                    f = open('static/uploadimg/' + str(i.id)  + '.' + 'jepg')
                    f.close()
                    a=3
                except Exception:
                    break
        if a == 1:
            List.append('png')
        elif a == 2:
            List.append('jpg')
        elif a == 3:
            List.append('jepg')
        else:
            pass
    print (List)
    return render_template('sellinfo.html', query=query ,List=List)

#################################
# purchase for official product #
#################################


@app.route('/purchase1', methods=['POST'])
def purchase1():
    try:
        POST_PURCHASE = int(request.form['productNo1'])
    except Exception:
        return redirect(url_for('producterror'))
    Session = sessionmaker(bind=engine)
    s = Session()
    products = Product(username = session['username'], purchaseno = POST_PURCHASE, modle = 'A')
    s.add(products)
    s.commit()
    return product()

@app.route('/purchase2', methods=['POST'])
def purchase2():
    try:
        POST_PURCHASE = int(request.form['productNo2'])  
    except Exception:
        return redirect(url_for('producterror'))
    Session = sessionmaker(bind=engine)
    s = Session()
    products = Product(username = session['username'], purchaseno = POST_PURCHASE, modle = 'B')
    s.add(products)
    s.commit()
    return product()

@app.route('/purchase3', methods=['POST'])
def purchase3():
    try:
        POST_PURCHASE = int(request.form['productNo3'])   
    except Exception:
        return redirect(url_for('producterror'))
    Session = sessionmaker(bind=engine)
    s = Session()
    products = Product(username = session['username'], purchaseno = POST_PURCHASE, modle = 'C')
    s.add(products)
    s.commit()
    return product()

@app.route('/purchase4', methods=['POST'])
def purchase4():
    try:
        POST_PURCHASE = int(request.form['productNo4'])  
    except Exception:
        return redirect(url_for('producterror'))
    Session = sessionmaker(bind=engine)
    s = Session()
    products = Product(username = session['username'], purchaseno = POST_PURCHASE, modle = 'D')
    s.add(products)
    s.commit()
    return product()

@app.route('/purchase5', methods=['POST'])
def purchase5():
    try:
        POST_PURCHASE = int(request.form['productNo5'])   
    except Exception:
        return redirect(url_for('producterror'))
    Session = sessionmaker(bind=engine)
    s = Session()
    products = Product(username = session['username'], purchaseno = POST_PURCHASE, modle = 'E')
    s.add(products)
    s.commit()
    return product()



@app.route('/purchase6', methods=['POST'])
def purchase6():
    try:
        POST_PURCHASE = int(request.form['productNo6'])  
    except Exception:
        return redirect(url_for('producterror'))
    Session = sessionmaker(bind=engine)
    s = Session()
    products = Product(username = session['username'], purchaseno = POST_PURCHASE, modle = 'F')
    s.add(products)
    s.commit()
    return product()

######################
# error for purchase #
######################

@app.route('/producterror')
def producterror():
    return product()

####################################################
# purchase for components of the secondhand divice #
####################################################

@app.route('/Purchase1', methods=['POST'])
def Purchase1():
    try:
        POST_PURCHASE = int(request.form['componentNo1'])   
    except Exception:
        return redirect(url_for('componenterror'))
    Session = sessionmaker(bind=engine)
    s = Session()
    components = Component(username = session['username'], Purchaseno = POST_PURCHASE, modle = 'A')
    s.add(components)
    s.commit()
    return component()

@app.route('/Purchase2', methods=['POST'])
def Purchase2():
    try:
        POST_PURCHASE = int(request.form['componentNo2'])  
    except Exception:
        return redirect(url_for('componenterror'))
    Session = sessionmaker(bind=engine)
    s = Session()
    components = Component(username = session['username'], Purchaseno = POST_PURCHASE, modle = 'B')
    s.add(components)
    s.commit()
    return component()

@app.route('/Purchase3', methods=['POST'])
def Purchase3():
    try:
        POST_PURCHASE = int(request.form['componentNo3'])   
    except Exception:
        return redirect(url_for('componenterror'))
    Session = sessionmaker(bind=engine)
    s = Session()
    components = Component(username = session['username'], Purchaseno = POST_PURCHASE, modle = 'C')
    s.add(components)
    s.commit()
    return component()

@app.route('/Purchase4', methods=['POST'])
def Purchase4():
    try:
        POST_PURCHASE = int(request.form['componentNo4'])   
    except Exception:
        return redirect(url_for('componenterror'))
    Session = sessionmaker(bind=engine)
    s = Session()
    components = Component(username = session['username'], Purchaseno = POST_PURCHASE, modle = 'D')
    s.add(components)
    s.commit()
    return component()

@app.route('/Purchase5', methods=['POST'])
def Purchase5():
    try:
        POST_PURCHASE = int(request.form['componentNo5'])   
    except Exception:
        return redirect(url_for('componenterror'))
    Session = sessionmaker(bind=engine)
    s = Session()
    components = Component(username = session['username'], Purchaseno = POST_PURCHASE, modle = 'E')
    s.add(components)
    s.commit()
    return component()

@app.route('/Purchase6', methods=['POST'])
def Purchase6():
    try:
        POST_PURCHASE = int(request.form['componentNo6'])   
    except Exception:
        return redirect(url_for('componenterror'))
    Session = sessionmaker(bind=engine)
    s = Session()
    components = Component(username = session['username'], Purchaseno = POST_PURCHASE, modle = 'F')
    s.add(components)
    s.commit()
    return component()

####################################
# error for purchase the component # 
####################################

@app.route('/componenterror')
def componenterror():
    return component()

##########################################
# a page about purchase history for user #
##########################################

@app.route('/purchasehistory')
def purchasehistory():
    Session = sessionmaker(bind=engine)
    s = Session()
    POST_USERNAME = session['username']
    query = s.query(Product).filter(Product.username.in_([POST_USERNAME])).all()
    query1 = s.query(Component).filter(Component.username.in_([POST_USERNAME])).all()
    return render_template('history.html',query=query,query1=query1)
    
###############################################
# sort by latest of purchase history for user #
###############################################

@app.route('/historysort')
def historysort():
    Session = sessionmaker(bind=engine)
    s = Session()
    POST_USERNAME = session['username']
    query = s.query(Product).filter(Product.username.in_([POST_USERNAME])).order_by(Product.id.desc()).all()
    query1 = s.query(Component).filter(Component.username.in_([POST_USERNAME])).order_by(Component.id.desc()).all()
    return render_template('history.html',query=query,query1=query1)

###########################################
# a page about purchase history for admin #
###########################################

@app.route('/adminhistory')
def adminhistory():
    Session = sessionmaker(bind=engine)
    s = Session()
    query = s.query(Product).all()
    query1 = s.query(Component).all()
    return render_template('adminhistory.html',query=query,query1=query1)

################################################
# sort by latest of purchase history for admin #
################################################

@app.route('/adminhistorysort')
def adminhistorysort():
    Session = sessionmaker(bind=engine)
    s = Session()
    query = s.query(Product).order_by(Product.id.desc()).all()
    query1 = s.query(Component).order_by(Component.id.desc()).all()
    return render_template('adminhistory.html',query=query,query1=query1)

#########################################
# forget password function (send email) #
#########################################

@app.route('/forgetpassword', methods=['POST'])
def forgetpassword():
    session['error'] = False
    POST_USERNAME = request.form['username']
    POST_EMAIL = request.form['email']
    Session = sessionmaker(bind=engine)
    s = Session()
    query = s.query(User).filter(User.username.in_([POST_USERNAME]), User.email.in_([POST_EMAIL]))
    result = query.first()
    if result:
        if not session['error']:
            pw = result.password
            
            msg = Message('Forgetpassword from HPC.(a company made up)',sender='205project2019@gmail.com',recipients=[str(POST_EMAIL)])
            msg.body = "Your password is" + " " + pw
            mail.send(msg)
            
            return index()
        else:
            print('error')
            session['error'] = True
            return redirect(url_for('forgeterror'))
    else:
        session['error'] = True
        return redirect(url_for('forgeterror'))

#############################
# error for forget password #
#############################

@app.route('/forgeterror')
def forgeterror():
    return index()

######################################################################
# override and refrash when i change the content of this python file #
######################################################################

@app.context_processor
def override_url_for():
    return dict(url_for=dated_url_for)

def dated_url_for(endpoint, **values):
    if endpoint == 'static':
        filename = values.get('filename', None)
        if filename:
            file_path = os.path.join(app.root_path, endpoint, filename)
            values['q'] = int(os.stat(file_path).st_mtime)
    return url_for(endpoint, **values)

#########################
# set secret key random #
#########################
   
if __name__ == '__main__':
    app.secret_key = os.urandom(12)
    app.run(debug = True)
