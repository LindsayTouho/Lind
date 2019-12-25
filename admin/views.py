from lind.admin import admin
from lind.admin.reCaptcha import reCaptcha
from datetime import datetime, timedelta
from flask import flash, request, redirect, render_template, url_for, current_app
from flask_login import login_user, login_required, current_user, logout_user
from lind.db.models import User, Article, Tag, db, LoginInfo, BlackList
from lind.tools import send_mail
from lind.tools import MdParser


@admin.route('/')
@login_required
def index():
    black_list = BlackList.query.all()
    recent_login = LoginInfo.query.filter_by(uid=current_user.id).order_by(LoginInfo.time.desc()).slice(0, 10)
    drafts = Article.query.filter(Article.author_id == current_user.id).filter(Article.type
                                                                               == 'draft').filter(Article.title != "友链")
    return render_template('admin/index.html', blacklist=black_list, user=current_user, recent_login=recent_login,
                           drafts=drafts)


@admin.route('/joke/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        re_captcha = reCaptcha(current_app.config['G_VERIFY_SECRET_KEY'])
        ip_addr = request.headers.get('X-Real-IP', request.remote_addr)
        if 'g-recaptcha-response' in request.form and re_captcha.is_success(request.form['g-recaptcha-response'],
                                                                            ip_addr):
            user = User().query.filter_by(username=request.form.get('username')).first()
            if LoginInfo.query.filter(LoginInfo.time > datetime.now()-timedelta(minutes=30))\
                    .filter(LoginInfo.is_correct_passwd is False)\
                    .filter(LoginInfo.ip_addr == request.headers.get('X-Real-IP', request.remote_addr)).count() >= 3:
                flash("输入错误三次，请三十分钟后重试")
                if current_app.config.get('MAIL_NOTIFICATION', False):
                    send_mail('通知', user.email, user.username, '您在 www.remilia.me 的账号，从 {} 有多次失败的登陆尝试。'
                              .format(ip_addr))
                return redirect(url_for('admin.login'))
            if LoginInfo.query.filter(LoginInfo.time > datetime.now()-timedelta(hours=3))\
                    .filter(LoginInfo.is_correct_passwd == False)\
                    .filter(LoginInfo.ip_addr == request.headers.get('X-Real-IP', request.remote_addr)).count() >= 10:
                db.session.add(BlackList(ip_addr=request.headers.get('X-Real-IP', request.remote_addr),
                                         time=datetime.now()))
                db.session.commit()
                return redirect(url_for('admin.login'))

            if user is not None and current_app.config.get('MAIL_NOTIFICATION', False):
                send_mail('登陆通知', user.email, user.username, '你有新的登陆活动，从{}。如果不是本人操作，请尽快更改密码'
                          .format(ip_addr))

            if user is not None and user.verify_password(request.form.get('password')):
                last_log = LoginInfo.query.filter(LoginInfo.uid == user.id).filter(LoginInfo.is_correct_passwd == True)\
                    .order_by(LoginInfo.time.desc()).first()
                info = LoginInfo()
                info.ip_addr = request.headers.get('X-Real_IP', request.remote_addr)
                info.uid = user.id
                info.is_correct_passwd = True
                info.time = datetime.now()
                db.session.add(info)
                db.session.commit()
                login_user(user, remember=request.form.get("remember_me", False))
                if last_log is not None:
                    flash('登陆成功\n您最近的登陆时间为{}，登陆ip为{}'
                          .format(last_log.time.strftime('%b %d %H:%M'), last_log.ip_addr))
                else:
                    flash("欢迎使用此博客")
                return redirect(url_for('admin.index'))
            else:
                info = LoginInfo()
                info.ip_addr = ip_addr
                info.is_correct_passwd = False
                info.time = datetime.now()
                if user is not None:
                    info.uid = user.id
                db.session.add(info)
                db.session.commit()
                flash('登陆失败，用户名或密码错误')
        else:
            flash('请先进行人机验证')
    return render_template('admin/login.html')


@admin.route('/logout/')
@login_required
def logout():
    if current_user.is_authenticated:
        logout_user()
    return redirect(url_for('main.index'))


@admin.route('/list/')
@login_required
def articles_list():
    articles = Article.query.filter_by(author_id=current_user.id).order_by(Article.time.desc())
    anonymous_article = Article.query.filter_by(author_id=None).order_by(Article.time.desc())
    return render_template('admin/articles.html', user=current_user, articles=articles,
                           anoymous_article=anonymous_article)


@admin.route('/editor/', methods=['GET', ])
@login_required
def editor():
    id_input = ''
    if 'id' in request.args:
        article_id = request.args.get('id')
        article = Article.query.filter_by(id=article_id).first_or_404()
        id_input = '<input type="hidden" value="{}" name="id" id="id">'.format(str(article_id))
        with open(article.path, 'r', encoding='utf-8') as f:
            text = f.read()
            head, markdown = MdParser.read_md_head(text)
            if isinstance(head.get('tags'), list):
                head['tags'] = ';'.join(head['tags'])
        text = repr(text)
        text = text.replace('/', '\/')

        return render_template('admin/editor.html', head=head, markdown=text, id_input=id_input, article=article)
    else:
        return render_template('admin/editor.html', head=None, markdown='""', id_input=id_input, article=None)


@admin.route('/delete')
@login_required
def delete():
    import os
    article_id = request.args.get('id')
    obj = Article.query.filter_by(id=article_id).first()
    if obj.author_id is None and obj.author_id != current_user.id:
        flash("请不要删除非本用户的文章")
        return redirect(url_for('admin.articles_list'))
    path = obj.path
    for i in Tag.query.filter_by(article_id=article_id):
        db.session.delete(i)
    if os.path.isfile(path):
        os.remove(path)
    db.session.delete(obj)
    db.session.commit()
    flash("删除成功")
    return redirect(url_for('admin.articles_list'))


@admin.route('clear_login_info')
@login_required
def clear_login_info():
    infos = LoginInfo.query.filter_by(uid=current_user.id)
    for i in infos:
        db.session.delete(i)
    db.session.commit()
    flash('清除成功')
    return redirect(url_for('admin.index'))
