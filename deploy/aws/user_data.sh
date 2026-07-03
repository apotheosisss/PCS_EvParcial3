#!/bin/bash
# =============================================================================
# EC2 user-data (Amazon Linux 2023) — bootstrap de DiabetesNHANES
# Pegar este script en "Advanced details > User data" al lanzar la instancia.
# Instala Docker + Compose, clona el repo y deja todo listo para deploy.sh.
# =============================================================================
set -euxo pipefail

REPO_URL="https://github.com/apotheosisss/PCS_EvParcial3.git"
APP_DIR="/opt/diabetes-nhanes"

# --- Docker + Git ------------------------------------------------------------
dnf update -y
dnf install -y docker git
systemctl enable --now docker

# Docker Compose v2 (plugin)
mkdir -p /usr/local/lib/docker/cli-plugins
curl -SL "https://github.com/docker/compose/releases/latest/download/docker-compose-linux-x86_64" \
  -o /usr/local/lib/docker/cli-plugins/docker-compose
chmod +x /usr/local/lib/docker/cli-plugins/docker-compose

# Permite a ec2-user usar docker sin sudo
usermod -aG docker ec2-user || true

# --- Clonar el proyecto ------------------------------------------------------
git clone "$REPO_URL" "$APP_DIR"
chown -R ec2-user:ec2-user "$APP_DIR"

echo "Bootstrap completo. Continua con: cd $APP_DIR && bash deploy/aws/deploy.sh"
