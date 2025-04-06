from flask import Flask, request, jsonify
# from server_file import key
key = 123

app = Flask(__name__)
PORT = 8080
# expense
#     amt
#     date
#     cat sub cat
#     descr
expense = []
total_expense = 0
parametes = ['user_id', 'key', 'id', 'amt', 'date', 'cat', 'sub_cat', 'descr']

@app.route('/New_transaction', methods=['POST'])
def add_new():
        # for i in ['user_id', 'key', 'amt', 'date', 'cat', 'sub_cat', 'descr']:
        #     if i not in request.():
        #         return '401 All parameters not given. required parameters - amt, date, cat, subcat, descr'
        # if request.json().get['key'] != key:
        #     return '403 Permission Denied'
        print(request.json)
        new_trans = {
            'id' : len(expense),
            'amt' : request.query.get['amt'],
            'date' : request.query.get['date'],
            'cat' : request.query.get['cat'],
            'sub_cat' : request.query.get['sub_cat'],
            'descr' : request.query.get['descr'],
        }
        expense.append(new_trans)
        total_expense+=new_trans['amt']
        return '201 OK'

@app.route('/all_transactions', methods=['GET'])
def all_transactions():
    global total_expense
    # if ['user_id', 'key'] not in request.json():
    #     return '401 Key Required'
    # if request.json().get['key'] != key:
    #         return '403 Permission Denied'
    return expense


@app.route('/Update_transaction', methods=['POST'])
def update():
    try:
        for i in parametes:
            if i not in request.data.keys():
                return '401 All parameters not given. required parameters - id, amt, date, cat, subcat, descr'

        # Fetching the new id and data
        trans = {
            'id' : request.json().get['id'],
            'amt' : request.json().get['amt'],
            'date' : request.json().get['date'],
            'cat' : request.json().get['cat'],
            'sub_cat' : request.json().get['sub_cat'],
            'descr' : request.json().get['descr'],
        }

        requested_trans = trans
        original_trans = expense[trans['id']]
        # Comparing to see any data mismatch
        for i in requested_trans:
            if requested_trans[i]!=original_trans[i]:
                return '403 Data mismatch'

        total_expense -= original_trans['amt']
        total_expense += requested_trans['amt']

        expense[trans['id']] = trans
        return '202 Updated'
    except:
        return '500 Internal Server Error'

@app.route('/remove_transaction/<id>', methods=['POST'])
def del_trans(id):
    try:
        total_expense -= expense[id]['amt']
        expense.pop(id)
        return '202 Updated'
    except:
        return '500 Internal Server Error'


if __name__ == '__main__':
    app.run('0.0.0.0', port=PORT)
