from flask import Flask, flash, render_template,request,redirect

from flask_login import LoginManager,login_user,UserMixin,logout_user

from flask_sqlalchemy import SQLAlchemy

from flask_bcrypt import Bcrypt,bcrypt

from datetime import datetime

app = Flask(__name__)
bcrypt = Bcrypt(app)
login_manager = LoginManager()  
login_manager.init_app(app)

app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:1234@localhost:5433/Login"
app.config['SECRET_KEY'] = 'secret'
db = SQLAlchemy(app)

class Todo(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    desc = db.Column(db.String(500), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return self.email

class Login(db.Model,UserMixin):
    id = db.Column(db.Integer,primary_key= True)
    email = db.Column(db.String,unique=True)
    password = db.Column(db.String,nullable=False)

    def __repr__(self):
        return self.email

@app.route('/index', methods=['GET', 'POST'])
def main():
    if request.method=='POST':
        title = request.form.get('title')
        desc = request.form.get('desc')
        todo = Todo(title=title, desc=desc)
        db.session.add(todo)
        db.session.commit()
        
    allTodo = Todo.query.all() 
    return render_template('index.html', allTodo=allTodo)

@app.route("/",methods=['POST','GET'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        enc_password = bcrypt.generate_password_hash(password).decode('utf-8')
        user = Login(email=email,password=enc_password)
        db.session.add(user)
        db.session.commit()
        return redirect('/login')
    return render_template("register.html")

@app.route('/show')
def contents():
    allTodo = Todo.query.all()
    print(allTodo)
    return ''

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = Login.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password,password):
            login_user(user)
            return redirect('/index') 
        else:
            flash('Email and password did not matched!!!','warning')
            return redirect('/login')
    else:
        return render_template("login.html")



@login_manager.user_loader
def load_user(user_id):              
    return Login.query.get(int(user_id))

@app.route('/update/<int:sno>', methods=['GET', 'POST'])
def update(sno):
    if request.method=='POST':
        title = request.form['title']
        desc = request.form['desc']
        todo = Todo.query.filter_by(sno=sno).first()
        todo.title = title
        todo.desc = desc
        db.session.add(todo)
        db.session.commit()
        return redirect("/index")
        
    todo = Todo.query.filter_by(sno=sno).first()
    return render_template('update.html', todo=todo)

@app.route('/delete/<int:sno>')
def delete(sno):
    todo = Todo.query.filter_by(sno=sno).first()
    db.session.delete(todo)
    db.session.commit()
    return redirect("/index")

@app.route("/logout")
def logout():
    logout_user()
    flash('User logout Suceessfully!','success')
    return redirect('/login')

if __name__ == "__main__":
    app.run(debug=True)