.PHONY: deps
deps:
	poetry install 

.PHONY: run-opensearch
run-opensearch:
	@echo "Starting OpenSearch..."
	docker-compose up -d

.PHONY: index-products
index-products:
	@echo "Creating index..."
	curl -k -X PUT \
		-u admin:admin https://localhost:9200/green_products \
		-H 'Content-Type: application/json' \
		-d @green_products.json
	@echo "Indexing products..." && \
	poetry run python index.py -s data/products.csv -w 9 -b 500

.PHONY: reindex-products
reindex-products:
	@echo "Reindexing products..."
	poetry run python index.py

.PHONY: delete-index
delete-index:
	@echo "Deleting index..." && \
	curl -k -X DELETE \
	-u admin:admin https://localhost:9200/green_products


.PHONY: stop
stop:
	@echo "Stopping OpenSearch..."
	docker-compose down

.PHONY: run-plugin-server
run-plugin-server:
	@echo "Starting Plugin Server..."
	cd plugin-server && poetry run python main.py
