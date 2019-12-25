from . import main
from flask.templating import render_template
from lind.db.models import *
from math import ceil
from flask import redirect, url_for, abort, current_app, send_from_directory, request
from flask_login import current_user


@main.route('/')
def index():
    articles = Article.query.filter_by(type='post').order_by(Article.time.desc()).limit(10)
    page_count = Article.query.filter_by(type='post').count()

    if 'X-PJAX' in request.headers:
        return render_template('main/index.html', articles=articles, page_count=ceil(page_count/10), current_page=0,
                               pjax=True)
    else:
        nav_pages = Article.query.filter(Article.type.startswith('page_')).all()
        return render_template('main/index.html', articles=articles, page_count=ceil(page_count/10), current_page=0,
                           nav_pages=nav_pages, pjax=False)


@main.route('/page/<string:page_name>/')
def nav_page(page_name):
    nav_pages = Article.query.filter(Article.type.startswith('page_')).all()
    article = Article.query.filter_by(type='page_'+page_name).first_or_404()

    if 'X-PJAX' in request.headers:
        return render_template('main/detail.html', article=article, pjax=True)
    return render_template('main/detail.html', article=article, nav_pages=nav_pages, pjax=False)


@main.route('/<int:num>/')
def page(num):
    if num == 0:
        return redirect(url_for('main.index'))
    else:
        articles = Article.query.filter_by(type='post').order_by(Article.time.desc()).slice(10*num, 10*num+10)
        if articles is None:
            abort(404)
        page_count = Article.query.filter_by(type='post').count()
        if 'X-PJAX' in request.headers:
            return render_template('main/index.html', articles=articles, page_count=ceil(page_count / 10),
                                   current_page=num, user=current_user, pjax=True)
        else:
            nav_pages = Article.query.filter(Article.type.startswith('page_')).all()
            return render_template('main/index.html', articles=articles, page_count=ceil(page_count / 10),
                                   current_page=num, nav_pages=nav_pages, pjax=False)


@main.route('/article/<int:article_id>/')
def detail(article_id):
    article = Article.query.filter_by(id=article_id).first_or_404()
    if article.type != 'post':
        abort(404)
    if 'X-PJAX' in request.headers:
        return render_template('main/detail.html', article=article, pjax=True)
    else:
        nav_pages = Article.query.filter(Article.type.startswith('page_')).all()
        return render_template('main/detail.html', article=article, nav_pages=nav_pages, pjax=False)


@main.route('/about/')
def about():
    if 'X-PJAX' in request.headers:
        return render_template('main/about.html', pjax=True)
    else:
        nav_pages = Article.query.filter(Article.type.startswith('page_')).all()
        return render_template('main/about.html',  nav_pages=nav_pages, pjax=False)


@main.route('/tag/<string:tag_name>/')
def tag(tag_name):
    articles = []
    for item in Tag.query.filter_by(tag_name=tag_name):
        articles.append(Article.query.order_by(Article.time).filter_by(id=item.article_id).first())
    if 'X-PJAX' in request.headers:
        return render_template('main/archives.html', articles=articles, pjax=True)
    else:
        nav_pages = Article.query.filter(Article.type.startswith('page_')).all()
        return render_template('main/archives.html', articles=articles, nav_pages=nav_pages, pjax=False)


@main.route('/archives/')
def archives():
    if 'X-PJAX' in request.headers:
        return render_template('main/archives.html', articles=Article.query.filter_by(type='post')
                               .order_by(Article.time.desc()), pjax=True)
    else:
        nav_pages = Article.query.filter(Article.type.startswith('page_')).all()
        return render_template('main/archives.html', articles=Article.query.filter_by(type='post')
                           .order_by(Article.time.desc()), nav_pages=nav_pages, pjax=False)


@main.route('/favicon.ico')
def ico():
    return send_from_directory(current_app.static_folder, 'images/favicon.ico')


@main.route('/links/')
def friend_links():
    article = Article.query.filter_by(title='友链').first_or_404()
    if 'X-PJAX' in request.headers:
        return render_template('main/detail.html', article=article, pjax=True)
    else:
        nav_pages = Article.query.filter(Article.type.startswith('page_')).all()
        return render_template('main/detail.html', article=article, nav_pages=nav_pages, pjax=False)


@main.route('/robot.txt')
def robot():
    return send_from_directory(current_app.static_folder, 'robot.txt')


