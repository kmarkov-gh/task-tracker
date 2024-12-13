kubectl create configmap postgres --from-file=postgres.conf --from-file=master.conf --from-file=replica.conf --from-file=pg_hba.conf \
	--from-file=create-replica-user.sh --dry-run=client -o yaml > 2_configmap.yaml
