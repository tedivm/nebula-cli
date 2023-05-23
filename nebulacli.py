import click
import os
import re
import requests
import shutil
import subprocess
import time


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
    results = api_call(url, put_data={'name':name})


# Set Status
@cli.command(short_help="")
@click.argument('status')
@click.option('--instance_id', default=False)
def set_status(status, instance_id):
    if not instance_id:
        instance_id = get_instance_id()
    url = 'api/instances/%s/status' % instance_id
    results = api_call(url, put_data={'status':status})


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


@cli.command(short_help="")
def gpu_utilization():
    utilization = get_gpu_utilization()
    if utilization is False:
        click.echo('No GPUs detected.')
        return
    click.echo(utilization)


@cli.command(short_help="")
def disk_utilization():
    click.echo(get_disk_utilization())


@cli.command(short_help="Sends statistics, such as GPU Utilization, to Nebula")
@click.option('--instance_id', default=False)
def send_stats(instance_id):
    if not instance_id:
        instance_id = get_instance_id()
    disk_utilization = get_disk_utilization()
    gpu_utilization = get_gpu_utilization_polled()
    url = 'api/instances/%s/stats' % instance_id
    results = api_call(url, post_data={
        'gpu_utilization': gpu_utilization,
        'disk_utilization': disk_utilization})



def api_call(route, put_data=False, post_data=False):
    url, id, token = get_authentication_token()
    full_url = "%s/%s" % (url, route)
    headers = {
        'User-Agent': 'nebula_cli',
        'id': id,
        'token': token
    }

    if post_data:
        r = requests.put(full_url, headers=headers, data=post_data)
    elif put_data:
        r = requests.put(full_url, headers=headers, data=put_data)
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

    token_pattern = r'^\s*token\s*=\s*([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})'
    token_match = re.search(token_pattern, config_string, flags=re.M)
    if not token_match:
        raise RuntimeError('Configuration file has no token.')
    token = token_match.group(1)

    token_id_match = re.search(r'^\s*token_id\s*=\s*([0-9a-f]{12})', config_string, flags=re.M)
    if not token_id_match:
        raise RuntimeError('Configuration file has no token_id.')
    token_id = token_id_match.group(1)

    install_url_match = re.search(r'^\s*url\s*=\s*(\S+)', config_string, flags=re.M)
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
    imdsv2_token_url = 'http://169.254.169.254/latest/api/token'
    token_request_headers = {'X-aws-ec2-metadata-token-ttl-seconds': '21600'}
    t = requests.put(imdsv2_token_url, headers=token_request_headers)
    t.raise_for_status()
    imdsv2_token = t.text

    metadata_request_headers = {'X-aws-ec2-metadata-token': imdsv2_token}
    r = requests.get('http://169.254.169.254/latest/meta-data/instance-id', headers=metadata_request_headers)
    r.raise_for_status()
    return r.text


def get_gpu_utilization_polled(attempts=3):
    gpu_stats = []
    for x in range(attempts):
        utilization = get_gpu_utilization()
        if utilization is False:
            return False
        gpu_stats.append(utilization)
        time.sleep(0.05)

    gpu_utilization = False
    if len(gpu_stats) > 0:
        total = sum(gpu_stats)
        if total == 0:
            gpu_utilization = 0
        else:
            gpu_utilization = sum(gpu_stats) / len(gpu_stats)

    return gpu_utilization


def get_gpu_utilization():
    # If nvidia-smi isn't here there are no GPUs
    which_result = subprocess.run(['which', 'nvidia-smi'], stdout=subprocess.PIPE)
    if which_result.returncode != 0:
        return False

    command = 'nvidia-smi --query-gpu=utilization.gpu --format=csv'
    result = subprocess.run(command.split(' '), stdout=subprocess.PIPE)
    util_strings = result.stdout.decode("utf-8").replace(' %', '').strip().split('\n')[1:]
    util_numbers = [int(n) for n in util_strings if n]

    # No GPUs detected
    if len(util_numbers) < 1:
        return False

    total = sum(util_numbers)
    if total <= 0:
        return 0

    return total/float(len(util_numbers))


def get_disk_utilization():
    usage = shutil.disk_usage('/')
    return usage.used/usage.total



if __name__ == '__main__':
    cli()
