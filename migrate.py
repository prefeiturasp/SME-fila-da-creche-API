import psycopg2
import sys
import os
from tenacity import retry, wait_fixed

POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")

# wait to see if db is up, 5 seconds between retries
@retry(wait=wait_fixed(5))
def migrate():
    print("Migrating")
    try:
        con = psycopg2.connect(dbname=POSTGRES_DB, user=POSTGRES_USER, host=POSTGRES_HOST, password=POSTGRES_PASSWORD)
        cur = con.cursor()
        # cur.execute("DROP TABLE IF EXISTS solicitacao_matricula_grade_dw")
        cur.execute("""CREATE TABLE IF NOT EXISTS solicitacao_matricula_grade_dw(
        cd_solicitacao_matricula_random integer,
        cd_serie_ensino integer,
        cd_solicitacao_matricula_grade_distancia integer,
        cd_unidade_educacao integer,
        in_elegivel_compatibilizacao character varying(20),
        in_grade_ano_corrente character varying(20),
        in_grade_ano_seguinte character varying(20),
        qt_distancia integer
        )""")
        # cur.execute("DROP TABLE IF EXISTS solicitacao_matricula_grade_dw_atualizacao")
        cur.execute("""CREATE TABLE IF NOT EXISTS solicitacao_matricula_grade_dw_atualizacao(
        an_letivo integer,
        dt_solicitacao timestamp without time zone,
        dt_solicitacao_atual timestamp without time zone,
        dt_status_solicitacao timestamp without time zone
        )""")
        # cur.execute("DROP TABLE IF EXISTS unidades_educacionais_ativas_endereco_contato")
        cur.execute("""CREATE TABLE IF NOT EXISTS unidades_educacionais_ativas_endereco_contato(
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
        # cur.execute("DROP TABLE IF EXISTS unidades_educacionais_infantil_vagas_serie")
        cur.execute("""CREATE TABLE IF NOT EXISTS unidades_educacionais_infantil_vagas_serie(
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
        cur.execute("CREATE EXTENSION IF NOT EXISTS postgis")
        cur.execute("ALTER TABLE unidades_educacionais_ativas_endereco_contato ADD COLUMN IF NOT EXISTS geom geometry(Point, 4326)")
        cur.execute("""UPDATE unidades_educacionais_ativas_endereco_contato
        SET geom = ST_SetSrid(ST_MakePoint(cd_longitude, cd_latitude), 4326)
        WHERE geom IS NULL AND cd_longitude IS NOT NULL AND cd_latitude IS NOT NULL
        """)
        con.commit()
        con.close()
        print('Migrate successful')
    except Exception as e:
        if con:
            con.rollback()

        print('Error %s' % e)
        sys.exit(1)

    finally:
        if con:
            con.close()

migrate()
