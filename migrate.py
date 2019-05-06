import psycopg2
import sys
import os
from wrap_connection import transact

POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DBNAME = os.getenv("POSTGRES_DBNAME")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")

def connect():
    import psycopg2
    return psycopg2.connect(
        dbname = POSTGRES_DBNAME,
        user = POSTGRES_USER,
        host = POSTGRES_HOST,
        password = POSTGRES_PASSWORD
    )

# wait to see if db is up, 5 seconds between retries
@transact(connect)
def migrate():
    print("Migrating")
    con = psycopg2.connect(dbname=POSTGRES_DBNAME, user=POSTGRES_USER, host=POSTGRES_HOST, password=POSTGRES_PASSWORD)
    cursor = con.cursor()
    # cursor.execute("DROP TABLE IF EXISTS solicitacao_matricula_grade_dw")
    cursor.execute("""CREATE TABLE IF NOT EXISTS solicitacao_matricula_grade_dw(
    cd_solicitacao_matricula_random integer,
    cd_serie_ensino integer,
    cd_solicitacao_matricula_grade_distancia integer,
    cd_unidade_educacao integer,
    in_elegivel_compatibilizacao character varying(20),
    in_grade_ano_corrente character varying(20),
    in_grade_ano_seguinte character varying(20),
    qt_distancia integer
    )""")
    # cursor.execute("DROP TABLE IF EXISTS solicitacao_matricula_grade_dw_atualizacao")
    cursor.execute("""CREATE TABLE IF NOT EXISTS solicitacao_matricula_grade_dw_atualizacao(
    an_letivo integer,
    dt_solicitacao timestamp without time zone,
    dt_solicitacao_atual timestamp without time zone,
    dt_status_solicitacao timestamp without time zone
    )""")
    # cursor.execute("DROP TABLE IF EXISTS unidades_educacionais_ativas_endereco_contato")
    cursor.execute("""CREATE TABLE IF NOT EXISTS unidades_educacionais_ativas_endereco_contato(
    cd_unidade_educacao character varying(60),
    nm_exibicao_unidade_educacao character varying(255),
    nm_unidade_educacao character varying(255),
    tp_escola integer,
    sg_tp_escola character varying(60),
    cd_latitude float,
    cd_longitude float,
    endereco_completo character varying(255),
    telefones character varying(60)[],
    sg_tipo_situacao_unidade character varying(60)
    )""")
    # cursor.execute("DROP TABLE IF EXISTS unidades_educacionais_infantil_vagas_serie")
    cursor.execute("""CREATE TABLE IF NOT EXISTS unidades_educacionais_infantil_vagas_serie(
    cd_unidade_educacao character varying(60),
    nm_exibicao_unidade_educacao character varying(255),
    nm_unidade_educacao character varying(255),
    tp_escola integer,
    sg_tp_escola character varying(60),
    vagas_cd_serie_1 integer,
    vagas_cd_serie_4 integer,
    vagas_cd_serie_27 integer,
    vagas_cd_serie_28 integer,
    sg_tipo_situacao_unidade character varying(60)
    )""")
    cursor.execute("CREATE EXTENSION IF NOT EXISTS postgis")
    cursor.execute("ALTER TABLE unidades_educacionais_ativas_endereco_contato ADD COLUMN IF NOT EXISTS geom geometry(Point, 4326)")
    cursor.execute("""UPDATE unidades_educacionais_ativas_endereco_contato
    SET geom = ST_SetSrid(ST_MakePoint(cd_longitude, cd_latitude), 4326)
    WHERE geom IS NULL AND cd_longitude IS NOT NULL AND cd_latitude IS NOT NULL
    """)
    connection.commit()
    print('Migrate successful')

migrate()
