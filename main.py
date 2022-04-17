from flask import Flask, render_template, request, url_for, session, redirect
import psycopg2
import json
# create an object
app = Flask(__name__)

# connect to an existing database
#conn = psycopg2.connect(user="postgres", password="lilian",
                        #host="localhost", port="5432", database="duka")
conn=psycopg2.connect(user="zbgesovjbfrlda",password="7247fc832cd35ab82a8756f3244e6dd15e622705e6d0c5c753548a0886c80b59",host="ec2-99-81-137-11.eu-west-1.compute.amazonaws.com",port="5432",database="dckkmj8bg4akmc")
# create a cursor to perform database operation
cur = conn.cursor()

cur.execute("CREATE TABLE IF NOT EXISTS products (id serial PRIMARY KEY,name VARCHAR(100),buying_price INT,selling_price INT,stock_quantity INT);")
cur.execute("CREATE TABLE IF NOT EXISTS sales (id serial PRIMARY KEY,pid INT, quantity INT, created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW() );")
cur.execute("CREATE TABLE IF NOT EXISTS login (id integer NOT NULL, username character varying(50) NOT NULL,email character varying(50) NOT NULL, password character varying(15) NOT NULL);")
conn.commit()
# create a home route
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:lilian@localhost:5432/duka'
app.config["SECRET_KEY"] = "#lilian@haki"
#conn = psycopg2.connect(user="postgres", password="lilian",
                       # host="localhost", port="5432", database="duka")
conn=psycopg2.connect(user="zbgesovjbfrlda",password="7247fc832cd35ab82a8756f3244e6dd15e622705e6d0c5c753548a0886c80b59",host="ec2-99-81-137-11.eu-west-1.compute.amazonaws.com",port="5432",database="dckkmj8bg4akmc")

@app.route("/login", methods=["GET", "POST"])
def login():
    msg = ""
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        cur.execute(
            "select * from login where username=%s and password=%s",
            (username, password),
        )
        record = cur.fetchone()
        if record:
            session["loggedin"] = True
            session["username"] = record[1]
            return redirect("/dashboard")
            # return "WELCOME"
        else:
            msg = "Incorrect username/password.Try again!"
    return render_template("login.html", msg=msg)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        user_name = request.form["username"]
        password = request.form["password"]
        email = request.form["email"]
        cur.execute(
            "INSERT INTO login (username,password,email) VALUES(%s,%s,%s)",
            (user_name, password, email),
        )
        conn.commit()
        return redirect("/login")
    else:
        return render_template("register.html")


# @app.route("/sign_up", methods=["GET", "POST"])
# def dashboard():


@app.route("/logout")
def logout():
    # Remove session data, this will log the user out
    session.pop("loggedin", None)
    session.pop("id", None)
    session.pop("username", None)
    # Redirect to login page
    return redirect("/login")


@app.route("/", methods=["GET", "POST"])
def homepage():
    return render_template("homepage.html")


@app.route("/sales/<int:pid>", methods=["GET", "POST"])
def view_sales(pid):
    cur.execute("select * from sales where pid=%s", [pid])
    data = cur.fetchall()
    return render_template("sales.html", data=data)


@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    cur.execute("select count(id) from products")
    data = cur.fetchone()
    print(data)
    cur.execute("select count(id) from sales")
    dataa = cur.fetchone()
    print(dataa)
    cur.execute("""select sum((products.selling_price-products.buying_price)*sales.quantity) as profit, products.name from sales 
        join products on products.id=sales.pid
        GROUP BY products.name""")
    graph = cur.fetchall()
    v = []
    y = []

    for i in graph:
        v.append(i[1])
        y.append(i[0])
    print(v)
    print(y)
    return render_template("dashboard.html", data=data, dataa=dataa, y=y, v=v, graph=graph)


@app.route("/products", methods=["GET", "POST"])
def products():
    if request.method == "POST":
        name = request.form["name"]
        buying_price = request.form["buying_price"]
        selling_price = request.form["selling_price"]
        stock_quantity = request.form["stock_quantity"]
        print(name)
        print(buying_price)
        print(selling_price)
        print(stock_quantity)

        cur.execute("insert into products(name,buying_price,selling_price,stock_quantity) values(%s,%s,%s,%s)",
                    (name, buying_price, selling_price, stock_quantity))
        conn.commit()
        return redirect("/products")

    else:
        cur.execute("select * from products")
        data = cur.fetchall()
        return render_template("products.html", data=data)


@app.route("/sales", methods=["POST", "GET"])
def sales():

    cur.execute("select * from sales")
    data = cur.fetchall()
    return render_template("sales.html", data=data)


@app.route("/make_sale", methods=["POST", "GET"])
def make_sale():
    if request.method == "POST":
        pid = request.form["product_id"]
        quantity = request.form["stock_quantity"]
        cur.execute("select stock_quantity from products where id=%s", [pid])
        stock_quantity = cur.fetchone()
        print(stock_quantity)
        rem = int(stock_quantity[0])-int(quantity)
        if rem < 0:
            pass
            return redirect('/products')
        else:

            cur.execute("insert into sales(pid,quantity,created_at) values(%s,%s,%s)", (
                pid, quantity, "NOW()"))

            cur.execute("""update products set stock_quantity=%(rem)s where id=%(pid)s""", {
                        "pid": pid, "rem": rem})
            conn.commit()
            cur.execute("select * from sales")
            data = cur.fetchall()
            return render_template("make_sale.html", data=data)


if __name__ == '__main__':
    app.run(debug=True)
