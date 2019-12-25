from . import app
from flask import render_template, request, abort
from lind.db.models import BlackList


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(401)
def unauthorized(e):
    return render_template('401.html'), 401


@app.before_request  # 这里感觉效率好低
def check_ip():
    if BlackList().query.filter_by(ip_addr=request.headers.get('X-Real-IP')).count() != 0:
        abort(404)


"""
注册jinja2 过滤器
"""


def summary(s):
    string = str(s).split('<!-- more -->')[0]
    if string == s:
        string = str(s).split('<!-- More -->')[0]
    return string


def datetime_filter(t):
    return t.strftime('%b %d, %Y')


BlockElement = ['<script>', '</script>', '<frame>', '</frame>', '<iframe>', '</iframe>', '<object>', '</object>']


def html_ele_block(html):
    for e in BlockElement:
        html = html.replace(e, '')
    return html


app.jinja_env.filters['summary'] = summary
app.jinja_env.filters['datetime_filter'] = datetime_filter
app.jinja_env.filters['html_ele_block'] = html_ele_block

