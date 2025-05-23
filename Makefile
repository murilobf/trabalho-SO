# Roda o programa principal
run:
	python3 main.py

# Instala todas as dependências listadas em requirements.txt
install:
	pip3 install -r requirements.txt

# Atualiza requirements.txt com dependências do sistema
freeze:
	pip3 freeze > requirements.txt

# Remove arquivos temporários
clean:
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -delete
