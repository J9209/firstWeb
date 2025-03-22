from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate  # 載入 Flask-Migrate 用於資料庫遷移
import os

app = Flask(__name__)

# 設定資料庫，這裡使用 SQLite 資料庫
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///books.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 初始化 SQLAlchemy 用來操作資料庫
db = SQLAlchemy(app)

# 初始化 Flask-Migrate
migrate = Migrate(app, db)

# 資料庫模型：書籍的模型，包含書名、作者、價格和描述等欄位
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(500))
    quantity = db.Column(db.Integer, default=1)  # 新增庫存數量欄位，預設為 1

    def __repr__(self):
        return f'<Book {self.title}>'

# 創建資料庫（如果還沒有）
with app.app_context():
    db.create_all()

# 主頁：顯示所有書籍
@app.route('/')
def index():
    books = Book.query.all()  # 從資料庫讀取所有書籍
    return render_template('index.html', books=books)

# 上架書籍：顯示表單來上架新書
@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        price = float(request.form['price'])
        description = request.form['description']
        
        
        # 新建書籍對象並加入資料庫
        new_book = Book(title=title, author=author, price=price, description=description)
        db.session.add(new_book)
        db.session.commit()

        return redirect(url_for('index'))  # 完成後重定向到主頁

    return render_template('add_book.html')  # 顯示上架書籍表單頁面

# 顯示書籍詳細信息
@app.route('/book_detail/<int:book_id>', methods=['GET'])
def book_detail(book_id):
    book = Book.query.get_or_404(book_id)  # 根據書籍 ID 查找書籍
    return render_template('book_detail.html', book=book)

# 購買書籍：更新書籍的庫存
@app.route('/buy_book/<int:book_id>', methods=['POST'])
def buy_book(book_id):
    book = Book.query.get_or_404(book_id)  # 根據書籍 ID 查找書籍
    if book.quantity > 0:
        book.quantity -= 1  # 購買時減少庫存
        db.session.commit()  # 提交更改
        return redirect(url_for('book_detail', book_id=book.id))
    else:
        return "庫存不足，無法購買", 400  # 如果庫存為 0，顯示錯誤

if __name__ == '__main__':
    # app.run(debug=True)
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)