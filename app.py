from flask import Flask, redirect, url_for, render_template, send_file

app = Flask(__name__)
'''
for creating dyamic pages
@app.route('/home/<name>')
def create_app(name):
    return 'Hello %s!' % name
'''

'''
@app.route('/blog/<int:postID>')
def show_blog(postID):
    return 'Blog Number %d' % postID

@app.route('/rev/<float:revNo>')
def revision(revNo):
    return 'Reivsion Number %f' % revNo
'''
@app.route('/')
def hello_name():
    return render_template('home.html')

@app.route('/download')
def download_eddy():
    path = "eddy.txt"
    return  send_file(path, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)