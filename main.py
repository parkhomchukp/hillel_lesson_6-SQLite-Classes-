from flask import Flask, jsonify
from webargs import fields
from marshmallow import validate
from webargs.flaskparser import use_kwargs

import db
import utils

app = Flask(__name__)


@app.errorhandler(422)
@app.errorhandler(400)
def handle_error(err):
    headers = err.data.get("headers", None)
    messages = err.data.get("messages", ["Invalid request."])
    if headers:
        return jsonify({"errors": messages}), err.code, headers
    else:
        return jsonify({"errors": messages}), err.code


@app.route('/')
def home():
    return 'SUCCESS'


# @app.route('/customers')
# @use_kwargs(
#     {
#         "first_name": fields.Str(
#             required=False,
#             missing=None,
#             validate=[validate.Regexp('^[0-9]*')]
#         ),
#         "last_name": fields.Str(
#             required=False,
#             missing=None,
#             validate=[validate.Regexp('^[0-9]*')]
#         ),
#     },
#     location="query",
# )
# def get_customers(first_name, last_name):
#     query = 'select * from customers'
#
#     fields = {}
#     if first_name:
#         fields["FirstName"] = first_name
#
#     if last_name:
#         fields["LastName"] = last_name
#
#     if fields:
#         query += ' WHERE ' + ' AND '.join(f'{k}="{v}"' for k, v in fields.items())
#
#     records = execute_query(query)
#     result = format_records(records)
#     return result


@app.route('/unique_names')
def get_unique_names():
    query = 'SELECT FirstName FROM customers'
    records = db.execute_query(query)
    unique_names = list()
    for name in records:
        if name not in unique_names:
            unique_names.append(name)
    result = str(len(unique_names))
    return result


@app.route('/tracks_count')
def get_tracks_count():
    query = 'SELECT COUNT(*) FROM tracks'
    records = db.execute_query(query)
    result = str(records[0][0])
    return result


@app.route('/customers')
@use_kwargs(
    {
        'text': fields.Str(
            required=False,
            missing=None,
            validate=validate.Regexp('^[a-zA-Z]+$')
        )
    },
    location='query',
)
def get_customers(text):
    if text:
        query = db.execute_query(f"SELECT * FROM customers WHERE  FirstName LIKE '%{text}%' "
                                 f"OR LastName LIKE '%{text}%' OR Company LIKE '%{text}%' OR Address LIKE '%{text}%'"
                                 f"OR City LIKE '%{text}%' OR State LIKE '%{text}%' OR  Country LIKE '%{text}%'"
                                 f"OR Email LIKE '%{text}%'")
    else:
        query = db.execute_query("SELECT * FROM customers")
    result = utils.format_records(query)
    return result


app.run(debug=True)
