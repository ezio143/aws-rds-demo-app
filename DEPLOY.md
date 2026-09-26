# Deploying the FastAPI app to app_server via SSM

App code is intentionally kept separate from Terraform (no user_data
install script) — this is a manual, repeatable-by-hand deploy so each step
is visible rather than hidden inside instance boot logs.

## 1. Get the instance ID and connect

    terraform output app_server_instance_id
    aws ssm start-session --target <instance-id>

You're now in a shell on app_server, same as basic-vpc.

## 2. Install Python and MySQL client libs (Amazon Linux 2023)

    sudo dnf install -y python3.12 python3.12-pip git

## 3. Get the app code onto the instance

Simplest path for a small project like this: push the `app/` folder to a
private GitHub repo, then on the instance:

    git clone <your-repo-url>
    cd <repo>/app

(Outbound internet works fine here — app_server sits in a public subnet
with a route to the Internet Gateway, so git clone / pip install both
work without needing SSH inbound or a NAT Gateway.)

## 4. Install dependencies and set env vars

    python3.12 -m pip install -r requirements.txt --user

    export DB_HOST=<rds-endpoint-hostname-only>   # from: terraform output rds_endpoint
    export DB_PORT=3306
    export DB_USER=app_admin
    export DB_PASSWORD=<same password as terraform.tfvars>
    export DB_NAME=order_tracking

(For anything beyond a one-off test, put these in a `.env` file loaded by
systemd rather than typing exports into an SSM session each time — see
step 6.)

## 5. Run it

    python3.12 -m uvicorn main:app --host 0.0.0.0 --port 8000

Then from your own machine:

    curl http://<app_server_public_ip>:8000/health

`app_server_public_ip` is a Terraform output — `terraform output app_server_public_ip`.

## 6. (Optional, once it's working) Run it as a systemd service

So the app survives an instance reboot instead of dying when the SSM
session ends. On the instance:

    sudo tee /etc/systemd/system/order-tracking.service <<'EOF'
    [Unit]
    Description=Order Tracking FastAPI app
    After=network.target

    [Service]
    User=ssm-user
    WorkingDirectory=/home/ssm-user/<repo>/app
    EnvironmentFile=/home/ssm-user/<repo>/app/.env
    ExecStart=/usr/bin/python3.12 -m uvicorn main:app --host 0.0.0.0 --port 8000
    Restart=on-failure

    [Install]
    WantedBy=multi-user.target
    EOF

    sudo systemctl daemon-reload
    sudo systemctl enable --now order-tracking
