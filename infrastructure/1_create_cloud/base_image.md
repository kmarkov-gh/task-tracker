### **Создание базового образа Debian в OpenNebula**

---

#### **1. Цель**
Создать базовый образ Debian, который можно использовать для создания новых виртуальных машин (VM) в OpenNebula. Базовый образ содержит минимальную конфигурацию Debian и необходимые настройки для удобного развёртывания.

---

#### **2. Предварительные требования**
- OpenNebula установлен и настроен.
- Доступ к хранилищу (`default datastore`) для сохранения образов.
- Доступ к ISO-образу Debian (например, `debian-12.8.0-amd64-netinst.iso`).

---

### **Шаги по созданию базового образа**

---

#### **Шаг 1: Установка виртуальной машины**

1. **Создайте VM для установки Debian:**
   - Убедитесь, что ISO-образ Debian доступен в OpenNebula.
   - Создайте шаблон VM с ISO-образом для установки Debian:
     ```bash
     onetemplate create <<EOF
     NAME = "Debian-Installer-Template"
     MEMORY = "2048"
     CPU = "1"
     VCPU = "2"

     OS = [
       BOOT = "disk0"
     ]

     DISK = [
       IMAGE = "Debian-12-Netinst",  # Укажите имя ISO
       IMAGE_UNAME = "oneadmin",
       DEV_PREFIX = "sd",
       TYPE = "CDROM"
     ]

     DISK = [
       SIZE = "20480",  # 20 GB диск для установки ОС
       DEV_PREFIX = "vd",
       FORMAT = "qcow2",
       TYPE = "FS"
     ]

     NIC = [
       NETWORK = "admin_net",
       NETWORK_UNAME = "oneadmin"
     ]

     GRAPHICS = [
       LISTEN = "0.0.0.0",
       TYPE = "VNC"
     ]
     EOF
     ```

2. **Инстанцируйте виртуальную машину из шаблона:**
   ```bash
   onetemplate instantiate <TEMPLATE_ID> --name "Debian-Installer-VM"
   ```

3. **Установите Debian:**
   - Подключитесь к VM через VNC.
   - Установите Debian на диск (обычно `vda`).
   - Установите только минимальные пакеты, чтобы система оставалась лёгкой.

---

#### **Шаг 2: Подготовка базового образа**

1. **Удалите специфичные данные:**
   - Удалите сетевые правила:
     ```bash
     sudo rm -f /etc/udev/rules.d/70-persistent-net.rules
     ```
   - Очистите историю:
     ```bash
     history -c
     ```

2. **Установите обновления и необходимые пакеты:**
   ```bash
   sudo apt update && sudo apt upgrade -y
   sudo apt install qemu-guest-agent -y
   ```

3. **Выключите VM:**
   ```bash
   sudo poweroff
   ```

---

#### **Шаг 3: Создание базового образа**

1. **Сохраните диск VM как образ:**
   - Найдите ID VM и диска:
     ```bash
     onevm show <VM_ID>
     ```
     Например:
     ```text
     DISK=[
       DISK_ID="1",
       SIZE="20G",
       TARGET="vda",
       TYPE="FS"
     ]
     ```
   - Сохраните диск как образ:
     ```bash
     onevm disk-saveas <VM_ID> 1 "Base Debian Image"
     ```

2. **Проверьте созданный образ:**
   ```bash
   oneimage list
   ```

---

#### **Шаг 4: Использование базового образа**

1. **Создайте шаблон для новых VM:**
   ```bash
   onetemplate create <<EOF
   NAME = "Debian-Base-Template"
   MEMORY = "2048"
   CPU = "1"
   VCPU = "2"

   OS = [
     BOOT = "disk0"
   ]

   DISK = [
     IMAGE = "Base Debian Image",
     IMAGE_UNAME = "oneadmin"
   ]

   NIC = [
     NETWORK = "admin_net",
     NETWORK_UNAME = "oneadmin"
   ]

   GRAPHICS = [
     LISTEN = "0.0.0.0",
     TYPE = "VNC"
   ]
   EOF
   ```

2. **Инстанцируйте VM из нового шаблона:**
   ```bash
   onetemplate instantiate <TEMPLATE_ID> --name "New Debian VM"
   ```

3. **Подключитесь и начните использовать новую VM.**

---

### **Шаги по обновлению базового образа**

1. **Инстанцируйте VM из базового образа:**
   ```bash
   onetemplate instantiate <TEMPLATE_ID> --name "Base Image Update VM"
   ```

2. **Внесите изменения:**
   - Обновите систему:
     ```bash
     sudo apt update && sudo apt upgrade -y
     ```
   - Установите/удалите пакеты.

3. **Сохраните обновлённый диск обратно в образ:**
   ```bash
   onevm disk-saveas <VM_ID> 0 "Base Debian Image"
   ```

---

### **Примечания**

- **Резервное копирование**: Перед обновлением образа создавайте его копию:
  ```bash
  oneimage clone <IMAGE_ID> "Backup Debian Image"
  ```

- **Оптимизация**: Убедитесь, что базовый образ содержит только минимально необходимые пакеты.

---
Имиджи получилось создать только так:
```bash
   root@opennebula-fe1:~# cat debian_image.xml
    <IMAGE>
        <NAME>Base Debian Image</NAME>
        <PATH>/var/tmp/base-debian-image.qcow2</PATH>
        <TYPE>OS</TYPE>
        <PERSISTENT>YES</PERSISTENT>
        <DATASTORE>1</DATASTORE>
    </IMAGE>
    root@opennebula-fe1:~# oneimage create -d 1 debian_image.xml
  ``` 
