### Установка OpenNebula

#### Требования
1. **Сервер виртуализации**:
   - Установлен KVM и libvirt.
   - Настроенная сеть с поддержкой мостов (bridge).
   - Образ Ubuntu 22.04 (`ubuntu-22.04.5-live-server-amd64.iso`).
2. **Сервер с установленным Ansible**:
   - Доступ к управляемым узлам.
   - Установленные зависимости для работы с проектом `one-deploy`.

---

### Шаг 1. Подготовка виртуальной машины

1. Создайте файл `inventory.yml` для определения параметров виртуальной машины:
    ```yaml
    all:
      hosts:
        vm1:
          ansible_host: localhost
          disksize: 200G
          ram: 20480
          vcpus: 20
    ```

2. Убедитесь, что структура проекта содержит:
   - Шаблон `cloudinit-user-data.j2` для cloud-init.
   - Образ Ubuntu в указанном пути.

3. Запустите плейбук для создания виртуальной машины:
   ```bash
   ansible-playbook -i inventory.yml main.yml
   ```

4. Убедитесь, что VM создана и настроена для работы.

---

### Шаг 2. Установка OpenNebula с помощью `one-deploy`

1. Склонируйте репозиторий [one-deploy](https://github.com/OpenNebula/one-deploy):
   ```bash
   git clone https://github.com/OpenNebula/one-deploy.git
   cd one-deploy
   ```

2. Установите зависимости Ansible:
   ```bash
   ansible-galaxy collection install -r requirements.yml
   ```

3. Настройте файл `local.yml`:
   - Укажите версию OpenNebula, пароль для администратора, параметры сети и IP-адреса узлов.

4. Запустите плейбук установки OpenNebula:
   ```bash
   ansible-playbook -i local.yml opennebula.deploy.main
   ```

5. Дождитесь завершения выполнения и убедитесь, что OpenNebula доступна по адресу `http://<frontend-ip>:2616`.

---

### Примечания
1. **Конфигурация сети**: 
   - Настройки bridge network в `local.yml` должны соответствовать вашей инфраструктуре.
2. **Проверка узлов**:
   - Убедитесь, что все узлы доступны через SSH и имеют необходимые зависимости.

---

### Завершение
После выполнения всех шагов OpenNebula будет развернута и готова к использованию. Вы можете управлять виртуальными машинами, сетями и хранилищем через веб-интерфейс или CLI.
