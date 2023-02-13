### Website Demo Video: 
https://www.youtube.com/watch?v=oZlG4QvNlWc&list=PLHTeo1wzM4eIMHFiSwvYTCxVavXNu_3_b&index=38&t=133s

### How our system works at a packet level
Packets allow us to split up the information we are transmitting and recieving into smaller units, making their transer more efficient and streamlined. When it comes to the information we are relaying from our server to the client this aids in the delivery of larger files and data that is required for communication to and from the server. 

We communicate using Transmission Control Protocol (TCP) which is the basis for connection based communication and is used in the HTTP and HTTPS protocols we utilize to communicate with clients. When a user looks up our domain name on a web browser the DNS will translate it to our IP. The client will then send a packet to our server. Through the use of routing tables the packet will eventually land at our server and we will then be able to communicate with the client. 

![Diagram of Packet Flow](/source/images/Packet_Diagram.png "Packet Diagram")

### Server Documentation
For our server we are using Nginx as our reverse proxy/load balancer. Nginx will serve the purpose of managing traffic to our server as well as encrypting the data that comes to and from the server. Nginx is basically a middleman, that will intercept these requests and decide further action upon inspection. Our Nginx is currently set up to encrypt and protect the server with through the use of SSL. SSL was set up through the use of certbot, a program that automatically modified our Nginx sites-available configuration file, which encrypts and secures the server. This allows us to communicate on port 443 and enable HTTPS communication.

Additionally we are using gunicorn, a python web server gateway that interfaces with HTTP, to serve our flask application. This flask application currently displays the log in authenticator Auth0 which we use to monitor incoming users into our website. From here we want to display the news we obtain from HackerNews using the HackerNews API. 

![Auth0 Home](/source/images/Auth0_Home_Image.PNG "Auth0 Home")

### Updates
Any updates made to the Nginx configuration requires that we run the command: **sudo systemctl restart nginx** this will restart the service and allow for the changes to reflect. 

If we make any changes to our project .service file which determines what flask application is currently being served then we must execute the following list of commands: 
- sudo daemon-restart
- sudo systemctl stop myproject
- sudo systemctl disable myproject
- sudo systemctl start myproject
- sudo systemctl enable myproject

This will ensure that any changes made to the service file and/or gunicorn will be applied properly. 

### Instructions, Ease of Installation


In order to set up the application on another server that would require cloning the repo into a folder. 

In order to clone from Gitlab it would require using SSH keys or cloning over HTTPS, once all the necessary files are in the directory, you can then move to set up the server so it runs the application,

First, you must update the server and install all new packages and make sure that the server has Python3, you must then download all necessary packages into the virtual environment so that the application has all the necessary tools, 

The list of packages are as follows

    pip install wheel

    pip install gunicorn flask

You would then go onto the main server within our application and change the app.run ip address so that the application can run on the new server.

Once this has been established you would go into the gunicorn service file and make sure that the files are appropriate placed in order to bind Gunicorn, our project has our Gunicorn file, with our local paths set.

Once the Gunicorn service file has been created you would save it and start it as boot, 

	sudo systemctl start myproject
    sudo systemctl enable myproject

Now in order to use Nginx you must set up the Nginx server configuration blocks, so that it points to the appropriate server,

server {
    listen 80;
    server_name your_domain www.your_domain;

    location / {
        include proxy_params;
        proxy_pass http://unix:/home/USER/myproject/myproject.sock;
    }
}


You must then link the files to sites-enabled in order for Nginx to create the server block using the following command,

	sudo ln -s /etc/nginx/sites-available/myproject /etc/nginx/sites-enabled

In order to see the reflected changes you would then restart nginx and allow Nginx to run fully using the following commands

	sudo systemctl restart nginx
    sudo ufw allow 'Nginx Full'

You would then see the changes displayed on your domain,

Auth0

First you will need to configure the settings on Auth0 in order to get secure authentication to work on the new server, you will have to add the appropriate URL to the callback and logout URLs, as we have done for our site with our domain names

![Auth0](/source/images/urlHandling.png "PythonHackers")

Afterwards you will have to install all the necessary dependencies from the requirements.txt file, in order to link the Auth0 application to their database you  must edit the ENV file and put your own,

    Client ID, 
    Client Secret Key
    Domain
    Secret Key 

Afterwards Auth0 will be configured to run on the server.

![Auth0](/source/images/PythonHackers.png "PythonHackers")

Then you can import flask into your python file.
