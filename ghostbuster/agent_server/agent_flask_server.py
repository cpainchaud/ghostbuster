import os

import flask
import logging
import ghostbuster.database as database
from ghostbuster.database.GhostAgent import GhostAgent, get_agents, get_agent_by_href, create_new_agent
from ghostbuster.database.GhostAgentWaitList import GhostAgentWaitListEntry, get_wait_list, get_wait_list_entry_by_href, create_or_increment_wait_list_entry

app = flask.Flask(__name__)

# flask default answer is 500
@app.errorhandler(500)
def server_error(e):
    return flask.jsonify({'error': 'internal server error'}), 500


@app.route('/api/v<api_version>/orgs/<org_id>/agents/<agent_id>/heartbeat', methods=['POST'])
def server_heartbeat(api_version, org_id, agent_id):
    #example curl request:
    #curl -X POST -H "Content-Type: application/json" -d '{"uptime": 10736}' http://localhost:9900/api/v1/orgs/1/agents/1/heartbeat

    conn = database.get_conn()
    href = f'/orgs/{org_id}/agents/{agent_id}'

    create_or_increment_wait_list_entry(conn, href)

    # is there an agent for this href?
    agent = get_agent_by_href(conn, href)
    if not agent:
        logging.error(f'agent does not exist: {href}')
        return flask.jsonify({'error': 'agent does not exist'}), 400

    json_payload = generate_agent_unpair_payload(int(agent_id))

    logging.info(f'heartbeat: {href}. Sent payload {json_payload}')
    return flask.jsonify(json_payload)


@app.route('/api/v<api_version>/orgs/<org_id>/agents/<agent_id>', methods=['GET', 'PUT', 'POST'])
def server_get_agent(api_version, org_id, agent_id):
    logging.info(f'agent "/" request: {org_id}/{agent_id}')
    return '', 204


@app.route('/api/v<api_version>/orgs/<org_id>/agents/<agent_id>/master_config', methods=['GET'])
def server_get_master_config(api_version, org_id, agent_id):
    # error 500 if agent_id is not an integer, or 0 or not in the ghost database
    href = f'/orgs/{org_id}/agents/{agent_id}'

    agent = get_agent_by_href(database.get_conn(), href)

    if not agent_id.isdigit() or agent is None and int(agent_id) != 0:
        return flask.jsonify({'error': 'agent does not exist or not supported'}), 400

    logging.info(f'agent "/master_config" request for {href}')


    # get url from current Host header
    api_url = f"{flask.request.headers.get('Host')}"

    # if api_url does not contain a port, add default port 443
    if ':' not in api_url:
        api_url = f"{api_url}:443"


    yaml_payload = generate_agent_master_config_payload(int(api_version), api_url, api_url)
    return yaml_payload, 200



def generate_agent_unpair_payload(agent_id: int):
    return {
        "clone_token": None,
        "commands": [
            {
                "action": "uninstall",
                "ip_table_restore": "open"
            }
        ],
        "id": agent_id,
        "uptime": 10736
    }

def generate_agent_master_config_payload(api_version: int, api_url: str, event_url: str) -> str:
    # we get payload template string from 'data/master_config_<api_version>.yml'
    this_script_parent_parent_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

    master_config_file = f'{this_script_parent_parent_path}/data/master_config_{api_version}.yml'

    with open(master_config_file, 'r') as f:
        payload = f.read()
        # replace placeholders with actual values
        payload = payload.replace('{api_url}', api_url)
        payload = payload.replace('{event_url}', event_url)


    return payload
