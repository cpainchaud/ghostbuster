import argparse
import os
from pid import PidFile
import waitress

import ghostbuster.database as database
from ghostbuster import default_data_dir
from ghostbuster.admin_server.admin_flask_server import app


pid_file = 'ghost-admin-server.pid'
process_name = 'ghost-admin-server'


def run():
    global pid_file

    parser = argparse.ArgumentParser()
    parser.add_argument('--root-dir', type=str, default=default_data_dir)
    parser.add_argument('--listen-address', type=str, default='127.0.0.1')
    parser.add_argument('--port', type=int, default=9901)

    args = parser.parse_args()

    settings_root_dir = args.root_dir
    # make root dir the current working directory
    os.chdir(settings_root_dir)
    pid_file = os.path.join(settings_root_dir, pid_file)


    with PidFile(process_name, piddir=settings_root_dir) as p:
        #if developer_mode:
        #    app.run()
        #else:
        #    waitress.serve(app, listen='*:9111')

        # create database now rather than when a page is requested
        database.get_conn()

        app.run(
            host=args.listen_address,
            port=args.port)


if __name__ == '__main__':
    run()


