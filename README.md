# stock_crawler

## create db on docker 
``` docker compose -f pgdb.yml up ```

## initialize db
``` docker exec -it fcn-postgres /bin/bash ```
``` psql -U admin -d fcn2 ```
``` \i ./create_table.sql```
