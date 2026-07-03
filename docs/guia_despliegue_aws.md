# Guía de despliegue en AWS (EC2 + Docker Compose)

Despliegue de **DiabetesNHANES** en un **AWS Academy Learner Lab**. El Learner Lab
restringe servicios (ECS/EKS suelen estar bloqueados), por lo que el camino soportado
y verificado es **EC2 + docker-compose**.

> Región del Learner Lab: normalmente **us-east-1**. Usa la key pair del lab (`vockey`)
> y el rol `LabRole` ya provistos.

---

## 0. Requisitos
- Learner Lab **iniciado** (botón *Start Lab*, punto verde).
- Acceso a la consola AWS (botón *AWS* del lab).
- Los scripts [`deploy/aws/user_data.sh`](../deploy/aws/user_data.sh) y
  [`deploy/aws/deploy.sh`](../deploy/aws/deploy.sh) de este repo.

---

## 1. Lanzar la instancia EC2
Consola AWS → **EC2** → *Launch instance*:

| Campo | Valor |
|---|---|
| Name | `diabetes-nhanes` |
| AMI | **Amazon Linux 2023** |
| Instance type | **t3.large** (8 GB) — recomendado por el ETL. Mínimo `t3.medium` (4 GB). |
| Key pair | `vockey` (la del lab) |
| Network / Security group | crear uno nuevo, ver paso 2 |
| Storage | 20 GB gp3 |
| Advanced details → User data | pegar el contenido de `deploy/aws/user_data.sh` |

> El *user data* instala Docker, Compose y clona el repo automáticamente al arrancar.

---

## 2. Security Group (puertos)
Crear/editar el Security Group con estas reglas de entrada (*inbound*):

| Tipo | Puerto | Origen | Uso |
|---|---|---|---|
| SSH | 22 | Mi IP | administración |
| Custom TCP | 8000 | 0.0.0.0/0 | API FastAPI (`/docs`) |
| Custom TCP | 8501 | 0.0.0.0/0 | Dashboard |

> Para la defensa puedes restringir a *My IP*; para la demo pública, `0.0.0.0/0`.

---

## 3. Conectarse y desplegar
Cuando la instancia esté *Running* (espera ~2-3 min a que el user-data termine):

**Opción A — EC2 Instance Connect** (navegador, sin key): botón *Connect* → *EC2 Instance Connect*.

**Opción B — SSH**:
```bash
ssh -i vockey.pem ec2-user@<IP_PUBLICA>
```

Ya dentro de la instancia:
```bash
cd /opt/diabetes-nhanes
bash deploy/aws/deploy.sh
```

El script descarga los datos NHANES, corre el ETL (genera `model.pkl` y reportes) y
levanta API + dashboard + db.

---

## 4. Verificar
Desde tu navegador (reemplaza `<IP_PUBLICA>` por la IP de la instancia):
- API: `http://<IP_PUBLICA>:8000/docs`
- Dashboard: `http://<IP_PUBLICA>:8501`

Chequeo rápido de salud:
```bash
curl http://<IP_PUBLICA>:8000/health
```

---

## 5. Troubleshooting

| Síntoma | Causa | Solución |
|---|---|---|
| ETL muere con `exit 137` | Sin memoria (OOM) | Usa `t3.large`; el `deploy.sh` ya corre el ETL aparte para mitigarlo |
| No abre `:8000`/`:8501` | Security Group | Verifica reglas inbound del paso 2 |
| `docker: permission denied` | Grupo docker | `newgrp docker` o reconéctate por SSH |
| Descarga NHANES falla | Red/CDN | El ETL usa la muestra: `python scripts/make_sample_model_input.py` |

---

## 6. Apagar para ahorrar créditos
El Learner Lab consume crédito mientras la instancia corre:
```bash
# detener servicios
docker compose -f docker/docker-compose.yml down
```
Y en la consola EC2 → *Instance state* → **Stop** (no *Terminate* si quieres reusarla).
Al cerrar el lab, todo se detiene automáticamente.

---

## 7. Evidencia para la entrega
Captura para el informe/anexos:
- Instancia EC2 *Running* con su IP pública.
- `http://<IP>:8501` con el dashboard cargado.
- `http://<IP>:8000/docs` con los endpoints.
- Salida de `curl .../health` mostrando `"status":"ok"`.
