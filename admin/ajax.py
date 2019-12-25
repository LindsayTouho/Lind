from . import admin
from flask_login import login_required, current_user
from flask import request, current_app, jsonify
from lind.db.models import Article, Tag, User, db
import os
from ..tools import MdParser
from sqlalchemy.exc import IntegrityError


# BlockElement = ['<script>', '</script>', '<frame>', '</frame>', '<iframe>', '</iframe>', '<object>', '</object>']


@admin.route('/save/', methods=['POST', ])
@login_required
def save():
    md = MdParser()
    from datetime import datetime
    markdown = request.form.get('content', '').replace('\r\n', '\n')
    # markdown = str(Markup.escape(markdown))
    # for e in BlockElement:
    #     markdown = markdown.replace(e, '')
    head, text = md(markdown)
    aid = int(request.form.get('id'))
    if aid == -1:
        article = Article(title=head.get('title', 'untitled'), text=text)
    else:
        article = Article.query.filter_by(id=aid).first_or_404()
        article.title = head.get('title', 'untitled')
        article.text = text
    if 'date' in head:
        try:
            article.time = datetime.strptime(head['date'], '%Y-%m-%d')
        except ValueError:
            return jsonify(message="Time date doesn't match format '%Y-%m-%d'", id=-1)
    else:
        article.time = datetime.now()
        markdown = md.insert_front_matter(markdown, 'date: ' + datetime.now().strftime('%Y-%m-%d'))
    if 'type' not in head:
        markdown = md.insert_front_matter(markdown, "type: draft")

    article.type = head.get("type", 'draft')
    if 'author' in head:
        author = User.query.filter_by(username=head['author']).first()
        if author is None:
            return jsonify(message='Error author', id=-1)
        article.author_id = author.id

    else:
        article.author_id = current_user.id
        markdown = md.insert_front_matter(markdown, "author: "+current_user.username)
    try:
        article.path = os.path.join(current_app.config.get('RESOURCE_PATH'), str(article.title)+'.md')
    except TypeError:
        return jsonify(message='Source storage error', id=-1)
    
    if aid == -1:
        db.session.add(article)
    try:
        db.session.commit()
    except IntegrityError:
        return jsonify(message='Front matter error', id=-1)

    with open(article.path, 'w', encoding='utf-8') as f:
        f.write(markdown)

    tags = head.get('tags', [])
    for i in Tag.query.filter_by(article_id=article.id):
        if i.tag_name not in tags or i.tag_name == '':
            db.session.delete(i)
    for value in tags:
        if value.strip() == '' or Tag.query.filter_by(tag_name=value.strip(), article_id=article.id).count() != 0:
            continue
        tag = Tag()
        tag.tag_name = value.strip()
        tag.article_id = article.id
        db.session.add(tag)
    db.session.commit()
    return jsonify(message='Saved', id=article.id)