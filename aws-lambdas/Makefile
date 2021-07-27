etl: etl.py
	python3 -m pip install --target etl-package boto3
	cd etl-package; zip -r ../etl-package.zip .
	zip -g etl-package.zip etl.py

api: api.py
	python3 -m pip install --target api-package boto3
	cd api-package; zip -r ../api-package.zip .
	zip -g api-package.zip api.py