
# GCP

For this tutorial, (workload identity needs to be enabled in your cluster)[https://cloud.google.com/kubernetes-engine/docs/how-to/workload-identity#kubectl].


## Export names

```
export INJECTOR_SA_NAME=kscp-injector
export OPERATOR_SA_NAME=kscp-operator
export PROJECT_ID=<< PROJ_ID>>
```

## Create the service accounts

```
gcloud iam service-accounts create $OPERATOR_SA_NAME \
    --description="Service account used by the KSCP Operator to manage secrets" \
    --display-name="kscp-operator"
```

```
gcloud iam service-accounts create $INJECTOR_SA_NAME \
    --description="Service account used by the KSCP Injector to read secrets" \
    --display-name="kscp-injector"
```

## Grant project permissions

```
gcloud projects add-iam-policy-binding --role="roles/secretmanager.admin" ${PROJECT_ID} --member "serviceAccount:${OPERATOR_SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
gcloud projects add-iam-policy-binding --role="roles/secretmanager.accessor" ${PROJECT_ID} --member "serviceAccount:${INJECTOR_SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
```


## Grant workload permissions

```
gcloud iam service-accounts add-iam-policy-binding \
  --role roles/iam.workloadIdentityUser \
  --member "serviceAccount:${PROJECT_ID}.svc.id.goog[kscp/kscp-operator]" \
  ${OPERATOR_SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com
```

```
gcloud iam service-accounts add-iam-policy-binding \
  --role roles/iam.workloadIdentityUser \
  --member "serviceAccount:${PROJECT_ID}.svc.id.goog[kscp/kscp-injector]" \
  ${INJECTOR_SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com
```