#!/bin/bash

mkdir ~/almond-server
echo '{"server-login":{"password":"x","salt":"x","sqliteKeySalt":"x"}}' > ~/almond-server/prefs.db
docker run -p 3000:3000 \
  -v ~/almond-server:/var/lib/almond-server \
  -e THINGENGINE_HOST_BASED_AUTHENTICATION=insecure \
  stanfordoval/almond-server:latest-portable &

sleep 60
