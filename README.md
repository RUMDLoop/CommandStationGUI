CommandStationGUI
=================

### Recommended Steps

1. Learn how to use [Git](https://www.codecademy.com/learn/learn-git)
2. Learn how to write [Python](https://www.codecademy.com/learn/python)
2. Install Flask and follow the quickstart tutorial (link below)
3. Once you've done that, read about socket.io (links below) on Python and try implementing your own websocket application using that and Flask
4. If you would like to work on this, but haven't been assigned anything yet, message Shreyas on slack to see how you can help and to get access to the repository (note: this is different then getting access to the organization)

### Workflow

1. Clone this repository (HOW: "git clone https://github.com/RUMDLoop/CommandStationGUI")
2. If there is a new feature to be added, or a next step, or a bug, please make an [issue](https://help.github.com/articles/creating-an-issue/)
3. Create a new branch in this format: "Name/IS-(Issue Number)", so if I was working on Issue 5, it would be "shreyas/IS-5", if you are just playing around replace the part after the slash with "play", like "shreyas/play". (HOW: "git checkout -b (branch-name)
4. Once you are done and would like to contribute to the master branch, make a [pull request](https://help.github.com/articles/creating-a-pull-request/). Your code will be reviewed and merged in if it works and is good code
5. Once it has been merged in, delete your branch and repeat this process

### How to Test (External Client and Server only)
1. Inside the root directory of the project, in your command line (Terminal for Mac/Cygwin or PuTTY for Windows), run "python server.py"
2. Then, on your browser go to "http://localhost:5000"
3. Play around and make sure your code works!

### Components
1. External Client (mostly HTML/Javascript) - displays data and sends commands
2. Internal (Pod) Client (can be either Python or C++) - sends data and receives commands
3. Server (mostly Python) - acts as a middleman between the two, it is the core of the system


### Warnings

* DO NOT PUSH TO MASTER DIRECTLY
* TEST YOUR CODE BEFORE YOU MAKE A PULL REQUEST

### Relevant Links

* [Flask](http://flask.pocoo.org/docs/0.10/quickstart/)
* [Sockets](http://python-socketio.readthedocs.org/en/latest/)
* [Flask WITH Sockets](https://flask-socketio.readthedocs.org/en/latest/)
