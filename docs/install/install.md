
# Install

## Install via helm

helm repo add kscp charts.tiagoposse.com/kscp
helm install kscp/kscp


The operator requires read/write/update/delete permissions on all secrets it needs to manage, while the injector only requires read access.

