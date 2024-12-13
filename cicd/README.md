# Документация по CI/CD для проекта Task Tracker

## Описание
Настройка CI/CD реализована с использованием GitLab CI и включает три стадии:
1. **Build** — сборка и публикация Docker-образов.
2. **Test** — выполнение тестов.
3. **Deploy** — развертывание приложения в Kubernetes.

## Общая структура
```yaml
stages:
  - build
  - test
  - deploy

variables:
  REGISTRY_URL: "192.168.2.100:5000"
  IMAGE_NAME: "$REGISTRY_URL/task-tracker"
  REGISTRY_USER: "admin"
  REGISTRY_PASSWORD: $REGISTRY_PASSWORD
  DOCKER_TLS_CERTDIR: ""

services:
  - name: docker:stable
    alias: docker
    command:
      - "--host=tcp://0.0.0.0:2375"
```

### Переменные
- **REGISTRY_URL**: URL Docker-реестра.
- **IMAGE_NAME**: Полное имя образа, включая реестр.
- **REGISTRY_USER**: Пользователь для авторизации в реестре.
- **REGISTRY_PASSWORD**: Пароль для авторизации (передается через переменные окружения).
- **DOCKER_TLS_CERTDIR**: Отключение использования TLS для Docker.
- **KUBECONFIG**: Файл конфигурации Kubernetes, добавленный как переменная типа File в GitLab, неявно используемая при выполнении команд `kubectl`.

### Сервисы
Для выполнения сборки используется Docker, запускаемый в контейнере с настройкой сервиса.

---

## Стадии CI/CD

### 1. Build (Сборка)
**Цель:** Сборка Docker-образа приложения и публикация его в реестр.

**Конфигурация:**
```yaml
build:
  stage: build
  image: docker:stable
  before_script:
    - echo $REGISTRY_PASSWORD | docker login $REGISTRY_URL -u $REGISTRY_USER --password-stdin
  script:
    - docker build -t $IMAGE_NAME:$CI_COMMIT_SHA ./application/src
    - docker tag $IMAGE_NAME:$CI_COMMIT_SHA $IMAGE_NAME:latest
    - docker push $IMAGE_NAME:$CI_COMMIT_SHA
    - docker push $IMAGE_NAME:latest
  rules:
    - changes:
        - application/src/**  # Отслеживаем изменения в application/src
      when: always
    - when: never  # Отключает выполнение, если изменения отсутствуют
```

**Описание шагов:**
1. Авторизация в Docker-реестре.
2. Сборка Docker-образа с тегом, соответствующим текущему коммиту.
3. Присвоение тегу "latest".
4. Публикация обоих тегов в реестр.

**Условие выполнения:**
Стадия выполняется только при изменениях в директории `application/src`.

---

### 2. Test (Тестирование)
**Цель:** Запуск тестов для проверки работоспособности кода.

**Конфигурация:**
```yaml
test:
  stage: test
  script:
    - echo "Running tests..."  # Placeholder для тестов
  dependencies:
    - build
  rules:
    - changes:
        - application/src/**
      when: always
    - when: never
```

**Описание шагов:**
1. Выполнение тестов (место для добавления реальных тестовых команд).
2. Зависимость от стадии **Build**, чтобы использовать собранный Docker-образ.

**Условие выполнения:**
Стадия выполняется только при изменениях в директории `application/src`.

---

### 3. Deploy (Развертывание)
**Цель:** Обновление и развертывание приложения в Kubernetes.

**Конфигурация:**
```yaml
deploy:
  stage: deploy
  cache:
    key: "${CI_COMMIT_REF_SLUG}-${CI_COMMIT_SHA}"
    paths:
    - .runner-cache/
  image:
    name: bitnami/kubectl:1.29
    entrypoint: [""]
  script:
    - kubectl config get-contexts
    - kubectl patch deployment tracker -p "{\"spec\":{\"template\":{\"metadata\":{\"annotations\":{\"ci-run-id\":\"$CI_PIPELINE_ID\"}}}}}"
    - kubectl rollout status deployment/tracker
  dependencies:
    - test
  rules:
    - changes:
        - application/src/**
      when: always
    - when: never
```

**Описание шагов:**
1. Проверка текущих контекстов Kubernetes.
2. Обновление аннотации в деплойменте с ID текущего пайплайна.
3. Ожидание завершения обновления деплоймента.

**Условие выполнения:**
Стадия выполняется только при изменениях в директории `application/src`.

---

## Зависимости между стадиями
- **Test** зависит от успешного выполнения **Build**.
- **Deploy** зависит от успешного выполнения **Test**.

---

## Настройка GitLab Runner

Для успешного выполнения пайплайна требуется:
1. Убедиться, что установлен GitLab Runner и он поддерживает Docker-in-Docker.
2. Убедиться, что Runner настроен на доступ к Kubernetes-кластеру.
3. Добавить переменные `REGISTRY_PASSWORD` и другие в настройках репозитория (Settings > CI/CD > Variables).

---

## Рекомендации по тестированию и обновлению
1. **Тесты:** Разработайте и добавьте полноценные тесты в стадию **Test**.
2. **Обновления Kubernetes:** Проверьте корректность конфигурации kubectl, включая доступ к кластеру и контексты.
3. **Мониторинг:** Настройте уведомления о статусе пайплайна для быстрого реагирования.

