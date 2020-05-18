# osm-tm-communication

Repository for testing the storage of files in a github repository.

## Configuration

* Copy the example configuration file to start your own configuration: `cp example.env .env`.
* Adjust the `.env` configuration file to fit your configuration.
* Make sure that the following variables are set correctly in the `.env` configuration file:
  - `POSTGRES_USER`=database-user-name
  - `POSTGRES_PASSWORD`=database-user-password
  - `POSTGRES_ENDPOINT`=database-endpoint-can-be-localhost
  - `POSTGRES_PORT`=database-port
  - `POSTGRES_DB`=database-name
  - `GITHUB_TOKEN`=github-api-token
  - `GITHUB_REPOSITORY`=github-repository-where-files-will-be-saved
  - `GITHUB_COMMITER_NAME`=github-user-that-will-commit-file
  - `GITHUB_COMMITER_EMAIL`=github-email-that-will-commit-file

## Build

### Python dependencies

* Create a Python Virtual Environment, using Python 3.7+:
    * ```python3 -m venv ./venv```
* Activate your virtual environment and install dependencies:
    * Linux/Mac:
        * ```. ./venv/bin/activate```
        * ```pip install -r requirements.txt```
* With your virtual environment activaded, execute the following command for running the server
    * ```py
      python runserver -d
      ```

## Postgres database

* The database uses docker for development, but you can also set the `.env` file to run the databasse in your postgres local instance. In case of docker, for setting everything just follow the command.
    * `docker-compose up`

## Endpoints availables

* `/document` - **POST**
    * Create a xml file with the post received in the following format.
    ```json
    {
	"project":{
		"id": "projectId",
		"goal": "projectGoal",
		"timeframe": "projectTimeframe",
		"externalSource": "projectExternalSource",
		"instructions": "projectInstructions",
		"projectManager": "projectManager",
	    "changesetComment": "projectChangesetComment",
		"users": [
			{
				"osmId": "userOsmId"
			},
			{
				"osmId": "userOsmId"
			}
		]
	},
	"organisation":{
		"id": "organisationId",
		"name": "organisationName",
        "description": "organisationDescription"
	}
    }
    ```

## Migrations 
* All migrations commands
    * `python manage.py db init`
    * `python manage.py db upgrade`
    * `python manage.py db downgrade`

## Tests

* For running tests execute the following command:
    * `python -m unittest discover server/tests/`