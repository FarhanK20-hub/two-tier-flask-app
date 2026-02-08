# Flask + MySQL Deployment on AWS EC2 using Docker & Docker Compose

This README provides a **step-by-step guide** to deploy a Flask application connected to a MySQL database using Docker on an AWS EC2 instance. It also covers pushing your Docker image to Docker Hub and managing containers using Docker Compose.

---

## **📌 Prerequisites**

Before starting, ensure you have the following:

* AWS account
* EC2 instance (Ubuntu 22.04 LTS recommended)
* SSH key to connect to the instance
* Flask application with `requirements.txt` (including `mysqlclient`)
* Docker Hub account (optional for pushing images)

---

## **1️⃣ Launch an EC2 Instance**

1. Create an **Ubuntu 22.04 LTS** instance.
2. Configure **Security Group** to allow:

   * SSH → port 22
   * Flask app → port 5000
   * MySQL (optional for remote) → port 3306
3. Take note of your **EC2 public IP**.

> Security tip: Restrict access to known IPs for SSH and MySQL if possible.

---

## **2️⃣ Connect to EC2**

Open terminal and run:

```bash
ssh -i your-key.pem ubuntu@<EC2-public-IP>
```

Replace `your-key.pem` with your private key file and `<EC2-public-IP>` with your instance's public IP.

---

## **3️⃣ Install Docker**

Install Docker and enable it to start on boot:

```bash
sudo apt update
sudo apt install -y docker.io
sudo systemctl enable --now docker
sudo usermod -aG docker $USER
```

> Logout and login again so you can run Docker commands without `sudo`.

Verify Docker installation:

```bash
docker --version
```

---

## **4️⃣ Create a Docker Network**

To allow Flask and MySQL containers to communicate:

```bash
docker network create flask-network
```

---

## **5️⃣ Run MySQL Container**

Start MySQL container using Docker:

```bash
docker run -d \
  --name flask-mysql \
  --network flask-network \
  -e MYSQL_ROOT_PASSWORD=password \
  -e MYSQL_DATABASE=flaskdb \
  -e MYSQL_USER=flaskuser \
  -e MYSQL_PASSWORD=flaskpass \
  -p 3306:3306 \
  mysql:8
```

Check if MySQL is running:

```bash
docker logs flask-mysql
```

> This creates a MySQL database called `flaskdb` with a user `flaskuser`.

---

## **6️⃣ Prepare Flask Dockerfile**

Create a `Dockerfile` in your Flask project root:

```dockerfile
<<<<<<< HEAD
# Use Python slim image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install dependencies for MySQL
RUN apt-get update && apt-get install -y gcc default-libmysqlclient-dev pkg-config && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir mysqlclient -r requirements.txt

# Copy Flask app code
COPY . .

# Run the Flask app
=======
# Use an official Python runtime as the base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# install required packages for system
RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y gcc default-libmysqlclient-dev pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
COPY requirements.txt .

# Install app dependencies
RUN pip install mysqlclient
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Specify the command to run your application
>>>>>>> 7d29b05664d2f9b99285b01fd5eca1b832fd5693
CMD ["python", "app.py"]
```

---

## **7️⃣ Build Flask Docker Image**

```bash
docker build -t flaskapp:latest .
```

* `flaskapp:latest` is the name/tag of your Docker image.
* Ensure `app.py` and `requirements.txt` are in the same directory.

---

## **8️⃣ Run Flask Container**

Run Flask and link it to MySQL:

```bash
docker run -d \
  --name flask-app \
  --network flask-network \
  -p 5000:5000 \
  -e MYSQL_HOST=flask-mysql \
  -e MYSQL_USER=flaskuser \
  -e MYSQL_PASSWORD=flaskpass \
  -e MYSQL_DB=flaskdb \
  flaskapp:latest
```

Verify Flask logs:

```bash
docker logs flask-app
```

You should see:

```
* Running on http://0.0.0.0:5000/ (Press CTRL+C to quit)
```

---

## **9️⃣ Access Flask App**

Open your browser and go to:

```
http://<EC2-public-IP>:5000
```

Your Flask application should now be live and connected to MySQL.

---

## **🔟 Push Docker Image to Docker Hub (Optional)**

1. Login to Docker Hub:

```bash
docker login
```

2. Tag your image:

```bash
docker tag flaskapp:latest <your-username>/flaskapp:latest
```

3. Push it:

```bash
docker push <your-username>/flaskapp:latest
```

> Replace `<your-username>` with your Docker Hub username.

---

## **1️⃣1️⃣ Docker Compose Setup (Recommended)**

Create a `docker-compose.yml` for easier deployment:

```yaml
version: "3.9"

services:
  mysql:
    image: mysql:8
    container_name: flask-mysql
    restart: unless-stopped
    environment:
      MYSQL_ROOT_PASSWORD: password
      MYSQL_DATABASE: flaskdb
      MYSQL_USER: flaskuser
      MYSQL_PASSWORD: flaskpass
    ports:
      - "3306:3306"
    networks:
      - flask-network

  flask:
    image: <your-username>/flaskapp:latest
    container_name: flask-app
    restart: unless-stopped
    ports:
      - "5000:5000"
    environment:
      MYSQL_HOST: flask-mysql
      MYSQL_USER: flaskuser
      MYSQL_PASSWORD: flaskpass
      MYSQL_DB: flaskdb
    depends_on:
      - mysql
    networks:
      - flask-network

networks:
  flask-network:
    driver: bridge
```

Run everything:

```bash
docker-compose up -d
```

---

## **1️⃣2️⃣ Verify Deployment**

```bash
docker ps
docker logs flask-app
docker logs flask-mysql
```

Your app should now be running with MySQL on the same network.

---

## **1️⃣3️⃣ Optional Production Setup**

* Use **port 80** for Flask (no need to type `:5000` in browser)
* Add **Nginx** as a reverse proxy
* Enable **SSL** using Let's Encrypt
* Ensure **auto-restart** on EC2 reboot:

```bash
docker update --restart unless-stopped flask-app
```

---

## ✅ Summary

* Deployed Flask app + MySQL on AWS EC2 using Docker.
* Managed containers via Docker Compose.
* Optional: Pushed Docker image to Docker Hub.
* Optional: Configured production-ready setup with reverse proxy & SSL.

> Your Flask app is now fully deployed, scalable, and easy to manage with Docker.
