### Установка StatefulSet PostgreSQL в Kubernetes

#### 1. Подготовка окружения

##### 1.1. Создание секретов
Создайте `Secret`, содержащий пароли для пользователя базы данных и репликации:

```yaml
# 1_secret.yml
apiVersion: v1
kind: Secret
metadata:
  name: postgres
type: Opaque
stringData:
  password: XXXXXX
  replicaPassword: XXXXXX
```

Примените манифест:
```bash
kubectl apply -f 1_secret.yml
```

##### 1.2. Создание ConfigMap
Соберите все необходимые конфигурационные файлы в `ConfigMap`:
```bash
cd config; kubectl create configmap postgres \
  --from-file=postgres.conf \
  --from-file=master.conf \
  --from-file=replica.conf \
  --from-file=pg_hba.conf \
  --from-file=create-replica-user.sh \
  --dry-run=client -o yaml > ../2_configmap.yaml
cd ..
kubectl apply -f 2_configmap.yaml
```

Пример содержимого файлов конфигурации:
- `postgres.conf`: основные настройки PostgreSQL.
- `master.conf`: настройки для мастера.
- `replica.conf`: настройки для реплики.
- `pg_hba.conf`: правила доступа.
- `create-replica-user.sh`: скрипт создания пользователя репликации.

##### 1.3. Настройка PersistentVolumes
Создайте `PersistentVolume` для хранения данных PostgreSQL:

```yaml
# 3_postgres_local_pv.yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: persistent-postgres-pv-0
spec:
  capacity:
    storage: 1Gi
  accessModes:
    - ReadWriteOnce
  persistentVolumeReclaimPolicy: Retain
  local:
    path: /mnt/data/persistent-postgres-0
  nodeAffinity:
    required:
      nodeSelectorTerms:
      - matchExpressions:
        - key: kubernetes.io/hostname
          operator: In
          values:
          - k8s-worker-0
---
apiVersion: v1
kind: PersistentVolume
metadata:
  name: persistent-postgres-pv-1
spec:
  capacity:
    storage: 1Gi
  accessModes:
    - ReadWriteOnce
  persistentVolumeReclaimPolicy: Retain
  local:
    path: /mnt/data/persistent-postgres-1
  nodeAffinity:
    required:
      nodeSelectorTerms:
      - matchExpressions:
        - key: kubernetes.io/hostname
          operator: In
          values:
          - k8s-worker-1
```

Примените манифест:
```bash
kubectl apply -f 3_postgres_local_pv.yaml
```

#### 2. Поднятие мастер-нод

Создайте StatefulSet для мастера:

```bash
kubectl apply -f 4_statefulset-master.yml
```

`4_statefulset-master.yml` должен включать настройку VolumeClaimTemplate и использование ConfigMap.

#### 3. Настройка сервисов
Создайте сервисы для мастера и реплики:

```yaml
# 5_service.yaml
apiVersion: v1
kind: Service
metadata:
  labels:
    app: postgres
  name: postgres
spec:
  type: ClusterIP
  ports:
  - name: postgres
    port: 5432
    protocol: TCP
    targetPort: 5432
  selector:
    app: postgres
---
apiVersion: v1
kind: Service
metadata:
  labels:
    app: postgres-replica
  name: postgres-replica
spec:
  type: ClusterIP
  ports:
  - name: postgres-replica
    port: 5432
    protocol: TCP
    targetPort: 5432
  selector:
    app: postgres-replica
```

Примените манифест:
```bash
kubectl apply -f 5_service.yaml
```

#### 4. Поднятие реплики

Создайте StatefulSet для реплики:
```bash
kubectl apply -f 6_statefulset-replica.yml
```

Пример `statefulset-replica.yml` включает:
- Контейнер `initContainers` для настройки данных реплики через `pg_basebackup`.
- Использование секретов и ConfigMap для конфигурации.

#### 5. Проверка работы

##### Проверка статуса ресурсов:
```bash
kubectl get pods
kubectl get pv
kubectl get svc
```

##### Проверка подключения:
Подключитесь к PostgreSQL:
```bash
kubectl exec -it <master-pod-name> -- psql -U postgres
```

#### Заключение

Этот процесс разворачивает PostgreSQL с мастер-репликой в Kubernetes с использованием `StatefulSet`, `ConfigMap` и `Secrets`. StatefulSet обеспечивает управление подами с сохранением данных в локальном хранилище.


Добавить секцию про добавление user data.
