# Задаем IP мастеров и воркеров
masters = [f"192.168.2.{i}" for i in [148, 149]]
workers = [f"192.168.2.{i}" for i in [147, 134]]

# Проверяем четность количества мастеров
additional_etcd_worker = None
if len(masters) % 2 == 0:
    additional_etcd_worker = workers[0]  # Забираем первый воркер для ETCD

with open("inventory.ini", "w") as f:
    # Заголовок файла
    f.write("# This inventory describe a HA typology with stacked etcd (== same nodes as control plane)\n")
    f.write("# and worker nodes\n")
    f.write("# See https://docs.ansible.com/ansible/latest/inventory_guide/intro_inventory.html\n")
    f.write("# for tips on building your # inventory\n\n")
    f.write("# Configure 'ip' variable to bind kubernetes services on a different ip than the default iface\n")
    f.write("# We should set etcd_member_name for etcd cluster. The node that are not etcd members do not need to set the value,\n")
    f.write("# or can set the empty string value.\n")

    # Раздел мастеров
    f.write("[kube_control_plane]\n")
    for i, master in enumerate(masters, start=1):
        f.write(f"master{i} ansible_host={master} ip={master} etcd_member_name=etcd{i}\n")

    # Группа ETCD
    f.write("\n[etcd:children]\n")
    f.write("kube_control_plane\n")
    if additional_etcd_worker:
        f.write("\n[etcd]\n")
        for i, master in enumerate(masters, start=1):
            f.write(f"master{i} ansible_host={master} ip={master} etcd_member_name=etcd{i}\n")
        f.write(f"worker1 ansible_host={additional_etcd_worker} ip={additional_etcd_worker} etcd_member_name=etcd{len(masters) + 1}\n")

    # Группа воркеров
    f.write("\n[kube_node]\n")
    for i, worker in enumerate(workers, start=1):
        f.write(f"worker{i} ansible_host={worker} ip={worker}\n")
    if additional_etcd_worker:
        f.write(f"worker1 ansible_host={additional_etcd_worker} ip={additional_etcd_worker}\n")
