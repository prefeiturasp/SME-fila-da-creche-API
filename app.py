# -*- coding: UTF-8 -*-

import os

import psycopg2
from flask import Flask, jsonify, abort, make_response
from flask_cors import CORS
from psycopg2.extras import RealDictCursor
from tenacity import retry, wait_fixed

POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")

app = Flask(__name__, static_url_path="")

# FIXME: limit when domain is defined
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


# wait to see if db is up, 5 seconds between retries
@retry(wait=wait_fixed(5))
def init_api():
    try:
        con = psycopg2.connect(dbname=POSTGRES_DB, user=POSTGRES_USER, host=POSTGRES_HOST,
                               password=POSTGRES_PASSWORD, port=POSTGRES_PORT)
        con.set_session(autocommit=True)
    except Exception as e:
        print("I am unable to connect to the database.")
        print(e)
        abort(400)

    cur = con.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    # 2000 meters
    searchRadius = 2000

    @app.errorhandler(400)
    def not_found(error):
        return make_response(jsonify({'error': 'Bad request'}), 400)

    @app.errorhandler(404)
    def not_found(error):
        return make_response(jsonify({'error': 'Not found'}), 404)

    @app.route('/', methods=['GET'])
    # @auth.login_required
    def get_hello():
        return 'Hello World.'

    @app.route('/v1/schools/id/<string:cd_unidade_educacao>', methods=['GET'])
    # sample url
    # http://localhost:8080/v1/schools/id/091383
    # @auth.login_required
    def get_school_id(cd_unidade_educacao):
        try:
            if validate_school_id_request(cd_unidade_educacao):
                cur.execute(f"""
                SELECT *
                FROM unidades_educacionais_ativas_endereco_contato
                WHERE cd_unidade_educacao = '{cd_unidade_educacao}'
                """)
                schools = cur.fetchall()
                return jsonify({'results': schools})
            else:
                abort(400)
        except Exception as e:
            print(e)
            abort(400)

    @app.route('/v1/schools/radius/<string:lon>/<string:lat>', methods=['GET'])
    # sample url
    # http://localhost:8080/v1/schools/radius/-46.677023599999984/-23.5814295
    # @auth.login_required
    def get_schoolradius(lat, lon):
        try:
            if validate_wait_request(lat, lon):
                cur.execute(f"""SELECT *
                FROM unidades_educacionais_ativas_endereco_contato
                WHERE ST_DWithin(geom::geography, ST_SetSRID(ST_MakePoint({lon}, {lat}), 4326), {searchRadius})
                """)
                rowsSchools = cur.fetchall()
                return jsonify({'results': rowsSchools})
            else:
                abort(400)
        except Exception as e:
            print(e)
            abort(400)

    @app.route('/v1/schools/radius/wait/<string:lon>/<string:lat>/<int:cd_serie>', methods=['GET'])
    # sample url
    # http://localhost:8080/v1/schools/radius/wait/-46.677023599999984/-23.5814295/27
    # @auth.login_required
    def get_schoolradiuswait(lat, lon, cd_serie):
        try:
            # FIXME: validate by bouding box too
            if validate_wait_request(lat, lon, cd_serie):
                if cd_serie in [1, 4]:
                    raio_busca = 1500
                elif cd_serie in [27, 28]:
                    raio_busca = 2000
                cur.execute(f"""
                SELECT *, (ST_Distance(geom::geography, ST_SetSRID(ST_MakePoint({lon}, {lat}), 4326)) / 1000) as distance FROM unidades_educacionais_ativas_endereco_contato AS u
                LEFT JOIN unidades_educacionais_infantil_vagas_serie as v
                ON u.cd_unidade_educacao = v.cd_unidade_educacao
                WHERE ST_DWithin(geom::geography, ST_SetSRID(ST_MakePoint({lon}, {lat}), 4326), {raio_busca})
                  AND v.vagas_cd_serie_{cd_serie} IS NOT NULL
                ORDER BY distance
                """)
                rowsSchools = cur.fetchall()
                cur.execute(f"""
                SELECT count(DISTINCT cd_solicitacao_matricula_random)
                FROM unidades_educacionais_ativas_endereco_contato AS u
                LEFT JOIN solicitacao_matricula_grade_dw AS s
                ON u.cd_unidade_educacao::integer = s.cd_unidade_educacao
                WHERE ST_DWithin(geom::geography, ST_SetSRID(ST_MakePoint({lon}, {lat}), 4326), {raio_busca})
                  AND s.cd_serie_ensino = {cd_serie}
                """)
                rowsWait = cur.fetchall()
                cur.execute(f"""
                SELECT dt_solicitacao as updated_at
                FROM solicitacao_matricula_grade_dw_atualizacao
                """)
                rowsUpdated = cur.fetchall()
                results = {'wait': rowsWait[0]['count'], 'wait_updated_at': rowsUpdated[0]['updated_at'],
                           'schools': rowsSchools}
                return jsonify({'results': results})
            else:
                abort(400)
        except Exception as e:
            print(e)
            abort(400)

    def validate_wait_request(lat, lon, cd_serie=1):
        if float(lat) and float(lon) and (cd_serie in [1, 4, 27, 28]):
            return True
        else:
            return False

    def validate_school_id_request(id):
        if float(id):
            return True
        else:
            return False


init_api()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
