from datetime import datetime
from typing import TypedDict, Optional
import sqlite3
from .GhostAgentWaitList import set_wait_list_has_an_agent


class GhostAgent(TypedDict):
    href: str
    created_at: str
    updated_at: str
    stat_total_hits: int

table_name = 'GhostAgent'

def sql_row_to_ghost_agent(row: sqlite3.Row) -> GhostAgent:
    return {
        'href': row['href'],
        'created_at': row['created_at'],
        'updated_at': row['updated_at'],
        'stat_total_hits': row['stat_total_hits']
    }


def get_agents(conn: sqlite3.Connection) -> list[GhostAgent]:
    cursor = conn.cursor()
    cursor.execute(f'SELECT * FROM {table_name}')
    agents = cursor.fetchall()
    return [sql_row_to_ghost_agent(agent) for agent in agents]

def get_agent_by_href(conn: sqlite3.Connection, href: str) -> Optional[GhostAgent]:
    cursor = conn.cursor()
    cursor.execute(f'SELECT * FROM {table_name} WHERE href = ?', (href,))
    agent = cursor.fetchone()
    if agent:
        return sql_row_to_ghost_agent(agent)
    return None

def create_new_agent(conn: sqlite3.Connection, href: str):
    cursor = conn.cursor()
    cursor.execute(f'INSERT INTO {table_name} (href, created_at, updated_at ) VALUES (?,?,?)',
                   (href, datetime.now(), datetime.now())
                )
    set_wait_list_has_an_agent(conn, href, True)
    return