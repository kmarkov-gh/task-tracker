# Установка NGINX Ingress Controller и настройка маршрутизации

Данный документ описывает шаги по установке NGINX Ingress Controller и настройке маршрутизации трафика в Kubernetes. 

## 1. Описание файлов конфигурации

### Файлы для установки NGINX Ingress Controller:
1. **`1_namespace.sh`**: Скрипт для создания namespace `ingress-nginx`, в котором будут размещены ресурсы контроллера.
2. **`2_serviceaccount.yaml`**: Определение ServiceAccount, используемого NGINX Ingress Controller.
3. **`3_clusterrole-nginx.yaml`**: Определение ClusterRole с правами доступа для работы контроллера с различными ресурсами Kubernetes.
4. **`4_clusterrolebinding.yaml`**: Привязка ServiceAccount к ClusterRole для предоставления необходимых прав.
5. **`5_install-ingress-nginx.sh`**: Скрипт для установки NGINX Ingress Controller через Helm.

### Файлы для проверки и развертывания:
1. **`6_check.sh`**: Скрипт для проверки состояния pod-ов Ingress Controller.
2. **`7_make_statichtml.sh`**: Скрипт для создания ConfigMap из файла `index.html` с контентом для статического веб-сервера.

### Файлы для развертывания приложений:
1. **`8.1_deployment.yaml`**: Deployment для статического веб-сервера с использованием NGINX.
2. **`8.2_service.yaml`**: Service для обеспечения доступа к статическому веб-серверу.

### Файл маршрутизации:
1. **`9_ingress.yaml`**: Конфигурация Ingress для маршрутизации трафика. Устанавливает правила маршрутизации для разных путей (`/api` и `/`).

---

## 2. Пошаговая инструкция

### Шаг 1. Создание namespace
Запустите файл `1_namespace.sh`:
```bash
bash 1_namespace.sh
```

### Шаг 2. Создание ServiceAccount и ролей
Примените файлы `2_serviceaccount.yaml`, `3_clusterrole-nginx.yaml` и `4_clusterrolebinding.yaml` для настройки ролей и прав доступа:
```bash
kubectl apply -f 2_serviceaccount.yaml
kubectl apply -f 3_clusterrole-nginx.yaml
kubectl apply -f 4_clusterrolebinding.yaml
```

### Шаг 3. Установка Ingress Controller
Используйте скрипт `5_install-ingress-nginx.sh` для установки NGINX Ingress Controller:
```bash
bash 5_install-ingress-nginx.sh
```

### Шаг 4. Проверка состояния
После установки запустите `6_check.sh` для проверки, что все pod-ы находятся в состоянии `Running`:
```bash
bash 6_check.sh
```

### Шаг 5. Развертывание статического веб-сервера
Создайте ConfigMap из файла `index.html` с помощью скрипта `7_statichtml.sh`:
```bash
bash 7_make_statichtml.sh
kubectl apply -f 7_indexhtml_cm.yaml
```

Примените конфигурации Deployment и Service:
```bash
kubectl apply -f 8.1_deployment.yaml
kubectl apply -f 8.2_service.yaml
```

### Шаг 6. Настройка маршрутизации
Настройте Ingress, используя файл `9_ingress.yaml`:
```bash
kubectl apply -f 9_ingress.yaml
```

---

## 3. Проверка маршрутизации

1. Убедитесь, что DNS для `tracker.km.home` настроен на IP-адрес вашего узла Kubernetes или NodePort.
2. Проверьте доступ к веб-серверу:
   ```bash
   curl http://tracker.km.home/
   ```
3. Проверьте доступ к API:
   ```bash
   curl http://tracker.km.home/api
   ```

---

На этом установка и настройка завершены. Вы успешно развернули NGINX Ingress Controller и настроили маршрутизацию трафика в Kubernetes.
