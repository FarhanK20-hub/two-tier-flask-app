# Flask + MySQL Deployment on AWS EC2 using Docker

This guide explains how to deploy a Flask application connected to a MySQL database using Docker on an AWS EC2 instance.

---

## **Prerequisites**
- AWS account
- EC2 instance (Ubuntu 22.04 LTS recommended)
- SSH key to connect to the instance
- Flask app with `requirements.txt` including `mysqlclient`

---

## **1️⃣ Launch EC2 Instance**
1. Create an Ubuntu 22.04 LTS instance.
2. Configure Security Group to allow:
   - SSH → port 22
   - Flask app → port 5000
   - MySQL (optional for remote) → port 3306
3. Note your **public IP**.

---

## **2️⃣ Connect to EC2**
```bash
ssh -i your-key.pem ubuntu@<EC2-public-IP>
```

---

## **3️⃣ Install Docker**
```bash
sudo apt update
sudo apt install -y docker.io
sudo systemctl enable --now docker
sudo usermod -aG docker $USER
```
> Logout and login again to run `docker` without `sudo`.

---

## **4️⃣ Create Docker Network**
```bash
docker network create flask-network
```

---

## **5️⃣ Run MySQL Container**
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
- Wait for MySQL to be ready:
```bash
docker logs flask-mysql
```

---

## **6️⃣ Prepare Flask Dockerfile**
Example Dockerfile:
```dockerfile
FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y gcc default-libmysqlclient-dev pkg-config && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir mysqlclient -r requirements.txt

COPY . .

CMD ["python", "app.py"]
```

---

## **7️⃣ Build Flask Docker Image**
```bash
docker build -t flaskapp:latest .
```

---

## **8️⃣ Run Flask Container**
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

---

## **9️⃣ Verify Flask App**
```bash
docker logs flask-app
```
- You should see:
```
* Running on http://0.0.0.0:5000/ (Press CTRL+C to quit)
```

---

## **🔟 Access from Browser**
Open:
```
http://<EC2-public-IP>:5000
```
Your Flask application should now be live and connected to the MySQL database.

---

💡 **Optional:** Use `docker-compose.yml` to run both MySQL and Flask in one command for cleaner deployment.

