### Запуск приложения через Kubernetes

---

### **Preconditions**

1. **Установите Kubernetes и `kubectl`**:
   - Убедитесь, что ваш кластер Kubernetes доступен и настроен.
   - Проверьте подключение к кластеру:
     ```bash
     kubectl get nodes
     ```

2. **Убедитесь, что у вас есть рабочий Docker registry**:
   - Ваш приватный registry должен быть доступен с узлов кластера.
   - Пример: `192.168.2.100:5000`.

3. **Настройте приложение для работы с переменными окружения**:
   - Приложение должно использовать переменные среды для подключения к базе данных и другой конфигурации.

---

### **Шаг 1. Создание ConfigMap для приложения**

ConfigMap используется для хранения конфигурационных данных, таких как хост, порт, имя базы данных и имя пользователя.

1. Создайте файл `1_configmap.yaml` с содержимым:
   ```yaml
   apiVersion: v1
   kind: ConfigMap
   metadata:
     name: tracker-config
     namespace: default
   data:
     POSTGRES_HOST: "postgres"
     POSTGRES_PORT: "5432"
     POSTGRES_DB: "taskdb"
     POSTGRES_USER: "tracker_user"
   ```

2. Примените ConfigMap:
   ```bash
   kubectl apply -f 1_configmap.yaml
   ```

3. Проверьте, что ConfigMap создан:
   ```bash
   kubectl get configmap tracker-config -o yaml
   ```

---

### **Шаг 2. Создание Secret для пароля базы данных**

Secret используется для хранения конфиденциальных данных, таких как пароль базы данных.

1. Создайте файл `1_make_app_secret.sh` с содержимым:
   ```bash
   #!/bin/bash

   SECRET_NAME="tracker-secret"
   NAMESPACE="default"
   OUTPUT_FILE="1_${SECRET_NAME}.yaml"

   declare -A SECRET_DATA
   SECRET_DATA=(
     ["POSTGRES_PASSWORD"]="password"
   )

   (
   echo "apiVersion: v1
   kind: Secret
   metadata:
     name: $SECRET_NAME
     namespace: $NAMESPACE
   type: Opaque
   data:"
   for KEY in "${!SECRET_DATA[@]}"; do
     VALUE=${SECRET_DATA[$KEY]}
     ENCODED_VALUE=$(echo -n "$VALUE" | base64)
     echo "  $KEY: $ENCODED_VALUE"
   done ) | kubectl apply -f -
   ```

2. Сделайте скрипт исполняемым:
   ```bash
   chmod +x 1_make_app_secret.sh
   ```

3. Выполните скрипт:
   ```bash
   ./1_make_app_secret.sh
   ```

4. Проверьте, что Secret создан:
   ```bash
   kubectl get secret tracker-secret -o yaml
   ```

---

### **Шаг 3. Настройка доступа к приватному Docker registry**

Если ваш приватный Docker registry использует самоподписанный сертификат, Kubernetes может не доверять этому сертификату, что приведет к ошибке при попытке загрузить образы. Для решения этой проблемы нужно настроить доверие к сертификату на каждом узле кластера.

---

#### **Добавление доверия к самоподписанному сертификату**

1. **Скопируйте сертификат на все узлы Kubernetes**  
   Сначала получите публичный сертификат вашего Docker registry (например, `registry.crt`).

   На всех узлах Kubernetes выполните:
   ```bash
   mkdir -p /etc/docker/certs.d/<registry-host>:<port>
   cp registry.crt /etc/docker/certs.d/<registry-host>:<port>/
   ```

   Замените `<registry-host>:<port>` на адрес вашего Docker registry, например:
   ```
   /etc/docker/certs.d/192.168.2.100:5000/registry.crt
   ```

2. **Добавьте сертификат в системное хранилище доверенных сертификатов**  
   Чтобы сделать сертификат доверенным для всей системы:
   ```bash
   cp registry.crt /usr/local/share/ca-certificates/
   update-ca-certificates
   ```

3. **Перезапустите Docker и Kubelet**  
   После добавления сертификата перезапустите службы:
   ```bash
   systemctl restart docker
   systemctl restart kubelet
   ```

4. **Для containerd (если используется вместо Docker)**  
   Если ваш кластер использует `containerd`, настройте его конфигурацию:
   - Отредактируйте файл `/etc/containerd/config.toml`.
   - Добавьте секцию:
     ```toml
     [plugins."io.containerd.grpc.v1.cri".registry.configs."192.168.2.100:5000".tls]
       insecure_skip_verify = false
       ca_file = "/etc/docker/certs.d/192.168.2.100:5000/registry.crt"
     ```

   После этого перезапустите `containerd`:
   ```bash
   systemctl restart containerd
   ```

---

#### **Обход проверки сертификата (если сертификат нельзя добавить)**

Если вы не можете добавить сертификат в доверенное хранилище, настройте insecure-режим для Docker registry.

1. Для Docker:
   - Отредактируйте файл `/etc/docker/daemon.json`:
     ```json
     {
       "insecure-registries": ["192.168.2.100:5000"]
     }
     ```
   - Перезапустите Docker:
     ```bash
     systemctl restart docker
     ```

2. Для containerd:
   - Отредактируйте файл `/etc/containerd/config.toml`:
     ```toml
     [plugins."io.containerd.grpc.v1.cri".registry.configs."192.168.2.100:5000".tls]
       insecure_skip_verify = true
     ```
   - Перезапустите `containerd`:
     ```bash
     systemctl restart containerd
     ```

---

#### **Проверка настройки**

1. Проверьте доступность registry с узла:
   ```bash
   curl -k https://192.168.2.100:5000/v2/_catalog
   ```

2. Попробуйте вручную загрузить образ:
   ```bash
   docker pull 192.168.2.100:5000/task-tracker:latest
   ```

3. Убедитесь, что Kubernetes может загружать образ. Создайте простой Pod, используя образ из вашего приватного Registry. Укажите созданный секрет в imagePullSecrets:

  ```yaml
  apiVersion: v1
  kind: Pod
  metadata:
    name: test-registry
  spec:
    containers:
    - name: test-container
      image: <registry-host>:<registry-port>/<image>:<tag>
    imagePullSecrets:
    - name: regcred
  ```
Сохраните это как test-registry.yaml и создайте Pod:

  ```bash
  kubectl apply -f test-registry.yaml
  ```

Убедитесь, что Pod успешно запущен:

  ```bash
   kubectl get pods
   ```

---

### **Шаг 4. Развертывание приложения**

1. Создайте файл `3_deployment.yaml` с содержимым:
   ```yaml
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: tracker
     labels:
       app: tracker
   spec:
     replicas: 2
     selector:
       matchLabels:
         app: tracker
     template:
       metadata:
         labels:
           app: tracker
       spec:
         containers:
         - name: task-tracker
           image: 192.168.2.100:5000/task-tracker:latest
           ports:
           - containerPort: 8090
           imagePullPolicy: Always
           env:
           - name: POSTGRES_HOST
             valueFrom:
               configMapKeyRef:
                 name: tracker-config
                 key: POSTGRES_HOST
           - name: POSTGRES_PORT
             valueFrom:
               configMapKeyRef:
                 name: tracker-config
                 key: POSTGRES_PORT
           - name: POSTGRES_DB
             valueFrom:
               configMapKeyRef:
                 name: tracker-config
                 key: POSTGRES_DB
           - name: POSTGRES_USER
             valueFrom:
               configMapKeyRef:
                 name: tracker-config
                 key: POSTGRES_USER
           - name: POSTGRES_PASSWORD
             valueFrom:
               secretKeyRef:
                 name: tracker-secret
                 key: POSTGRES_PASSWORD
         imagePullSecrets:
         - name: registry-secret
   ```

2. Примените Deployment:
   ```bash
   kubectl apply -f 3_deployment.yaml
   ```

3. Проверьте Pods:
   ```bash
   kubectl get pods
   ```

---

### **Шаг 5. Создание Service для приложения**

1. Создайте файл `4_service.yaml` с содержимым:
   ```yaml
   apiVersion: v1
   kind: Service
   metadata:
     name: tracker-svc
     labels:
       app: tracker
   spec:
     ports:
     - port: 80
       targetPort: 8090
       protocol: TCP
     selector:
       app: tracker
     type: ClusterIP
   ```

2. Примените Service:
   ```bash
   kubectl apply -f 4_service.yaml
   ```

3. Проверьте, что сервис создан:
   ```bash
   kubectl get svc
   ```

---

### **Шаг 6. Настройка Ingress (опционально)**

1. Создайте файл `5_ingress.yaml`:
   ```yaml
   apiVersion: networking.k8s.io/v1
   kind: Ingress
   metadata:
     name: tracker-ingress
     annotations:
       nginx.ingress.kubernetes.io/rewrite-target: /
   spec:
     ingressClassName: nginx
     rules:
     - host: tracker.km.home
       http:
         paths:
         - path: /api
           pathType: Prefix
           backend:
             service:
               name: tracker-svc
               port:
                 number: 80
   ```

2. Примените Ingress:
   ```bash
   kubectl apply -f 5_ingress.yaml
   ```

3. Проверьте Ingress:
   ```bash
   kubectl get ingress
   ```

---

### **Шаг 7. Проверка работы приложения**

1. Проверка доступности через Service:
   ```bash
   kubectl exec -it <pod-name> -- curl http://tracker-svc.default.svc.cluster.local:80/api
   ```

2. Проверка через Ingress:
   ```bash
   curl http://tracker.km.home/api
   ```

---

### **Шаг 8. Мониторинг и отладка**

1. **Проверить Pods**:
   ```bash
   kubectl get pods
   kubectl describe pod <pod-name>
   kubectl logs <pod-name>
   ```

2. **Проверить Service**:
   ```bash
   kubectl describe svc tracker-svc
   ```

3. **Проверить Ingress**:
   ```bash
   kubectl describe ingress tracker-ingress
   ```

---

### **Результат**
После выполнения этих шагов приложение будет развернуто в Kubernetes с использованием ConfigMap, Secret, Docker registry и Ingress. Оно будет доступно как внутри кластера, так и извне (если настроен Ingress).
