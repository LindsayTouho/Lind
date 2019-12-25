from lind.config import config

import mistune
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import html


def send_mail(subject, to_addr, to_name, content):
    from urllib import request
    import json

    data = json.dumps({
        "personalizations": [{"to": [{"email": to_addr, "name": to_name}]}],
        "from": {"email": config.EMAIL_ADDRESS, "name": config.SITE_NAME},
        "subject": subject,
        "content": [{"type": "text/html", "value": content}]
    })

    data = data.encode('utf-8')

    req = request.Request('https://api.sendgrid.com/v3/mail/send')
    req.add_header('Authorization', 'Bearer {}'.format(config.API_KEY))
    req.add_header('Content-type', 'application/json')
    request.urlopen(req, data)


class HighlightRenderer(mistune.Renderer):
    def block_code(self, code, lang):
        if not lang:
            return '\n<pre><code>%s</code></pre>\n' % \
                mistune.escape(code)
        lexer = get_lexer_by_name(lang, stripall=True)
        formatter = html.HtmlFormatter()
        return highlight(code, lexer, formatter)


class MdParser:
    def __init__(self):
        render = HighlightRenderer(escape=False, hard_wrap=True)
        markdown = mistune.Markdown(renderer=render)
        self.markdown = markdown

    @staticmethod
    def read_md_head(text):
        if not text.startswith('---'):
            return dict(), text
        result = dict()
        s = text.split('---\n')
        current_name = ''
        if s[0] != '':
            return dict(), text
        for attributes in s[1].splitlines():
            # print(attributes)
            if attributes.strip() == '':
                continue
            if attributes.strip() == '---':
                break
            if attributes.strip().startswith('-'):
                if current_name in result:
                    result[current_name].append(attributes.strip()[1:])
                elif current_name != '':
                    result[current_name] = [attributes.strip()[1:], ]
                continue
            if attributes.strip().endswith(':'):
                current_name = attributes.strip()[:-1].strip()
                continue
            else:
                try:
                    name = attributes.split(':')
                    value = ':'.join(name[1:])
                    name = name[0]
                except ValueError:
                    return dict(), text
                result[name.strip()] = value.strip()
        return result, '---\n'.join(s[2:])

    @staticmethod
    def insert_front_matter(text, data):
        s = text.split('---')
        if s[0] != '' or len(s) == 1:
            return '---\n'+data+'\n\n---\n'+text
        else:
            return '---'+s[1]+data+'\n\n---'+'---'.join(s[2:])

    def __call__(self, text):
        head = dict()
        body = text
        if text.strip().startswith('---'):
            head, body = self.read_md_head(text)

        body = self.markdown(body)
        section = body.split('<!-- more -->')
        if section[0] == body:
            section = body.split('<!-- More -->')
        if len(section) != 1:
            body = section[0]+'<!-- More --><div id="more"></div>' + ''.join(section[1:])
        return head, body





