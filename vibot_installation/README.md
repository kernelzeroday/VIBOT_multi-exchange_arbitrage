# README #

Notice: This script needs to be updated to use one unified repository

### What is this repository for? ###

* Automated Installation of Vibot
* Per Server Config
* [Learn Markdown](https://bitbucket.org/tutorials/markdowndemo)

## Configuration

* Check that the vibot server hostnames are correct in the host.sh file
* Check that your default ssh is set (optional)

### How do I get set up? ###

* With a new Ubuntu 16.04 system...
* Clone this repo
* Run ./deploy.sh -i to install everything (or run --help to see available options [*])
* Follow the prompts
* Do this for each server (vi1,vi2,vi3,etc)

ubuntu@ip-172-31-20-66:~$ ./deploy.sh -h

	  ... welcome to the                                       
	...........................................................
 	_    ___ __          __     ____             __           
	| |  / (_) /_  ____  / /_   / __ \___  ____  / /___  __  __
	| | / / / __ \/ __ \/ __/  / / / / _ \/ __ \/ / __ \/ / / /
	| |/ / / /_/ / /_/ / /_   / /_/ /  __/ /_/ / / /_/ / /_/ / 
	|___/_/_.___/\____/\__/  /_____/\___/ .___/_/\____/\__, /  
	                                   /_/            /____/   
	...........................................................
	        ...wizard. Powered by #!/bin/bash                  
	        $ respect the power of the shell                   
	        DarkerEgo, 2018 ~ github.com/darkerego             
	
	Usage: 
    	 ./deploy.sh --install / -a : Install Everything
     	./deploy.sh --deploy-only/-D : Just Configure the Server Normally, Do not install vibot
     	./deploy.sh --vibot/-vb : Just install vibot, don't configure server
     	./deploy.sh --help / -h : Show usage 


### Who do I talk to? ###

* xelectron@protonmail.com
