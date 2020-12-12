# Sudoku Solver API

## What is it?

The Sudoku solver API is used to solve sudoku boards. It takes in http reqests with the sudoku board you want to solve.
It uses python algorithm to solve the sudoku boards and then it returns a json with the answer.

## What is it made of?

This API is build from a Flask API MYSQL DATABASE and a logger.
the idea that every board you sent it is solved and also stored in the DB for when you send
the same request it will be taken from the DB instead of being solved again and wasting power and time.

## How to start the API?

The only things you will need to start this API is Docker installed, internet connection and this code.
Easy way to download docker is using the [docker installation guid](https://docs.docker.com/engine/install/ubuntu/).

When you are done you will need to pull this project.
After you have everything you will need to edit the .env configuration file.

There are two configurations there one for the MYSQL password and the other one is the dir you want to put your logs from
the API to.

After you've configured the .env file its time to build the API.
Open the terminal and go to the directory where this project is.
And do:

```bash
$ docker-compose up -d
```
> If you are on linux you may need to use sudo befor the command

This will start the applicaion.
Wait until you start getting logs in the log file that is created in the dir you configured and then you can start sending requests.

# Sending Requests

This API is listening on port 5000.
There are 4 urls in this API:

* http://ip:5000/solve
* http://ip:5000/hint
* http://ip:5000/show_db
* http://ip:5000/delete_db

The first two : solve and hint require a body where the board and other data is stored. make sure that the body is in json format!
The json should look like this : {'data':{'board':[],'empty':X}}
When the empty value can be what ever you want and it is the value that represents the empty places in the sudoku board(cant be true or false)

e.g.

{
    "data":{
        "empty":0,
        "board":[
            0,0,0,0,7,0,0,0,0,
            6,0,0,1,9,5,0,0,0,
            0,9,8,0,0,0,0,6,0,
            8,0,0,0,6,0,0,0,3,
            4,0,0,8,0,3,0,0,1,
            7,0,0,0,2,0,0,0,6,
            0,6,0,0,0,0,2,8,0,
            0,0,0,4,1,9,0,0,5,
            0,0,0,0,8,0,0,7,9
        ]
    }
}

after you send this board to the solver you will get your answer back:

{
  "data":{
    "multiple_answers":true,
    "solved_board":[
      3,4,5,6,7,8,9,1,2,
      6,7,2,1,9,5,3,4,8,
      1,9,8,3,4,2,5,6,7,
      8,5,9,7,6,1,4,2,3,
      4,2,6,8,5,3,7,9,1,
      7,1,3,9,2,4,8,5,6,
      9,6,1,5,3,7,2,8,4,
      2,8,7,4,1,9,6,3,5,
      5,3,4,2,8,6,1,7,9
      ]
    },
    "method":"solver"
}

The method will change if you send it again to db because it will come from the DB instead of being solved again.

If you send it to hint:
{
    "data": {
        "location": 75,
        "value": 2
    },
    "method": "solver"
}

The other two urls are used for:
* delete_db - used to delete all the values from the DB not recomended
* show_db - use to see all the data in the DB

## Stand alone

If you want to run this API on a stand alone machine/ network that has no access to the internet you will have to folow this steps:

1.
you will need to run the Dockerfile:

```bash
$ docker build . -t sudokuapi:1.0
```
> If you are on linux you may need to use sudo befor the command

This command will create a docker image out of the flask API.

After that you will need to do:

```bash
$ docker pull mysql
```
> If you are on linux you may need to use sudo befor the command

When done use:
```bash
$ docker images
```
To see that the images are ready.
after this you will need to delete some lines in the docker-compose.yml file

```bash
    build:
      context: .
      dockerfile: ./Dockerfile
```
Thouse are the lines that you need to remove
After that you will need to save the docker images localy:
```bash
$ docker save sudokuapi:1.0 > sudokuapi.tar
```

```bash
$ docker save mysql > mysql.tar
```

That is almost it now you should have 4 files:
* sudokuapi.tar
* mysql.tar
* docker-compose.yml
* .env
thouse files you need to copy to the standalone machine (that also should have docker)
and after again configuring the .env file you do :
```bash
$ docker-compose up -d
```
and wait for the logs.