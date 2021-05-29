
## Objective and Context
The goal of this exercise is to implement in python3.7 a microservice performing read/write operations to a MySQL database. The difficult part of the challenge is to handle concurrent requests without losing consistency of the data.

This service is exposed using `uwsgi` which creates 4 worker processes to handle concurrent requests. I chose `Flask` as the web framework to integrate with `uwsgi`

### Prerequisites:
This project does not include a migration mechanism such as `Flask-Migrate`. There is at the root of the project a file called `init_db.sql` with the SQL DDL queries to initialize the database. This is a manual step.

### Starting the application
Build and run the application using docker-compose. The `.env` file is included for demonstrational purposes, as `.env` files should not be versioned. 
```
docker-compose build api client
docker-compose up mysql
docker-compose up api
```
To use the API on your localhost, you need to bind the ports. Add the following line to your api definition in the `docker-compose.yml`
and rebuild 

```
ports:
  - 8888:8888
```
### Running the tests
To run the tests execute:
```
docker-compose up client
```
Which should output the following:
```
docker-compose up client
Docker Compose is now in the Docker CLI, try `docker compose up`

interview-challenge_mysql_1 is up-to-date
interview-challenge_api_1 is up-to-date
Starting interview-challenge_client_1 ... done
Attaching to interview-challenge_client_1
client_1  | test_0_health (api_test.ApiTestCase)
client_1  | anity check to ensure that the API is reachable ... ok
client_1  | test_1_single_user (api_test.ApiTestCase)
client_1  | test read/write operations on a single user ... ok
client_1  | test_2_two_users (api_test.ApiTestCase)
client_1  | test read/write operations with two users ... ok
client_1  | test_3_concurrent (api_test.ApiTestCase)
client_1  | test concurrent read/write operations with multiple threads ... ok
client_1  |
client_1  | ----------------------------------------------------------------------
client_1  | Ran 4 tests in 0.430s
client_1  |
client_1  | OK
interview-challenge_client_1 exited with code 0
```

### Lessons learned
On my first approach, I solved the concurrent update in a very convoluted way, which lead into inconsistent test runs. 
I had some green runs, and some red runs on the fourth test, which failed because of deadlocks.
Upon closer inspection and rethinking my query, I came up with the proposed solution, which decoupled the involved tables
in the deadlocks.
