import os
import logging
import markdown
import re
import json
from datetime import datetime
from flask import Flask, abort, request, render_template
from werkzeug.middleware.proxy_fix import ProxyFix

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
app.wsgi_app = ProxyFix(
    app.wsgi_app,
    x_for=2,
    x_proto=1,
    x_host=1,
    x_port=1
)

BASE_DIR = os.path.dirname(__file__)
POSTS_DIR = os.path.join(BASE_DIR, "post")

SITE_NAME = "LonfLonf Blog"
SITE_DESCRIPTION = "Write-ups, CTFs, tech notes, and random thoughts from LonfLonf."

CATEGORIES = {
    "writeups": "Write-ups",
    "tech": "Tech Notes",
    "randomstuff": "Random Stuff"
}

@app.before_request
def log_request():
    app.logger.info(
        f"IP={request.remote_addr} "
        f"METHOD={request.method} "
        f"PATH={request.path} "
        f"UA={request.headers.get('User-Agent')}"
    )

def collect_posts_for_sitemap():
    posts = []
    for root, dirs, files in os.walk(POSTS_DIR):
        for file in files:
            if not file.lower().endswith(".md"):
                continue
            rel_path = os.path.relpath(os.path.join(root, file), POSTS_DIR)
            parts = rel_path.split(os.sep)
            if len(parts) > 1:
                category = parts[0].lower()
                name = os.path.splitext(file)[0]
                posts.append((category, name))
    return posts


@app.context_processor
def inject_site_defaults():
    base_url = request.url_root.rstrip('/') if request else ''
    return {
        'site_name': SITE_NAME,
        'site_description': SITE_DESCRIPTION,
        'base_url': base_url
    }


def _extract_title_and_description_from_markdown(content: str):
    title = None
    description = None
    for line in content.splitlines():
        ln = line.strip()
        if not ln:
            continue
        if ln.startswith('#') and title is None:
            title = ln.lstrip('#').strip()
            continue
        if not ln.startswith('#') and description is None:
            description = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", ln)
            description = re.sub(r'[`*_>]', '', description)
            description = description[:160]
            break
    return title, description


def _sanitize_post_html(html: str):
    def repl(match):
        tag = match.group(0)
        if 'alt=' not in tag:
            tag = tag.replace('<img', '<img alt=""', 1)
        if 'loading=' not in tag:
            tag = tag.replace('<img', '<img loading="lazy"', 1)
        return tag

    html = re.sub(r'<img[^>]*>', repl, html)
    return html

# Basic Routes
@app.route('/')
def home(user=None):
    
    return render_template('aboutme.html', user=user)

@app.route('/blog')
@app.route('/blog/search/<name>')
@app.route('/blog/<categories>')
def blog(categories=None, name=None):
    posts2 = []
    configFile = os.path.join(BASE_DIR, "config.json")
    logging.info(f" Configuration file path: {configFile}")
    
    with open(configFile, encoding='utf-8') as f:
        postsJson = json.load(f)
    logging.info(f" Loaded configuration: {postsJson}")
    
    for post in postsJson:
        logging.info(f" Post from config: {post['name']}")
        post['fileName'] = post['file']
        post['file'] = os.path.join(POSTS_DIR, post['file']) 
        # Format date for display (dateAtCreation expected in ISO 8601)
        date_str = post.get('dateAtCreation') or post.get('date_at_creation') or post.get('date')
        if date_str:
            try:
                dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                post['date'] = dt.strftime('%b %d, %Y')
                post['date_iso'] = dt.isoformat()
            except Exception:
                post['date'] = date_str
        else:
            post['date'] = ''

        posts2.append(post)
        
    page_title = "Blog - " + SITE_NAME
    page_description = SITE_DESCRIPTION

    if categories == None and name == None:
        return render_template('blog.html', files=posts2, categories='all', page_title=page_title, page_description=page_description)
    elif categories != None and name == None:
            category = re.search('Writeups|Tech|Randomstuff', categories, re.IGNORECASE)
            logging.info(f" Requested category: {categories}, Matched category: {category.group() if category else 'None'}")
            
            if category is None:
                abort(404)
            
            files = []
            for p in posts2:
                if p["category"] == category.group():
                    files.append(p)
            logging.info(f" Files in category '{category.group()}': {files}")
            
            return render_template('blog.html', files=files, categories=categories, page_title=f"{categories} - {SITE_NAME}", page_description=f"Posts in {categories} on {SITE_NAME}")
    elif categories == None and name != None:
            outputFiles = []
            for p in posts2:
                if re.search(re.escape(name), p["file"], re.IGNORECASE):
                    outputFiles.append(p)
            logging.info(f" Search results for '{name}': {outputFiles}")     
            return render_template('blog.html', name=name, files=outputFiles, categories='all', page_title=f"Search: {name} - {SITE_NAME}", page_description=f"Search results for {name} on {SITE_NAME}")
    else:
        abort(404)

#Variable Rules
@app.route('/post/<categories>/<name>')
def show_post(name=None, categories=None):
    logging.info(f" Posts directory: {POSTS_DIR}")
    html = ""
    
    # Check if category and name are provided and if exists
    if categories != None and name != None: # User click in Post
            tree = name.split('_')
            logging.info(f" Post name: {name}")
            logging.info(f" Post name split by '_': {tree}")
            try: 
                post_path = os.path.join(POSTS_DIR, f"{name}")
                logging.info(f" Constructed post path: {post_path}")
                with open(post_path, encoding='utf-8') as pf:
                    content = pf.read()
                html = markdown.markdown(content, extensions=['fenced_code', 'codehilite', 'tables', 'toc'])
            except FileNotFoundError:
                logging.error(f" FileNotFoundError: The file '{name}' in category '{categories}' was not found.")
                abort(404)

            md_title, md_desc = _extract_title_and_description_from_markdown(content)

            post_meta = {}
            try:
                with open(os.path.join(BASE_DIR, 'config.json'), encoding='utf-8') as cf:
                    cfg = json.load(cf)
                    for p in cfg:
                        if 'file' in p and p['file'] == name:
                            post_meta = p
                            break
            except Exception:
                post_meta = {}

            page_title = md_title or post_meta.get('name') or SITE_NAME
            page_description = md_desc or post_meta.get('summary') or SITE_DESCRIPTION

            # sanitize images and add lazy-loading/alt
            html = _sanitize_post_html(html)

    return render_template('post.html', markdown=html, page_title=page_title, page_description=page_description, is_article=True, article_date=post_meta.get('dateAtCreation') if post_meta else None)

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

@app.route('/robots.txt')
def robots():
    base_url = request.url_root.rstrip('/')
    content = "\n".join([
        "User-agent: *",
        "Allow: /",
        f"Sitemap: {base_url}/sitemap.xml"
    ])
    return content, 200, {"Content-Type": "text/plain; charset=utf-8"}

@app.route('/sitemap.xml')
def sitemap():
    base_url = request.url_root.rstrip('/')
    urls = [
        f"{base_url}/",
        f"{base_url}/blog",
        f"{base_url}/blog/writeups",
        f"{base_url}/blog/tech",
        f"{base_url}/blog/randomstuff",
    ]

    for category, name in collect_posts_for_sitemap():
        urls.append(f"{base_url}/post/{category}/{name}")

    xml_items = "\n".join([f"  <url><loc>{u}</loc></url>" for u in urls])
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{xml_items}
</urlset>
"""
    return xml, 200, {"Content-Type": "application/xml; charset=utf-8"}

if __name__ == '__main__':
    app.run()
