import os

from .base import *

DEBUG = False
ALLOWED_HOSTS = [
	host.strip()
	for host in os.getenv('ALLOWED_HOSTS', '').split(',')
	if host.strip()
]

render_external_hostname = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if render_external_hostname:
	ALLOWED_HOSTS.append(render_external_hostname)