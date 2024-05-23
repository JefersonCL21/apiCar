# # Usar uma imagem base do Python
# FROM python:3.9-slim

# # Definir o diretório de trabalho dentro do container
# WORKDIR /app

# # Copiar os arquivos de requisitos para o container
# COPY requirements.txt .

# # Instalar as dependências
# RUN pip install --no-cache-dir -r requirements.txt

# # Copiar o resto do código-fonte para o diretório de trabalho no container
# COPY . .

# # Comando para executar a aplicação usando Uvicorn
# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]





#Para o render
# Usar uma imagem base do Python
FROM python:3.9-slim

# Definir o diretório de trabalho dentro do container
WORKDIR /app

# Copiar os arquivos de requisitos para o container
COPY requirements.txt .

# Instalar as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o resto do código-fonte para o diretório de trabalho no container
COPY . .

# Definir variáveis de ambiente
ENV MODULE_NAME=main
ENV VARIABLE_NAME=app

# Expor a porta que o Uvicorn usará
EXPOSE 8000

# Comando para executar a aplicação usando Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
