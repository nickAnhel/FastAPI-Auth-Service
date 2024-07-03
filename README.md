# Auth Service API

A service for users authentication and authorization based on JWT.

## Local launching

Create a virtual environment and install all required dependencies using `poetry`.

```bash
# Create a virtual env
python3 -m venv .venv

# Intall all dependencies
poetry install
```

Create the public and private keys for JWT encrypting.

```bash
# Create a dir to store the keys
md certs
cd certs

# Create a private key
openssl genrsa -out private.pem 2048

# Create a public key
openssl rsa -in private.pem -outform PEM -pubout -out public.pem
```

Run `alembic` migrations.

```bash
alembic upgrade head
```

## Launching with Docker

Build and run the containers.

```bash
docker compose up --build
```
