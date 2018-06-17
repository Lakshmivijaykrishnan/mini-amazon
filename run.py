from flask import Flask, request

app =Flask('Amazon')

# http://127.0.0.1:5005/say_hello?name=Sunil
@app.route('/say_hello', methods=['GET', 'POST'])
def say_hello():
    if request.method == 'GET':
        return '[GET] Hello '+ request.args['name']
    elif request.method == 'POST':
        return 'hii '+ request.form['name'] + ' your age is ' +request.form['age']


if __name__=='__main__':
    app.run(host='127.0.0.1',port=5005)