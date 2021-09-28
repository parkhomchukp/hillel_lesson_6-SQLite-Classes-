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


@app.route('/customers')
@use_kwargs(
    {
        "first_name": fields.Str(
            required=False,
            missing=None,
            validate=[validate.Regexp('^[0-9]*')]
        ),
        "last_name": fields.Str(
            required=False,
            missing=None,
            validate=[validate.Regexp('^[0-9]*')]
        ),
    },
    location="query",
)
def get_customers(first_name, last_name):
    query = 'select * from customers'

    fields = {}
    if first_name:
        fields["FirstName"] = first_name

    if last_name:
        fields["LastName"] = last_name

    if fields:
        query += ' WHERE ' + ' AND '.join(f'{k}=?' for k in fields.items())

    records = execute_query(query, args=touple(fields.values()))
    result = format_records(records)
    return result


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


@app.route('/customers-2')
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
def get_customers_2(text):
    if text:
        query = db.execute_query(f"SELECT * FROM customers WHERE  FirstName LIKE '%{text}%' "
                                 f"OR LastName LIKE '%{text}%' OR Company LIKE '%{text}%' OR Address LIKE '%{text}%'"
                                 f"OR City LIKE '%{text}%' OR State LIKE '%{text}%' OR  Country LIKE '%{text}%'"
                                 f"OR Email LIKE '%{text}%'")
    else:
        query = db.execute_query("SELECT * FROM customers")
    result = utils.format_records(query)
    return result


@app.route('/genres_durations')
def get_genre_durations():
    query = (f"SELECT g.Name, t.Milliseconds / 1000 AS Duration "
             f"FROM genres g "
             f"INNER JOIN tracks t "
             f"ON g.GenreId = t.GenreId "
             f"GROUP BY g.Name "
             f"ORDER BY Duration DESC ")
    records = db.execute_query(query)
    result = '<br>'.join(f'Genre: "{rec[0]}", Duration: {rec[1]} minutes' for rec in records)
    return result


@app.route('/greatest_hits')
@use_kwargs(
    {
        'count': fields.Int(
            required=False,
            missing=99999999,
            validate=validate.Range(min=1)
        )
    },
    location='query',
)
def get_greatest_hits(count):
    query=f"SELECT t.Name, COUNT(ii.Quantity) as BuyingRate, COUNT(ii.TrackId) * ii.UnitPrice as TotalPrice " \
          f"FROM invoice_items ii " \
          f"INNER JOIN tracks t " \
          f"ON ii.TrackId = t.TrackId " \
          f"GROUP BY t.TrackId " \
          f"ORDER BY BuyingRate DESC " \
          f"LIMIT ?"
    records = db.execute_query(query, args=(count, ))
    result = '<br>'.join(f'Track name: {rec[0]}, Sold: {rec[1]}, Total amount: {rec[2]}' for rec in records)
    return result


app.run(debug=True)
