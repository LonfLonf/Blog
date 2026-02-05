import os
import logging
import markdown
import re
from flask import Flask, abort, request, render_template

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

BASE_DIR = os.path.dirname(__file__)
POSTS_DIR = os.path.join(BASE_DIR, "post")

def get_category_by_name(name):
    if re.search('WriteUp', name, re.IGNORECASE):
        return 'writeups'
    elif re.search('Tech', name, re.IGNORECASE):
        return 'tech'
    else:
        return 'randomstuff'

# Basic Routes
@app.route('/')
def home(user=None):
    return render_template('aboutme.html', user=user)

@app.route('/blog')
@app.route('/blog/search/<name>')
@app.route('/blog/<categories>')
def blog(categories=None, name=None):
    activeCategories = []
    posts = []
    
    for root, dirs, files in os.walk(POSTS_DIR):
        for dir in dirs:
            activeCategories.append(dir)
        for file in files:
            rel_path = os.path.relpath(os.path.join(root, file), POSTS_DIR)
            parts = rel_path.split(os.sep)
            if len(parts) > 1:
                category = parts[0].lower()
            else:
                category = get_category_by_name(file)
            posts.append({"file": file, "category": category})
    
    logging.info(f" Active Categories: {activeCategories}")
    logging.info(f" Active Files: {[p['file'] for p in posts]}")
        
    if categories == None and name == None:
        return render_template('blog.html', files=posts, categories='all')
    elif categories != None and name == None:
            category = re.search('writeups|tech|randomstuff', categories, re.IGNORECASE)
            
            if category is None:
                abort(404)
                
            logging.info(f" Requested category: {categories}, Matched category: {category.group()}")
            
            nameRe = None
            if category.group().lower() == 'writeups':
                nameRe = re.compile(r'writeup', re.IGNORECASE)
            elif category.group().lower() == 'tech':
                nameRe = re.compile(r'tech', re.IGNORECASE)
            elif category.group().lower() == 'randomstuff':
                nameRe = re.compile(r'^(?!.*(?:writeup|tech)).*$', re.IGNORECASE)
            
            logging.info(f" Regex for filtering files in category '{categories}'")
            
            files = []
            for p in posts:
                if p["category"] == category.group().lower() and nameRe.search(p["file"]):
                    files.append(p)
            logging.info(f" Files in category '{nameRe}': {files}")
            return render_template('blog.html', files=files, categories=categories)
    elif categories == None and name != None:
            outputFiles = []
            for p in posts:
                if re.search(re.escape(name), p["file"], re.IGNORECASE):
                    outputFiles.append(p)
            logging.info(f" Search results for '{name}': {outputFiles}")     
            return render_template('blog.html', name=name, files=outputFiles, categories='all')
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
                post_path = os.path.join(POSTS_DIR, f"{name}.MD")
                logging.info(f" Constructed post path: {post_path}")
                html = markdown.markdown(open(post_path).read(), extensions=['fenced_code', 'codehilite', 'tables', 'toc'])
            except FileNotFoundError:
                logging.error(f" FileNotFoundError: The file '{name}' in category '{categories}' was not found.")
                abort(404)

    return render_template('post.html', markdown=html)

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(debug=True)
