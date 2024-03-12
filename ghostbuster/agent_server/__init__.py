import argparse
import logging
import os

from pid import PidFile
import waitress

from ghostbuster import default_data_dir
import ghostbuster.database as database
from ghostbuster.agent_server.agent_flask_server import app

pid_file = 'ghost-agent-server.pid'
process_name = 'ghost-agent-server'


def run():
    global pid_file


    # with PidFile(process_title, piddir=runtime_env.settings_runtime_directory) as p:
    #if developer_mode:
    #    app.run()
    #else:
    #    waitress.serve(app, listen='*:9111')
    parser = argparse.ArgumentParser()
    parser.add_argument('--root-dir', type=str, default=default_data_dir)
    parser.add_argument('--listen-address', type=str, default='127.0.0.1')
    parser.add_argument('--port', type=int, default=9900)


    # set high level logging
    logging.basicConfig(level=logging.INFO)

    args = parser.parse_args()

    settings_root_dir = args.root_dir
    # make root dir the current working directory
    os.chdir(settings_root_dir)
    pid_file = os.path.join(settings_root_dir, pid_file)

    with PidFile(process_name, piddir=settings_root_dir) as p:
        # create database now rather than when a page is requested
        database.get_conn()

        app.run(
            host=args.listen_address,
            port=args.port)


if __name__ == '__main__':
    run()
