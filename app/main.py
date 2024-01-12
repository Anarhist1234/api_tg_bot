import uvicorn
from fastapi import FastAPI
from db import PgDriver

app = FastAPI(docs_url='/docs', openapi_url='/openapi.json')


with PgDriver() as curr:
    curr.execute("""
	                with projects_count as (
	                    select count(phone) as count, pr.id, pr.name from phones ph
	                    left join projects pr on ph.project_id = pr.id
	                    where pr.is_active = true and ph.used = false
	                    group by pr.id, pr.name
	                ),
	                projects_count_users as (
	                    select pc.count, pc.id, pc.name, count(u.id) as active_users_count from projects_count pc
	                    left join project_user pu on pu.project_id = pc.id
	                    left join users u on u.id = pu.user_id
	                    where u.status != 'OFFLINE'
	                    group by pc.id, pc.name, pc.count
	                )
	                select * from projects_count_users
	                where active_users_count > 0
	                """)
    result = curr.fetchall()


@app.get("/info_phones")
def get_info_phones():
    return result

def get_statistic_avg_sec_for_each_lead(date_from, date_to):
    with PgDriver() as curr:
        curr.execute("""
                                     WITH lead_table AS(
                        SELECT sh.user_id,
                           sh.created_at,
                           LEAD(sh.created_at) OVER (partition by user_id order by created_at) as ldt
                        FROM statuses_histories as sh
                        WHERE type = 'READY' AND sh.created_at BETWEEN %s and %s 
                        ),
                        
                        avg_sec AS (
                        SELECT ld.user_id,
                            ld.created_at::date,
                            ld.ldt,
                            ROUND(EXTRACT(SECONDS FROM ld.ldt - ld.created_at),2) as dif_sec
                            FROM lead_table as ld
                            WHERE ld.ldt is not null
                        ),
                        
                        avg_for_each_day AS (
                        SELECT avs.user_id, avs.created_at, ROUND(AVG(avs.dif_sec),2) as avg_total
                        FROM avg_sec as avs
                        GROUP BY avs.created_at, avs.user_id
                        
                        )
                        SELECT * FROM avg_for_each_day 
                     """, (date_from, date_to,))
        result1 = curr.fetchall()
        return result1


@app.get("/avg_sec_in_status_ready_for_each_user")
def get_avg_sec_in_ready(date_from: str, date_to: str):
    result = get_statistic_avg_sec_for_each_lead(date_from, date_to)
    print(result)
    return result


def get_conversion_all_filt(project_id, date_from, date_to, user_id):
    with PgDriver() as curr:
        curr.execute("""
                    with a as (
                select
                    count(*) filter ( where (lead_status = 'Не удалось перевести' or lead_status = 'Записан на ВУ' or lead_status = 'Лид переведен в САМОЛЕТ' or lead_status = 'Передано в А101' or lead_status = 'Лид для ОП') ) as lead,
                    count(*) filter ( where lead_status is not null ) as all_c
                from calls as c
                where
                    (project_id = %s)  and
                    (c.created_at BETWEEN %s and %s)  and
                    (user_id is not null and user_id = %s))
                select (cast(lead as decimal(7, 2)) / cast(greatest(all_c, 1) as decimal(7,2))) * 100 as percentage from a""", (project_id, date_from, date_to, user_id,))
        result1 = curr.fetchall()
        return result1

def get_conversion_without_usr_proj(date_from, date_to):
    with PgDriver() as curr:
        curr.execute("""
                    with a as (
                select
                    count(*) filter ( where (lead_status = 'Не удалось перевести' or lead_status = 'Записан на ВУ' or lead_status = 'Лид переведен в САМОЛЕТ' or lead_status = 'Передано в А101' or lead_status = 'Лид для ОП') ) as lead,
                    count(*) filter ( where lead_status is not null ) as all_c
                from calls as c
                where
                    c.created_at BETWEEN %s and %s)
                select (cast(lead as decimal(7, 2)) / cast(greatest(all_c, 1) as decimal(7,2))) * 100 as percentage from a""", (date_from, date_to,))
        result1 = curr.fetchall()
        return result1

def get_conversion_without_usr(project_id, date_from, date_to):
    with PgDriver() as curr:
        curr.execute("""
                    with a as (
                select
                    count(*) filter ( where (lead_status = 'Не удалось перевести' or lead_status = 'Записан на ВУ' or lead_status = 'Лид переведен в САМОЛЕТ' or lead_status = 'Передано в А101' or lead_status = 'Лид для ОП') ) as lead,
                    count(*) filter ( where lead_status is not null ) as all_c
                from calls as c
                where
                    project_id = %s  and
                    c.created_at BETWEEN %s and %s)
                select (cast(lead as decimal(7, 2)) / cast(greatest(all_c, 1) as decimal(7,2))) * 100 as percentage from a""", (project_id, date_from, date_to,))
        result1 = curr.fetchall()
        return result1


def get_conversion_without_proj(date_from, date_to, user_id):
    with PgDriver() as curr:
        curr.execute("""
                    with a as (
                select
                    count(*) filter ( where (lead_status = 'Не удалось перевести' or lead_status = 'Записан на ВУ' or lead_status = 'Лид переведен в САМОЛЕТ' or lead_status = 'Передано в А101' or lead_status = 'Лид для ОП') ) as lead,
                    count(*) filter ( where lead_status is not null ) as all_c
                from calls as c
                where
                    (c.created_at BETWEEN %s and %s) and
                    (user_id is not null and user_id = %s))
                select (cast(lead as decimal(7, 2)) / cast(greatest(all_c, 1) as decimal(7,2))) * 100 as percentage from a""", (date_from, date_to, user_id,))
        result1 = curr.fetchall()
        return result1


@app.get("/conversion")
def get_conversion_in_perc(date_from: str, date_to: str, user_id: int | None = None, project_id: int | None = None):
    if user_id == None and project_id == None:
        result = get_conversion_without_usr_proj(date_from, date_to)
        return result
    elif user_id == None:
        result = get_conversion_without_usr(project_id, date_from, date_to)
        return result
    elif project_id == None:
        result = get_conversion_without_proj(date_from, date_to, user_id)
        return result
    else:
        result = get_conversion_all_filt(project_id, date_from, date_to, user_id)
        print(result)
        return result


def get_lost_calls_all_filt(project_id, date_from, date_to):
    with PgDriver() as curr:
        curr.execute("""
                                with count as (
                select
                    count(*) filter ( where user_id is null and dial_status = 'ANSWER' ) as count_without_user_and_outbound,
                    count(*) filter ( where (dial_status = 'ANSWER') and user_id is not null ) as count_all_without_outbound,
                    count(*) filter ( where user_id is null and (dial_status = 'OUTBOUND_CALL' or dial_status = 'ANSWER') ) as count_without_user,
                    count(*) filter ( where (dial_status = 'OUTBOUND_CALL' or dial_status = 'ANSWER') ) as count_all_with_outbound
                from calls as c
                where
                    project_id = %s and c.created_at BETWEEN %s and %s 
            )
            select
                (cast(count_without_user_and_outbound as decimal(7, 2)) / cast(greatest(count_all_without_outbound, 1) as decimal(7,2))) * 100 as percent_without_outbound,
                (cast(count_without_user as decimal(7, 2)) / cast(greatest(count_all_with_outbound, 1) as decimal(7,2))) * 100 as percent_with_outbound,
                *
                from count;""", (project_id, date_from, date_to,))
        result1 = curr.fetchall()
        return result1


def get_lost_calls_without_proj_id(date_from, date_to):
    with PgDriver() as curr:
        curr.execute("""
                                with count as (
                select
                    count(*) filter ( where user_id is null and dial_status = 'ANSWER' ) as count_without_user_and_outbound,
                    count(*) filter ( where (dial_status = 'ANSWER') and user_id is not null ) as count_all_without_outbound,
                    count(*) filter ( where user_id is null and (dial_status = 'OUTBOUND_CALL' or dial_status = 'ANSWER') ) as count_without_user,
                    count(*) filter ( where (dial_status = 'OUTBOUND_CALL' or dial_status = 'ANSWER') ) as count_all_with_outbound
                from calls as c
                where
                    c.created_at BETWEEN %s and %s 
            )
            select
                (cast(count_without_user_and_outbound as decimal(7, 2)) / cast(greatest(count_all_without_outbound, 1) as decimal(7,2))) * 100 as percent_without_outbound,
                (cast(count_without_user as decimal(7, 2)) / cast(greatest(count_all_with_outbound, 1) as decimal(7,2))) * 100 as percent_with_outbound,
                *
                from count;""", (date_from, date_to,))
        result1 = curr.fetchall()
        return result1


@app.get("/count_lost_calls")
def get_lost_calls_for_project_id(date_from: str, date_to: str, project_id: int | None = None):
    if project_id is None:
        result = get_lost_calls_without_proj_id(date_from, date_to)
        return result
    result = get_lost_calls_all_filt(project_id, date_from, date_to)
    print(result)
    return result




if __name__ == "__main__":
    uvicorn.run('main:app', host="127.0.0.1", workers=1, port=8000)











