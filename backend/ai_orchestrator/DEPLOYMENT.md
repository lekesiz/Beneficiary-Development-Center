# 🚀 Guide de Déploiement - Système d'Orchestration d'IA

Ce guide détaille les différentes options de déploiement pour le système d'orchestration d'IA.

## 📋 Prérequis

### Système
- **OS** : Linux (Ubuntu 20.04+ recommandé), macOS, Windows
- **Python** : 3.11 ou supérieur
- **RAM** : 4GB minimum, 8GB recommandé
- **CPU** : 2 cores minimum, 4 cores recommandé
- **Stockage** : 10GB minimum

### Clés API (Optionnel)
- **Anthropic** : Pour Claude (recommandé)
- **OpenAI** : Pour GPT-4/ChatGPT
- **Google** : Pour Gemini
- **Autres** : Selon les modèles utilisés

## 🏠 Déploiement Local

### Installation Standard

```bash
# 1. Cloner le repository
git clone <repository-url>
cd ai_orchestrator

# 2. Créer un environnement virtuel
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# ou
venv\\Scripts\\activate  # Windows

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Configuration
cp config/config.example.yaml config/config.yaml
# Éditer config/config.yaml selon vos besoins

# 5. Variables d'environnement
export ANTHROPIC_API_KEY="votre_clé_claude"
export OPENAI_API_KEY="votre_clé_openai"

# 6. Lancer le système
python main.py
```

### Mode Développement

```bash
# Installation en mode développement
pip install -e .

# Lancer avec rechargement automatique
python -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

# Tests
pytest tests/

# Linting
black src/
flake8 src/
```

## 🐳 Déploiement Docker

### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Installer les dépendances système
RUN apt-get update && apt-get install -y \\
    gcc \\
    && rm -rf /var/lib/apt/lists/*

# Copier les fichiers de requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code source
COPY src/ src/
COPY main.py .
COPY config/ config/

# Créer les dossiers nécessaires
RUN mkdir -p data logs

# Exposer le port
EXPOSE 8000

# Variables d'environnement par défaut
ENV PYTHONPATH=/app
ENV ORCHESTRATOR_LOG_LEVEL=INFO

# Commande de démarrage
CMD ["python", "main.py"]
```

### Docker Compose

```yaml
version: '3.8'

services:
  orchestrator:
    build: .
    ports:
      - "8000:8000"
    environment:
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - DATABASE_PATH=/app/data/orchestrator.db
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
      - ./config:/app/config
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    restart: unless-stopped

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana
      - ./monitoring/grafana:/etc/grafana/provisioning
    restart: unless-stopped

volumes:
  redis_data:
  prometheus_data:
  grafana_data:
```

### Commandes Docker

```bash
# Build et démarrage
docker-compose up -d

# Logs
docker-compose logs -f orchestrator

# Arrêt
docker-compose down

# Mise à jour
docker-compose pull
docker-compose up -d
```

## ☸️ Déploiement Kubernetes

### Namespace

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: ai-orchestrator
```

### ConfigMap

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: orchestrator-config
  namespace: ai-orchestrator
data:
  config.yaml: |
    orchestrator:
      max_models_per_task: 3
      default_timeout: 300
    decision_engine:
      min_consensus_score: 0.7
    logging:
      level: INFO
```

### Secret

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: api-keys
  namespace: ai-orchestrator
type: Opaque
data:
  anthropic-api-key: <base64-encoded-key>
  openai-api-key: <base64-encoded-key>
```

### Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: orchestrator
  namespace: ai-orchestrator
spec:
  replicas: 3
  selector:
    matchLabels:
      app: orchestrator
  template:
    metadata:
      labels:
        app: orchestrator
    spec:
      containers:
      - name: orchestrator
        image: ai-orchestrator:latest
        ports:
        - containerPort: 8000
        env:
        - name: ANTHROPIC_API_KEY
          valueFrom:
            secretKeyRef:
              name: api-keys
              key: anthropic-api-key
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: api-keys
              key: openai-api-key
        volumeMounts:
        - name: config
          mountPath: /app/config
        - name: data
          mountPath: /app/data
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
      volumes:
      - name: config
        configMap:
          name: orchestrator-config
      - name: data
        persistentVolumeClaim:
          claimName: orchestrator-data
```

### Service

```yaml
apiVersion: v1
kind: Service
metadata:
  name: orchestrator-service
  namespace: ai-orchestrator
spec:
  selector:
    app: orchestrator
  ports:
  - port: 80
    targetPort: 8000
  type: ClusterIP
```

### Ingress

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: orchestrator-ingress
  namespace: ai-orchestrator
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
  - hosts:
    - orchestrator.votre-domaine.com
    secretName: orchestrator-tls
  rules:
  - host: orchestrator.votre-domaine.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: orchestrator-service
            port:
              number: 80
```

### Déploiement K8s

```bash
# Appliquer les manifests
kubectl apply -f k8s/

# Vérifier le déploiement
kubectl get pods -n ai-orchestrator
kubectl get services -n ai-orchestrator

# Logs
kubectl logs -f deployment/orchestrator -n ai-orchestrator

# Scaling
kubectl scale deployment orchestrator --replicas=5 -n ai-orchestrator
```

## 🌐 Déploiement Cloud

### AWS ECS

```json
{
  "family": "ai-orchestrator",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "executionRoleArn": "arn:aws:iam::account:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "orchestrator",
      "image": "your-account.dkr.ecr.region.amazonaws.com/ai-orchestrator:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "ORCHESTRATOR_LOG_LEVEL",
          "value": "INFO"
        }
      ],
      "secrets": [
        {
          "name": "ANTHROPIC_API_KEY",
          "valueFrom": "arn:aws:secretsmanager:region:account:secret:anthropic-key"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/ai-orchestrator",
          "awslogs-region": "us-west-2",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

### Google Cloud Run

```yaml
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: ai-orchestrator
  annotations:
    run.googleapis.com/ingress: all
spec:
  template:
    metadata:
      annotations:
        autoscaling.knative.dev/maxScale: "10"
        run.googleapis.com/cpu-throttling: "false"
    spec:
      containerConcurrency: 80
      containers:
      - image: gcr.io/your-project/ai-orchestrator:latest
        ports:
        - containerPort: 8000
        env:
        - name: ANTHROPIC_API_KEY
          valueFrom:
            secretKeyRef:
              name: api-keys
              key: anthropic-key
        resources:
          limits:
            cpu: "2"
            memory: "4Gi"
```

### Azure Container Instances

```yaml
apiVersion: 2019-12-01
location: eastus
name: ai-orchestrator
properties:
  containers:
  - name: orchestrator
    properties:
      image: your-registry.azurecr.io/ai-orchestrator:latest
      ports:
      - port: 8000
        protocol: TCP
      environmentVariables:
      - name: ORCHESTRATOR_LOG_LEVEL
        value: INFO
      - name: ANTHROPIC_API_KEY
        secureValue: your-api-key
      resources:
        requests:
          cpu: 1
          memoryInGB: 2
  osType: Linux
  ipAddress:
    type: Public
    ports:
    - protocol: TCP
      port: 8000
  restartPolicy: Always
```

## 🔧 Configuration Production

### Nginx Reverse Proxy

```nginx
upstream orchestrator {
    server 127.0.0.1:8000;
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
}

server {
    listen 80;
    server_name orchestrator.votre-domaine.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name orchestrator.votre-domaine.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://orchestrator;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    location /health {
        proxy_pass http://orchestrator/health;
        access_log off;
    }
}
```

### Systemd Service

```ini
[Unit]
Description=AI Orchestrator
After=network.target

[Service]
Type=simple
User=orchestrator
Group=orchestrator
WorkingDirectory=/opt/ai-orchestrator
Environment=PYTHONPATH=/opt/ai-orchestrator
Environment=ORCHESTRATOR_LOG_LEVEL=INFO
EnvironmentFile=/etc/ai-orchestrator/environment
ExecStart=/opt/ai-orchestrator/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Monitoring

```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'orchestrator'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: /metrics
    scrape_interval: 5s

  - job_name: 'node'
    static_configs:
      - targets: ['localhost:9100']
```

## 🔒 Sécurité

### SSL/TLS
```bash
# Générer certificat Let's Encrypt
certbot --nginx -d orchestrator.votre-domaine.com
```

### Firewall
```bash
# UFW (Ubuntu)
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable
```

### Secrets Management
```bash
# Utiliser des gestionnaires de secrets
# AWS Secrets Manager, Azure Key Vault, Google Secret Manager
# Ou HashiCorp Vault pour on-premise
```

## 📊 Monitoring Production

### Health Checks
- `/health` - Santé générale
- `/ready` - Prêt à recevoir du trafic
- `/metrics` - Métriques Prometheus

### Alertes Critiques
- Service indisponible
- Latence > 30s
- Taux d'erreur > 5%
- Utilisation mémoire > 80%

### Logs Centralisés
```yaml
# ELK Stack ou équivalent
logging:
  handlers:
    - type: elasticsearch
      hosts: ["elasticsearch:9200"]
      index: ai-orchestrator
```

## 🔄 Mise à Jour

### Rolling Update
```bash
# Kubernetes
kubectl set image deployment/orchestrator orchestrator=ai-orchestrator:v2.0

# Docker Compose
docker-compose pull
docker-compose up -d
```

### Blue-Green Deployment
```bash
# Déployer la nouvelle version
kubectl apply -f k8s/blue-green/

# Basculer le trafic
kubectl patch service orchestrator-service -p '{"spec":{"selector":{"version":"green"}}}'
```

## 🆘 Dépannage

### Problèmes Courants

1. **Erreur de connexion API**
   ```bash
   # Vérifier les clés API
   echo $ANTHROPIC_API_KEY
   curl -H "x-api-key: $ANTHROPIC_API_KEY" https://api.anthropic.com/v1/messages
   ```

2. **Problème de mémoire**
   ```bash
   # Augmenter les limites
   docker run -m 4g ai-orchestrator
   ```

3. **Latence élevée**
   ```bash
   # Vérifier les métriques
   curl http://localhost:8000/metrics
   ```

### Logs de Debug
```bash
# Activer le debug
export ORCHESTRATOR_LOG_LEVEL=DEBUG
python main.py
```

---

Ce guide couvre les principales méthodes de déploiement. Choisissez celle qui correspond le mieux à votre infrastructure et vos besoins.

