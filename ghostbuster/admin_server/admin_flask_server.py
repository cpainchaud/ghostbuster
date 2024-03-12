import re
from typing import Optional, Union, Literal

import flask

import ghostbuster.database as database
from ghostbuster.database.GhostAgent import GhostAgent, get_agents, get_agent_by_href, create_new_agent
from ghostbuster.database.GhostAgentWaitList import GhostAgentWaitListEntry, get_wait_list, get_wait_list_entry_by_href, create_or_increment_wait_list_entry

app = flask.Flask(__name__)

@app.route('/wait_list', methods=['GET'])
def server_get_wait_list():
    conn = database.get_conn()
    wait_list = get_wait_list(conn)
    return flask.jsonify(wait_list)

@app.route('/wait_list/ping', methods=['POST'])
def server_ping_wait_list():
    # example curl request:
    # curl -X POST -H "Content-Type: application/json" -d '{"href": "/orgs/1/agents/1"}' http://localhost:9901/wait_list/ping
    conn = database.get_conn()

    # href is provided in the request body
    href = flask.request.json['href']

    # check if the href is in the correct format
    check = check_agent_href_format(href)
    if check is not True:
        return flask.jsonify({'error': check}), 400

    create_or_increment_wait_list_entry(conn, href)
    return flask.jsonify({})

@app.route('/wait_list/ping_multi', methods=['POST'])
def server_ping_multi_wait_list():
    conn = database.get_conn()
    hrefs = flask.request.json['hrefs']

    return_list = []

    for href in hrefs:
        check = check_agent_href_format(href)
        if check is not True:
            return_list.append({'href': href,'error': check, 'success': False})
        else:
            create_or_increment_wait_list_entry(conn, href)
            return_list.append({'href': href, 'success': True})
            create_or_increment_wait_list_entry(conn, href)

    return flask.jsonify(return_list)

@app.route('/agents', methods=['GET'])
def server_get_agents():
    conn = database.get_conn()
    agents = get_agents(conn)
    return flask.jsonify(agents)

@app.route('/agents/create', methods=['POST'])
def server_create_agent():
    # example curl request:
    # curl -X POST -H "Content-Type: application/json" -d '{"href": "/orgs/1/agents/1"}' http://localhost:9901/agents/create
    conn = database.get_conn()
    href = flask.request.json['href']

    # does the agent already exist?
    agent = get_agent_by_href(conn, href)
    if agent:
        return flask.jsonify({'error': 'agent already exists'}), 400

    create_new_agent(conn, href)  # this function will also update the wait list

    return flask.jsonify({})


@app.route('/integrations/haproxy/generate_config', methods=['GET'])
def server_generate_haproxy_config():
    # example curl request:
    # curl -X GET http://localhost:9901/integrations/haproxy/generate_config?backend_profile=ghost

    # only argument required is the name of the backend profile
    backend_profile = flask.request.args.get('backend_profile')
    if not backend_profile:
        return flask.jsonify({'error': 'backend_profile is required'}), 400

    conn = database.get_conn()
    agents = get_agents(conn)

    # generate the haproxy config
    # each line is a regex match for the agent href and the server backend map file
    haproxy_config_map_file = ""
    for agent in agents:
        haproxy_config_map_file += f'    use_backend {backend_profile} if path_reg ^/api/v[0-9]+{agent["href"]}$\n'
        haproxy_config_map_file += f'    use_backend {backend_profile} if path_reg ^/api/v[0-9]+{agent["href"]}/\n'

    # return the config plain text
    return flask.Response(haproxy_config_map_file, mimetype='text/plain')




def check_agent_href_format(href: str) -> Union[Literal[True],str]:
    """
    Check if the href is in the correct format
    :param href:
    :return: True if correct, else a string with the error
    """
    # example href: /orgs/<org_id>/agents/<agent_id>
    # check with regex
    if not re.match(r'^/orgs/[0-9]+/agents/[0-9]+$', href):
        return f'href is not in the correct format ("^/orgs/[0-9]+/agents/[0-9]+$"): {href}'
    return True
