# -*- coding: utf-8 -*-
# Copyright (c) 2018 by Ecreall and Bluenove under licence AGPL terms
# available on http://www.gnu.org/licenses/agpl.html
# licence: AGPL
# author: Amen Souissi

import io
import sqlite3
import hashlib
import urllib
import json
from flask import (
    Flask, request, render_template,
    jsonify, send_file, abort)
from flask_cors import CORS, cross_origin
from sqlite3 import OperationalError
from flask_graphql import GraphQLView

from utils import get_url_metadata, headers, add_url_metadata
from graphql_schema import schema

#Assuming urls.db is in your app root folder
app = Flask(__name__)

cors = CORS(app, resources={r"/": {"origins": "*"}, r"/graphql": {"origins": "*"}})

app.add_url_rule('/graphql', view_func=GraphQLView.as_view('graphql', schema=schema, graphiql=True))

DB_FILENAME = 'var/urls.db'


def table_check():
    create_table_query = """
        CREATE TABLE URL_METADATA(
        ID INTEGER PRIMARY KEY     AUTOINCREMENT,
        METADATA TEXT NOT NULL UNIQUE,
        URL  TEXT  NOT NULL UNIQUE
        );
        """
    create_pictures_table_query = """
        CREATE TABLE PICTURES(
        ID TEXT PRIMARY KEY,
        PICTURE BLOB
        );
        """
    with sqlite3.connect(DB_FILENAME) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(create_table_query)
        except OperationalError:
            pass

        try:
            cursor.execute(create_pictures_table_query)
        except OperationalError:
            pass


@app.route('/', methods=['GET', 'POST'])
@cross_origin(origin='localhost',headers=['Content-Type','Authorization'])
def home():
    is_get = request.method == 'GET'
    with sqlite3.connect(DB_FILENAME) as conn:
        try:
            cursor = conn.cursor()
            # get the requested URL
            url = request.args.get('url', None) if \
                is_get else request.form.get('url', None)
            if url:
                url_metadata = add_url_metadata(url, cursor)
                # return the result to the user
                if is_get:
                    return jsonify(**{'code': 'SUCCESS',
                                      'metadata': url_metadata})
                else:
                    return render_template(
                        'home.html', url_metadata=url_metadata)

            return render_template('home.html')
        except Exception as error:
            if is_get:
                return jsonify(**{'code': 'ERROR',
                                  'error': str(error),
                                  'url': url
                                  })
            else:
                return render_template(
                    'home.html',
                    error=True)


# A view to serve the images
@app.route('/picture/<picture_id>')
def picture(picture_id):
    with sqlite3.connect(DB_FILENAME) as conn:
        try:
            cursor = conn.cursor()
            exist_img_query = """
                SELECT PICTURE FROM PICTURES
                    WHERE ID='{img_id}'
                """.format(img_id=picture_id)
            result_cursor = cursor.execute(exist_img_query)
            result_fetch = result_cursor.fetchone()
            if result_fetch:
                return send_file(io.BytesIO(result_fetch[0]), mimetype='image')

            return abort(404)
        except Exception as error:
            return abort(404)


if __name__ == '__main__':
    # This code checks whether database table is created or not
    table_check()
    # app.run(debug=True)
    app.run(host='0.0.0.0')
