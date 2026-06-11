from flask import Flask, render_template, request, redirect, session
from database import (
    init_db, add_user, get_user, get_user_by_id,
    add_task, get_tasks_by_user, delete_task, toggle_task,
    search_tasks, get_task_by_id, update_task
)

app = Flask(__name__)
app.secret_key = 'секретный_ключ_для_todo_12345'

init_db()

@app.route('/')
def index():
    if not session.get('user_id'):
        return redirect('/login')
    
    category = request.args.get('category', 'все')
    tasks = get_tasks_by_user(session['user_id'], category)
    user = get_user_by_id(session['user_id'])
    
    categories = ['все', 'работа', 'личное', 'учеба', 'дом']
    
    return render_template('index.html', 
                          tasks=tasks, 
                          username=user['username'],
                          current_category=category,
                          categories=categories)

@app.route('/add', methods=['POST'])
def add():
    if not session.get('user_id'):
        return redirect('/login')
    
    title = request.form.get('title', '').strip()
    description = request.form.get('description', '').strip()
    category = request.form.get('category', 'личное')
    
    if title:
        add_task(session['user_id'], title, description, category)
    return redirect('/')

@app.route('/toggle/<int:task_id>')
def toggle(task_id):
    if not session.get('user_id'):
        return redirect('/login')
    toggle_task(task_id, session['user_id'])
    return redirect('/')

@app.route('/delete/<int:task_id>')
def delete(task_id):
    if not session.get('user_id'):
        return redirect('/login')
    delete_task(task_id, session['user_id'])
    return redirect('/')

@app.route('/edit/<int:task_id>', methods=['GET', 'POST'])
def edit(task_id):
    if not session.get('user_id'):
        return redirect('/login')
    
    task = get_task_by_id(task_id, session['user_id'])
    if not task:
        return redirect('/')
    
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        category = request.form.get('category', 'личное')
        
        if title:
            update_task(task_id, session['user_id'], title, description, category)
        return redirect('/')
    
    categories = ['работа', 'личное', 'учеба', 'дом']
    return render_template('edit.html', task=task, categories=categories)

@app.route('/search')
def search():
    if not session.get('user_id'):
        return redirect('/login')
    
    query = request.args.get('q', '').strip()
    if query:
        tasks = search_tasks(session['user_id'], query)
    else:
        tasks = get_tasks_by_user(session['user_id'])
    
    user = get_user_by_id(session['user_id'])
    categories = ['все', 'работа', 'личное', 'учеба', 'дом']
    
    return render_template('index.html', 
                          tasks=tasks, 
                          username=user['username'],
                          current_category='все',
                          categories=categories,
                          search_query=query)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        user = get_user(username, password)
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect('/')
        else:
            return render_template('login.html', error='Неверный логин или пароль')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        if not username or not password:
            return render_template('register.html', error='Заполните все поля')
        
        if add_user(username, password):
            return redirect('/login')
        else:
            return render_template('register.html', error='Пользователь уже существует')
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)