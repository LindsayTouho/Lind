from flask_script import Manager
import os
from lind.db.models import db, app
from sqlalchemy.exc import IntegrityError

manager = Manager(app)


@manager.command
def clear():
    from lind.db.models import Article, Tag
    for i in Tag.query:
        db.session.delete(i)
    for i in Article.query:
        db.session.delete(i)
    db.session.commit()


@manager.command
def refresh(path=app.config['RESOURCE_PATH']):
    from lind.tools import MdParser
    md = MdParser()
    from datetime import datetime
    from lind.db.models import Article, User, Tag

    clear()
    print(os.path.realpath(path), os.listdir(path))
    for l in os.listdir(path):
        if l.endswith('.md'):
            with open(os.path.join(path, l), encoding='utf-8') as f:
                head, body = md(f.read())
                article = Article(title=head.get('title', 'untitled'), text=body)
                try:
                    article.time = datetime.strptime(head.get('date', datetime.now().strftime('%Y-%m-%d')),
                                                     '%Y-%m-%d')
                except ValueError:
                    pass
                author = User.query.filter_by(username=head.get('author'))
                if author.count() != 0:
                    article.author_id = author.first().id
                article.path = os.path.join(path, l)
                article.type = 'draft'
                try:
                    db.session.add(article)
                except IntegrityError:
                    pass
                db.session.commit()

                if isinstance(head.get('tags'), str):
                    head['tags'] = head['tags'].split(';')
                for value in head.get('tags', list()):
                    if Tag.query.filter(Tag.tag_name == value.strip()).filter(Tag.article_id == article.id).count() != 0:
                        continue
                    tag = Tag()
                    tag.tag_name = value.strip()
                    tag.article_id = article.id
                    db.session.add(tag)

                db.session.commit()
            print('Add', l)

        elif os.path.isdir(os.path.join(path, l)):
            refresh(path=os.path.join(path, l))


@manager.command
def init():
    db.create_all()
    if not os.path.exists(app.config['RESOURCE_PATH']):
        os.makedirs(app.config['RESOURCE_PATH'])
    print("Done!")


@manager.command
def useradd():
    import getpass
    from lind.db.models import User
    username = input("Input user name:")
    pwd = getpass.getpass()
    if getpass.getpass() != pwd:
        print('Please Input The Correct Password')
        exit(1)
    email = input("Input your email:")
    User.insert_admin(email, username, pwd)


@manager.command
def help():
    print("""
        Lind is a blog system based on flask
        Usage: lind -[option]
            -v:Show the version of lind
            -i:Initialization the database and file storage path
            -a:Add new user
            -f:Flush the article in database from stored file
            -c:Clear the article in database, this action would not delete file from system
    """)


def main():
    manager.run()


if __name__ == '__main__':
    main()
