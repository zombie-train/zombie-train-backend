#!/bin/bash

if ! [ -x "$(command -v certbot)" ]; then
  echo 'Error: certbot is not installed.' >&2
  exit 1
fi

domain=zombietra.in
email=sheliutsin.aliaksandr@gmail.com # Adding a valid address is strongly recommended
rsa_key_size=4096
data_path="/etc/letsencrypt"
nginx_conf="/etc/nginx/conf.d/default.conf"

if [ -d "$data_path/live/$domain" ]; then
  echo "Existing certificate found for $domain"
else
  echo "### Requesting Let's Encrypt certificate for $domain ..."

  # Enable staging mode if needed
  # staging_arg="--staging"

  certbot certonly --nginx --non-interactive --agree-tos --email $email -d $domain $staging_arg

  echo "### Reloading Nginx ..."
  nginx -s reload
fi

echo "### Replacing environment variables in Nginx config ..."
envsubst '${DJANGO_ALLOWED_HOSTS}' < /etc/nginx/conf.d/default.conf.template > /etc/nginx/conf.d/default.conf

echo "### Starting Nginx ..."
exec nginx -g 'daemon off;'
