# Установка и настройка Prometheus и Grafana

---

### 1. Создание PersistentVolume (PV) для Prometheus

На этом этапе создаются PersistentVolume для хранения данных Prometheus. Файл `1_pv_prometheus.yaml` содержит определения двух PersistentVolume, привязанных к различным узлам кластера.

**Как выполнить:**
1. Примените файл:
   ```bash
   kubectl apply -f 1_pv_prometheus.yaml
   ```
2. Проверьте, что PersistentVolume созданы:
   ```bash
   kubectl get pv
   ```

---

### 2. Создание PersistentVolume (PV) для Grafana

На этом этапе создаётся PersistentVolume для хранения данных Grafana. Файл `2_pv_grafana.yaml` содержит определение одного PersistentVolume для хранения данных Grafana.

**Как выполнить:**
1. Примените файл:
   ```bash
   kubectl apply -f 2_pv_grafana.yaml
   ```
2. Проверьте, что PersistentVolume создано:
   ```bash
   kubectl get pv
   ```

---

### 3. Установка Prometheus

На этом этапе производится установка Prometheus с использованием Helm-чарта. Используется файл `3_install_prometheus.sh`, который устанавливает Prometheus с учётом настроек, указанных в `values-prometheus.yaml`.

**Как выполнить:**
1. Запустите скрипт:
   ```bash
   bash 3_install_prometheus.sh
   ```
2. Проверьте, что все компоненты Prometheus установлены:
   ```bash
   kubectl get pods -n monitoring
   ```

---

### 4. Установка Grafana

На этом этапе производится установка Grafana с использованием Helm-чарта. Используется файл `4_install_grafana.sh` для автоматизации установки.

**Как выполнить:**
1. Запустите скрипт:
   ```bash
   bash 4_install_grafana.sh
   ```
2. Проверьте, что Grafana успешно установлена:
   ```bash
   kubectl get pods -n monitoring
   ```
3. Получите пароль администратора Grafana:
   ```bash
   kubectl get secret --namespace monitoring grafana -o jsonpath="{.data.admin-password}" | base64 --decode ; echo
   ```

---

### 5. Настройка прав доступа для Prometheus

На этом этапе создаются необходимые роли и привязки для Prometheus. Файл `5_clusterrole.yaml` содержит все необходимые настройки.

**Как выполнить:**
1. Примените файл:
   ```bash
   kubectl apply -f 5_clusterrole.yaml
   ```

---

### 6. Добавление метрик приложения

Приложение должно экспортировать метрики в формате Prometheus. В данном примере приложение использует `prometheus-client` и предоставляет метрики по адресу `/api/metrics`.

1. Проверьте, что приложение отдаёт метрики:
   ```bash
   curl http://<адрес-сервиса-приложения>/api/metrics
   ```
2. Конфигурация для сбора метрик приложения уже указана в `values-prometheus.yaml` при установке:
   ```yaml
   extraScrapeConfigs: |
     - job_name: 'my-application'
       metrics_path: '/api/metrics'
       static_configs:
         - targets:
             - 'tracker-svc.default.svc.cluster.local:80'
   ```
3. Примените изменения (если необходимо):
   ```bash
   helm upgrade prometheus prometheus-community/prometheus --namespace monitoring -f values-prometheus.yaml
   ```
4. Проверьте, что метрики приложения появились в Prometheus:
   - Откройте Prometheus UI.
   - Найдите метрики вашего приложения, например, `http_requests_total`.

---

### 7. Настройка Grafana для визуализации метрик

1. Войдите в Grafana (URL: `http://<IP-адрес-Grafana>:3000`, логин: `admin`, пароль: из шага 4.3).
2. Добавьте источник данных Prometheus:
   - Перейдите в `Configuration -> Data Sources`.
   - Нажмите `Add data source` и выберите `Prometheus`.
   - Введите URL Prometheus (`http://prometheus-server.monitoring.svc.cluster.local`) и сохраните.
3. Создайте дашборды для визуализации метрик:
   - Перейдите в `Dashboards -> New Dashboard`.
   - Добавьте панели (панели) с нужными метриками (например, `http_requests_total`).

---

Документация охватывает установку, настройку, и интеграцию всех компонентов для мониторинга.
