
# Test Project
test:: 
	pytest tests/*

format::
	toml-sort pyproject.toml

# Build the project
build:: format 
	poetry install --with dev
	poetry build

# Publish the project
publish:: build
	poetry publish