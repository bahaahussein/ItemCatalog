This is Catalog application to list categories and the items needed for it.
To run this program:
1) Install python from https://www.python.org/about/gettingstarted/
2) If you are windows user, install git terminal from git-scm.com
3) Install VirtualBox whcih is software that actually runs the virtual machine from https://www.virtualbox.org/wiki/Downloads
4) Install vagrant which is software that configures the VM and lets you share files between your host computer and the VM's filesystem from https://www.vagrantup.com/downloads.html
5) Open terminal from the folder where vagrant is installed, write "vagrant up" to download the Linux operating system and install it.
6) Write in the terminal command "vagrant ssh" to log in to your newly installed Linux VM.
7) Change directory to the project folder.
8) In terminal, write command "python database_setup.py" to create the database.
9) In terminal, write command "python lotsofitems.py" to load some data in the database.
10) In terminal, write command "python application.py" to run the web application.
11) Open your favourite browser and go to link "http:localhost:5000"
