dir="/mnt/grafana-data"
for i in 1; do 

   ssh k8s-worker-$i "[ -d $dir ] || mkdir -p $dir; chmod 755 $dir; chown nobody:nogroup $dir"
done
