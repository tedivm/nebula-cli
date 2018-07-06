import click
import os
import re
import requests


@click.group()
@click.pass_context
def cli(ctx):
    if ctx.parent:
        click.echo(ctx.parent.get_help())


# Set Name
@cli.command(short_help="")
@click.argument('name')
@click.option('--instance_id', default=False)
def set_name(name, instance_id):
    if not instance_id:
        instance_id = get_instance_id()
    url = 'api/instances/%s/name' % instance_id
    results = api_call(url, post_data={'name':name})


# Set Status
@cli.command(short_help="")
@click.argument('status')
@click.option('--instance_id', default=False)
def set_status(status, instance_id):
    if not instance_id:
        instance_id = get_instance_id()
    url = 'api/instances/%s/status' % instance_id
    results = api_call(url, post_data={'status':status})


# Get User
@cli.command(short_help="")
@click.option('--instance_id', default=False)
def get_status(instance_id):
    if not instance_id:
        instance_id = get_instance_id()
    url = 'api/instances/%s/status' % instance_id
    results = api_call(url)
    click.echo(results['Status'])


# Get User
@cli.command(short_help="")
@click.option('--instance_id', default=False)
def get_user(instance_id):
    if not instance_id:
        instance_id = get_instance_id()
    url = 'api/instances/%s/user' % instance_id
    results = api_call(url)
    click.echo(results['User'])


# Get SSH Key
@cli.command(short_help="")
def get_ssh_key():
    pass



def api_call(route, post_data=False):
    url, id, token = get_authentication_token()
    full_url = "%s/%s" % (url, route)
    headers = {
        'User-Agent': 'nebula_cli',
        'id': id,
        'token': token
    }
    if post_data:
        r = requests.put(full_url, headers=headers, data=post_data)
    else:
        r = requests.get(full_url, headers=headers)
    r.raise_for_status()
    return r.json()


def get_authentication_token():
    config_string = load_config_from_path('%s/.nebulacli' % (os.getcwd()))
    if not config_string:
        config_string = load_config_from_path('%s/.nebulacli' % (os.path.expanduser('~')))
    if not config_string:
        config_string = load_config_from_path('/etc/nebula/nebulacli')
    if not config_string:
        raise RuntimeError('Unable to load configuration file.')

    token_pattern = r'^token=([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})$'
    token_match = re.search(token_pattern, config_string, flags=re.M)
    if not token_match:
        raise RuntimeError('Configuration file has no token.')
    token = token_match.group(1)

    token_id_match = re.search(r'^token_id=([0-9a-f]{12})$', config_string, flags=re.M)
    if not token_id_match:
        raise RuntimeError('Configuration file has no token_id.')
    token_id = token_id_match.group(1)

    install_url_match = re.search(r'^url=(.*)$', config_string, flags=re.M)
    if not install_url_match:
        raise RuntimeError('Configuration file has no URL.')
    install_url = install_url_match.group(1)

    return (install_url, token_id, token)


def load_config_from_path(file):
    try:
        with open(file) as fp:
            return fp.read()
    except IOError:
        return False


def get_instance_id():
    r = requests.get('http://169.254.169.254/latest/meta-data/instance-id')
    r.raise_for_status()
    return r.text


if __name__ == '__main__':
    cli()
