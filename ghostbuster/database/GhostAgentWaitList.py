import sqlite3
from datetime import datetime
from typing import TypedDict, Optional

from ghostbuster.database import datetime_format_now


class GhostAgentWaitListEntry(TypedDict):
    href: str
    created_at: str
    last_seen_at: str
    stat_total_hits: int
    has_an_agent: bool

table_name = 'GhostAgentWaitListEntry'

def sql_row_to_ghost_agent_wait_list_entry(row: sqlite3.Row) -> GhostAgentWaitListEntry:
    return {
        'href': row['href'],
        'created_at': row['created_at'],
        'last_seen_at': row['last_seen_at'],
        'stat_total_hits': row['stat_total_hits'],
        'has_an_agent': row['has_an_agent']
    }


def get_wait_list(conn: sqlite3.Connection) -> list[GhostAgentWaitListEntry]:
    # ordered by last_seen_at
    cursor = conn.cursor()
    cursor.execute(f'SELECT * FROM {table_name} ORDER BY last_seen_at DESC')
    agents = cursor.fetchall()
    return [sql_row_to_ghost_agent_wait_list_entry(agent) for agent in agents]

def get_wait_list_entry_by_href(conn: sqlite3.Connection, href: str) -> Optional[GhostAgentWaitListEntry]:
    cursor = conn.cursor()
    cursor.execute(f'SELECT * FROM {table_name} WHERE href = ?', (href,))
    agent = cursor.fetchone()
    if agent:
        return sql_row_to_ghost_agent_wait_list_entry(agent)

    return None

def create_or_increment_wait_list_entry(conn: sqlite3.Connection, href: str):
    print(f'create_or_increment_wait_list_entry: {href}')
    cursor = conn.cursor()
    cursor.execute(f'SELECT * FROM {table_name} WHERE href = ?', (href,))
    agent = cursor.fetchone()
    if agent:
        cursor.execute(f'UPDATE {table_name} SET last_seen_at = ?, stat_total_hits = stat_total_hits + 1 WHERE href = ?',
                       (datetime_format_now(), href)
                    )
    else:
        cursor.execute(f'INSERT INTO {table_name} (href, created_at, last_seen_at) VALUES (?,?,?)',
                       (href, datetime_format_now(), datetime_format_now())
                    )
    conn.commit()

def set_wait_list_has_an_agent(conn: sqlite3.Connection, href: str, has_an_agent: bool):
    cursor = conn.cursor()
    cursor.execute(f'UPDATE {table_name} SET has_an_agent = ? WHERE href = ?', (has_an_agent, href))
    conn.commit()
    return


