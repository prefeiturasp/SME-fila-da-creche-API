# -*- coding: UTF-8 -*-

import os
from flask import Flask, jsonify, abort, request, url_for
from wrap_connection import transact
# from flask_httpauth import HTTPBasicAuth

#from geojson import Feature, Point, FeatureCollection

POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DBNAME = os.getenv("POSTGRES_DBNAME")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")

app = Flask(__name__, static_url_path = "")

# FIXME: limit when domain is defined
from flask_cors import CORS, cross_origin
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

# auth = HTTPBasicAuth()
# @auth.get_password
# def get_password(username):
#     if username == 'miguel':
#         return 'python'
#     return None
# @auth.error_handler
# def unauthorized():
#     return jsonify( { 'error': 'Unauthorized access' } ), 403
#     # return 403 instead of 401 to prevent browsers from displaying the default auth dialog

def connect():
    import psycopg2
    return psycopg2.connect(
        dbname = POSTGRES_DBNAME,
        user = POSTGRES_USER,
        host = POSTGRES_HOST,
        password = POSTGRES_PASSWORD
    )

def make_cursor(connection):
    import psycopg2
    return connection.cursor(cursor_factory = psycopg2.extras.RealDictCursor)

make_connection = { "db_connect" : connect, "cursor_factory": make_cursor }

# 2000 meters
searchRadius = 2000

@app.errorhandler(400)
def bad_request(error):
    return jsonify( { 'error': 'Bad request' } ), 400

@app.errorhandler(404)
def not_found(error):
    return jsonify( { 'error': 'Not found' } ), 404

@app.route('/', methods = ['GET'])
# @auth.login_required
def get_hello():
    return 'Hello World.'

@transact(**make_connection)
@app.route('/v1/schools/id/<int:cd_unidade_educacao>', methods = ['GET'])
# sample url
# http://localhost:8080/v1/schools/id/091383
# @auth.login_required
def get_school_id(cd_unidade_educacao):
    cursor.execute("SELECT * FROM unidades_educacionais_ativas_endereco_contato WHERE cd_unidade_educacao = %d", (cd_unidade_educacao,))
    return jsonify( { 'results': cursor.fetchall() } )

@transact(**make_connection)
@app.route('/v1/schools/radius/<float:lon>/<float:lat>', methods = ['GET'])
# sample url
# http://localhost:8080/v1/schools/radius/-46.677023599999984/-23.5814295
# @auth.login_required
def get_schoolradius(lat, lon):
    if not validate_coord(lat, lon):
        abort(422)
    cursor.execute("SELECT * FROM unidades_educacionais_ativas_endereco_contato WHERE ST_DWithin(geom::geography, ST_SetSRID(ST_MakePoint(%s, %s), 4326), %s)", (lon, lat, searchRadius))
    return jsonify( { 'results': cursor.fetchall() } )

@transact(**make_connection)
@app.route('/v1/schools/radius/wait/<float:lon>/<float:lat>/<int:cd_serie>', methods = ['GET'])
# sample url
# http://localhost:8080/v1/schools/radius/wait/-46.677023599999984/-23.5814295/27
# @auth.login_required
def get_schoolradiuswait(lat, lon, cd_serie):
    if cd_serie not in [1, 4, 27, 28] or not validate_coord(lat, lon):
        abort(422)
    # FIXME: validate by bouding box too

    sql1 = """
    SELECT *, (ST_Distance(geom::geography, ST_SetSRID(ST_MakePoint(%d, %d), 4326)) / 1000) AS distance
    FROM unidades_educacionais_ativas_endereco_contato AS u
    LEFT JOIN unidades_educacionais_infantil_vagas_serie AS v ON u.cd_unidade_educacao = v.cd_unidade_educacao
    WHERE ST_DWithin(geom::geography, ST_SetSRID(ST_MakePoint(%d, %d), 4326), %d)
    AND v.vagas_cd_serie_{cd_serie} IS NOT NULL
    ORDER BY distance
    """
    cursor.execute(sql1, (lon, lat, lon, lat, searchRadius))
    rowsSchools = cur.fetchall()

    sql2 = """
    SELECT COUNT(DISTINCT cd_solicitacao_matricula_random) AS cnt
    FROM unidades_educacionais_ativas_endereco_contato AS u
    LEFT JOIN solicitacao_matricula_grade_dw AS s ON u.cd_unidade_educacao::integer = s.cd_unidade_educacao
    WHERE ST_DWithin(geom::geography, ST_SetSRID(ST_MakePoint(%d, %d), 4326), %d)
      AND s.cd_serie_ensino = %d
    """
    cursor.execute(sql2, (lon, lat, seachRadius, cd_serie))
    rowsWait = cur.fetchone()

    sql3 = "SELECT dt_solicitacao AS updated_at FROM solicitacao_matricula_grade_dw_atualizacao"
    cursor.execute(sql3)
    rowsUpdated = cur.fetchone()

    results = {'wait': rowsWait['cnt'], 'wait_updated_at': rowsUpdated['updated_at'], 'schools': rowsSchools}
    return jsonify( { 'results': results } )

def validate_coord(lat, lon):
    return type(lat) in [int, float] and type(lon) in [int, float] and lat >= -90 and lat <= +90 and lon >= -180 and lon <= +180

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
