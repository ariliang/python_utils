from datetime import datetime, timedelta

import mysql.connector

from config import args
from config.mysql import db_config

from orm.wanbu_update import MedalTable
from utils.logger import get_logger

logger = get_logger(__name__, **args.log_config)


# truncate data
def truncate_answers():
    # 创建数据库连接
    conn = mysql.connector.connect(
        user=db_config.get('user'),
        password=db_config.get('password'),
        database=db_config.get('database'),
        port=db_config.get('port'))
    que_cur = conn.cursor()
    try:
        que_cur.execute('delete from questions')
        que_cur.execute('delete from questions_update')
        que_cur.execute('delete from answers')
        que_cur.execute('delete from answers_update')
        conn.commit()
    except Exception as e:
        logger.warning(f'truncate database failed, {e}')
        conn.rollback()
    conn.close()


# write test
def write_to_database(answers):
    # 创建数据库连接
    conn = mysql.connector.connect(
        host=db_config.get('host'),
        user=db_config.get('user'),
        password=db_config.get('password'),
        database=db_config.get('database'),
        port=db_config.get('port'))
    # 插入questions sql
    que_ins_sql = '''
        insert ignore into questions values(
            %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
    '''
    # 插入answers sql
    ans_ins_sql = '''
        insert ignore into answers values(
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
    '''
    # 插入的insert_cur
    insert_cur = conn.cursor()
    for ans in answers:
        try:
            insert_cur.execute(que_ins_sql, [
                    ans.get('question_id'),
                    ans.get('user_name'),
                    ans.get('question_desc'),
                    str(args.que_url + '/' + ans.get('question_id')),
                    ans.get('create_time'),
                    ans.get('visit_time'),
                    ans.get('bounty'),
                    ans.get('views'),
                    ans.get('answer_count')
            ])
        except Exception as e:
            logger.warning('questions_id={}; a question is failed to write to database, {}'.format(ans.get('questions_id'), e))
            with open(args.failed_file, 'r+') as f:
                old = f.read()
                f.seek(0)
                f.truncate()
                f.write('{}\t{}\n'.format(ans.get('question_id'), datetime.now().strftime(args.datefmt)))
                f.write(old)
                f.close()
            continue
        for ans_item in ans.get('answer_list'):
            try:
                insert_cur.execute(ans_ins_sql, [
                    ans.get('question_id'),
                    ans_item.get('user_id'),
                    ans_item.get('user_name'),
                    ans_item.get('tech_title'),
                    ans_item.get('dept'),
                    ans_item.get('hospital'),
                    args.doc_url + '/' + ans_item.get('user_id'),
                    ans_item.get('answer'),
                    ans_item.get('answer_time'),
                    ans_item.get('visit_time'),
                    ans_item.get('thumb'),
                    ans_item.get('award'),
                    ans_item.get('seq')
                ])
            except Exception as e:
                logger.warning('questions_id={}, user_id={}; an answer is failed to write to database, {}'.format(
                    ans.get('questions_id'), ans_item.get('user_id'), e)
                )
                continue
    insert_cur.close()

    try:
        conn.commit()
    except Exception as e:
        logger.warning(f'conn commit failed, {e}')
        conn.rollback()
    conn.close()


# query on condition
def quesition_id_since(days):
    # 创建数据库连接
    conn = mysql.connector.connect(
        host=db_config.get('host'),
        user=db_config.get('user'),
        password=db_config.get('password'),
        database=db_config.get('database'),
        port=db_config.get('port'))

    from_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')

    res_cur = conn.cursor(buffered=True)
    try:
        res_cur.execute('select question_id from questions where visit_time > %s', [from_date])
    except Exception as e:
        logger.warning(f'query id failed, {e}')
        return

    res_temp = res_cur.fetchall()
    results = []
    for res in res_temp:
        results.append(res[0])

    res_cur.close()
    conn.close()

    return results


# update record on condition
def update_views(views):
    # 创建数据库连接
    conn = mysql.connector.connect(
        host=db_config.get('host'),
        user=db_config.get('user'),
        password=db_config.get('password'),
        database=db_config.get('database'),
        port=db_config.get('port'))

    res_cur = conn.cursor(buffered=True)
    for question_id, view in views:
        try:
            res_cur.execute('select rev, views from questions_update where question_id = %s order by rev+0 desc limit 1', [question_id])

            if ret := res_cur.fetchone():
                rev, view_old = ret

                if (view - 10) > view_old:
                    rev += 1
                else:
                    continue
            else:
                rev = 1

            res_cur.execute('insert into questions_update values(%s, %s, %s, %s)', [question_id, rev, datetime.now().strftime(args.datefmt), view])
        except Exception as e:
            logger.warning(f'q_id={question_id}; update views failed, {e}')
            continue

    res_cur.close()

    try:
        conn.commit()
    except Exception as e:
        logger.warning(f'update views failed, {e}')
        conn.rollback()
    finally:
        conn.close()


# fetch one by one
def update_ans_count():
    file_path = args.update_ans_count_file
    update_sql = '''
        update questions set ans_count = %s where question_id = %s
    '''.strip()
    query_sql = ''

    with open(file_path, 'r') as f:
        query_sql = f.read()
        f.close()

    # 创建数据库连接
    conn = mysql.connector.connect(
        host=db_config.get('host'),
        user=db_config.get('user'),
        password=db_config.get('password'),
        database=db_config.get('database'),
        port=db_config.get('port'))

    res_cur = conn.cursor(buffered=True)
    update_cur = conn.cursor(buffered=True)

    res_cur.execute(query_sql)
    while (row := res_cur.fetchone()):
        question_id = row[0]
        ans_count_real = int(row[4])
        update_cur.execute(update_sql, (ans_count_real, question_id))

    update_cur.close()
    res_cur.close()
    try:
        conn.commit()
    except Exception as e:
        logger.error(f'update answer count failed, {e}')
        conn.rollback()
    finally:
        conn.close()
