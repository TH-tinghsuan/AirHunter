## AirHunter
Welcome to my project! This is a website made in Python and Flask framework. With this website, users can effectively find the most affordable flight ticket prices and receive email notificationsn when prices drop.
Additionally, it features a dashboard that visually represents fare data, offering users a comprehensive view of price trends.

- Website: https://www.airhunter.biz/
<img width="100%" alt="image" src="https://github.com/TH-tinghsuan/git_practice/assets/134147328/e1695560-22c1-4205-8ef6-dede3e61f676">

## Project Framework
The project framework can be divided into two main components: the data pipeline and the web server.
#### Data Pipeline
Scraping data from four travel agent websites, processing it using ETL, and store it in a MySQL database. This process is automated using Airflow on an EC2 server, ensuring up-to-date flight prices.
#### Web Server
Bulit the web base on Flask framework, and used Nginx as a revers proxy server.

<img width="100%" alt="image" src="https://github.com/TH-tinghsuan/git_practice/assets/134147328/bf6599e5-769e-4dbd-ab27-a1c1bd538078">

## Data Pipeline
<p align="center">
  <img width="618" alt="image" src="https://github.com/TH-tinghsuan/AirHunter/assets/134147328/20616c5d-b261-4fea-b051-403a4143aca5">
</p>

## Features
- #### Search for flight ticket prices and then direct users to the travel agent's booking page.
  

https://github.com/TH-tinghsuan/AirHunter/assets/134147328/8e472a39-f3aa-4efd-b568-30dece78c997


- #### A dashboard that provides an overview of price trends for specific departure and destination combinations.


https://github.com/TH-tinghsuan/AirHunter/assets/134147328/855c4a35-272f-4c61-867c-924aa65e8d51


- #### A tracking list feature for users to monitor their preferred airlines, with an automatic email notification system that informs users when ticket prices drop.


https://github.com/TH-tinghsuan/AirHunter/assets/134147328/8b4c5d20-4ba7-4fe9-acfe-3ed464b31c23

## Skills

> Data Pipeline
- Airflow
> Backend
- Flask
> Database
- MySQL
> Frontend
- HTML
- CSS
- JavaScript
> Networking
- Nginx
- SSL Certificate(Let's Encrypt)
> CI/CD
- GitHub Actions
> Others
- AWS EC2
- AWS RDS
- AWS S3
- AWS SQS