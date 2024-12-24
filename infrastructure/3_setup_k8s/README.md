# Установка Kubernetes через Kubespray

## Подготовка окружения

### Шаг 1: Подготовка серверов

Сервера:

- Два мастер-узла.
- Два воркер-узла (на одном из которых будет запущен третий экземпляр etcd).

### Шаг 2: Подготовка локальной машины

1. Установите зависимости:
   ```bash
   sudo apt update
   sudo apt install -y python3 python3-pip git
   ```
2. Склонируйте репозиторий Kubespray:
   ```bash
   git clone https://github.com/kubernetes-sigs/kubespray.git
   cd kubespray
   ```
3. Создайте виртуальное окружение и активируйте его:
   ```bash
   pip install virtualenv
   virtualenv .
   . bin/activate
   ```
4. Установите Python-зависимости:
   ```bash
   pip install -r requirements.txt
   ```

### Шаг 3: Настройка inventory

1. Укажите IP-адреса мастеров и воркеров в скрипте `generate_inventory.py`:

   ```python
   # Задаем IP мастеров и воркеров
   masters = [f"192.168.2.{i}" for i in [148, 149]]
   workers = [f"192.168.2.{i}" for i in [147, 134]]
   ```

2. Сгенерируйте файл `inventory.ini` с помощью скрипта `generate_inventory.py`:

   ```bash
   python3 generate_inventory.py
   ```

3. Проверьте и убедитесь, что файл `inventory.ini` соответствует вашей инфраструктуре.

## Установка Kubernetes

### Шаг 1: Запуск Ansible-плейбуков

1. Убедитесь, что есть SSH доступ ко всем серверам.
   - Добавьте SSH-ключ, если необходимо:
     ```bash
     ssh-copy-id root@<ip_address>
     ```
2. Проверьте подключение:
   ```bash
   ansible -i inventory.ini all -m ping
   ```
3. Запустите плейбук для установки кластера:
   ```bash
   cp -pr inventory/sample inventory/mycluster
   cp inventory.ini inentory/mycluster/
   ansible-playbook -i inventory/mycluster/inventory.ini cluster.yml
   ```

### Шаг 2: Проверка установки

1. Подключитесь к мастер-узлу:
   ```bash
   ssh root@<master_ip>
   ```
2. Проверьте состояние кластера:
   ```bash
   kubectl get nodes
   ```

## Установка дополнений

### Настройка Dashboard (опционально)

1. Установите Dashboard:
   ```bash
   kubectl apply -f https://raw.githubusercontent.com/kubernetes/dashboard/v2.7.0/aio/deploy/recommended.yaml
   ```
2. Создайте пользователя с доступом:
   ```bash
   kubectl create serviceaccount dashboard-admin -n kubernetes-dashboard
   kubectl create clusterrolebinding dashboard-admin --clusterrole=cluster-admin --serviceaccount=kubernetes-dashboard:dashboard-admin
   ```
3. Получите токен:
   ```bash
   kubectl -n kubernetes-dashboard describe secret $(kubectl -n kubernetes-dashboard get secret | grep dashboard-admin | awk '{print $1}')
   ```

## Завершение

Ваш кластер Kubernetes успешно установлен и настроен. Используйте `kubectl` для управления кластером.

