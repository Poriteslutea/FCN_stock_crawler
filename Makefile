# 創建docker network
create-docker-network:
	docker network create fcn_network

# 啟動postgresql db docker service
create-pgdb:
	docker compose -f pgdb.yml up -d

# 啟動crawler docker service
create-crawler:
	docker compose -f crawler.yml up -d

# 安裝環境
install-env:
	poetry install

# 建立.env (dev)
gen-dev-env:
	python genenv.py

# 建立.env (release)
gen-release-env:
	VERSION=RELEASE python genenv.py

# 更新report (SLN35)
update-report:
	poetry run python stock_crawler/create_report.py