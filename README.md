# stock_crawler

## create docker network
```
## create db on docker 
``` docker compose -f pgdb.yml up ```

## initialize db
``` docker exec -it fcn-postgres /bin/bash ```
``` psql -U admin -d fcn2 ```
``` \i ./create_table.sql```

## deploy
``` docker run --name fcn-db -d --restart=always -v postgres-data:/var/lib/postgresql/data -p 5432:5432 -e POSTGRES_USER='' -e POSTGRES_PASSWORD='' -e POSTGRES_DB='' --network fcn_network my_registry/fcn-postgres:0.0.1 ```

```docker run --name fcn-scheduler -d --restart=always --network fcn_network docker.megoo.site/fcn-scheduler:0.0.1 poetry run python stock_crawler/scheduler.py
```

