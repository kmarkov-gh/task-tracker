**Название проекта:** TaskTracker

**Описание:**\
TaskTracker — это минималистичное веб-приложение для управления задачами. Пользователи могут создавать, редактировать, удалять задачи, а также отмечать их как завершенные. Приложение имеет REST API и статичный фронтенд для взаимодействия. Для хранения данных используется база данных PostgreSQL. Основное внимание в проекте уделяется реализации и автоматизации DevOps процессов.

---

**Технологический стек:**

- **Backend:** FastAPI (Python) — для реализации API.
- **Frontend:** SPA (Single Page Application).
- **База данных:** PostgreSQL.
- **Контейнеризация:** Docker.
- **Оркестрация:** Kubernetes.
- **CI/CD:** GitLab CI.
- **Мониторинг:** Prometheus + Grafana.
- **Облачный провайдер:** OpenNebula.

---

### Этапы реализации проекта:

1. **Создание инфраструктуры Kubernetes-кластера:**

   - Подготовка виртуальных машин на OpenNebula с использованием Terraform.
   - Развертывание Kubernetes-кластера с помощью Ansible (Kubespray).
   - Настройка сети (поддержка LoadBalancer, MetalLB).
   - Конфигурация узлов для обеспечения высокой доступности.

2. **Создание Docker registry:**

   - Локальный Docker registry для хранения образов.

3. **Разработка и контейнеризация приложения:**

   - Создание Dockerfile.

4. **CI/CD Pipeline:**

   - Автоматизация сборки, тестирования и деплоя с использованием GitLab CI.
   - Использование GitLab Runner для исполнения pipeline.
   - Настройка безопасности CI/CD (ограничение доступа к чувствительным данным).
   - Реализация автоматического обновления приложений при изменении кода.

5. **Мониторинг и логирование:**

   - Настройка Prometheus для сбора метрик.
   - Интеграция Grafana для визуализации данных.

6. **Документация:**

   - README.md с общей информацией о проекте.
   - Детальная документация по каждому этапу:
     - Инфраструктура Kubernetes.
     - Настройка CI/CD.
     - Мониторинг.

---

### Инфраструктура проекта:

1. **Kubernetes:**

   - **Приложение:**
     - Deployment имиджа приложения из Docker registry.
   - **База данных (PostgreSQL):**
     - StatefulSet для управления базой данных.
     - VolumeClaimTemplates для PVC.
   - **Конфигурация:**
     - ConfigMap для переменных окружения.
     - Secrets для управления чувствительными данными (пароли, токены).
   - **Сеть:**
     - Ingress с использованием nginx ingress controller.
     - MetalLB для управления внешними IP-адресами.

2. **Хранилище:**

   - PersistentVolume (PV) и PersistentVolumeClaim (PVC) для базы данных PostgreSQL.
   - Использование встроенного хранилища OpenNebula.

3. **Мониторинг и логирование:**

   - Prometheus для сбора метрик Kubernetes и приложений.
   - Grafana для визуализации метрик и создания дашбордов.
   - Настройка алертов на основе метрик для уведомлений о критических событиях.

4. **CI/CD:**

   - Автоматизация сборки новых имиджей при коммите нового кода приложения.

   - Автоматизация деплоя через kubectl.

---

### Рекомендации по дополнениям:

1. **Функционал:**

   - Добавить регистрацию и аутентификацию пользователей (если не предусмотрено).
   - Добавить возможность прикреплять файлы к задачам (через Object Storage).

2. **Технологии:**

   - Использовать kustomize или Helm для управления манифестами Kubernetes.
   - Добавить Keycloak или другой инструмент для управления аутентификацией.

3. **Документация:**

   - Добавить инструкции по настройке мониторинга и логирования.
   - Описать процессы масштабирования компонентов (ручное и автоматическое).
   - Создать раздел по безопасным практикам работы с Kubernetes и CI/CD.

4. **Дополнительные компоненты:**

   - Настроить горизонтальное и вертикальное автоскалирование (HPA/VPA).
   - Добавить RBAC для управления доступом к кластеру.

