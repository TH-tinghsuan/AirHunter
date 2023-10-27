## AirHunter
Welcome to my project! This is a website made in Python and Flask framework. With this website, users can effectively find the most affordable flight ticket prices and receive email notificationsn when prices drop.
Additionally, it features a dashboard that visually represents fare data, offering users a comprehensive view of price trends.

- Website: https://www.airhunter.biz/
![image](https://github.com/TH-tinghsuan/git_practice/assets/134147328/e1695560-22c1-4205-8ef6-dede3e61f676)

## Project Framework
The project framework can be divided into two main components: the data pipeline and the web server.
#### Data Pipeline
Scraping data from four travel agent websites, processing it using ETL, and store it in a MySQL database. This process is automated using Airflow on an EC2 server, ensuring up-to-date flight prices.
#### Web Server
Bulit the web base on Flask framework, and used Nginx as a revers proxy server.

![image](https://github.com/TH-tinghsuan/git_practice/assets/134147328/bf6599e5-769e-4dbd-ab27-a1c1bd538078)

## Data Pipeline
<img width="365" alt="image" src="https://github.com/TH-tinghsuan/git_practice/assets/134147328/6c298dc6-94df-4b68-9419-a3841eb50837">


## Features
- #### Search for flight ticket prices and then direct users to the travel agent's booking page.
- #### A dashboard that provides an overview of price trends for specific departure and destination combinations.
- #### A tracking list feature for users to monitor their preferred airlines, with an automatic email notification system that informs users when ticket prices drop.
- #### Compare today's prices with those from yesterday and display the top four price drops on the main page.