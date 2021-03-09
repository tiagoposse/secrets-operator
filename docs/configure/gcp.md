# GCP

## Requirements

Create service accounts

```
gcloud iam service-accounts create kscp-operator \
    --description="kscp-operator serviceaccount" \
    --display-name="kscp-operator"

gcloud iam service-accounts create kscp-injector \
    --description="kscp-injector serviceaccount" \
    --display-name="kscp-injector"
```

Grant workload identity permissions to the service account

```
gcloud iam service-accounts add-iam-policy-binding \
  --role roles/iam.workloadIdentityUser \
  --member "serviceAccount:$PROJECT_ID.svc.id.goog[kscp/kscp-operator]" \
  kscp-operator@$PROJECT_ID.iam.gserviceaccount.com

gcloud iam service-accounts add-iam-policy-binding \
  --role roles/iam.workloadIdentityUser \
  --member "serviceAccount:$PROJECT_ID.svc.id.goog[kscp/kscp-injector]" \
  kscp-injector@$PROJECT_ID.iam.gserviceaccount.com
```

Grant secret related permissions for both service accounts

```
gcloud projects add-iam-policy-binding --role="roles/secretmanager.secretVersionManager" $PROJECT_ID --member "serviceAccount:kscp-operator@$PROJECT_ID.iam.gserviceaccount.com

gcloud projects add-iam-policy-binding --role="roles/secretmanager.secretAccessor" $PROJECT_ID --member "serviceAccount:kscp-injector@$PROJECT_ID.iam.gserviceaccount.com
```


## Values

```
operator:
  serviceAccount:
    create: true
    annotations:
      iam.gke.io/gcp-service-account: ${OPERATOR_SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com

injector:
  serviceAccount:
    create: true
    annotations:
      iam.gke.io/gcp-service-account: ${INJECTOR_SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com

backends:
  gcp:
    enabled: true
    projectID: ${PROJECT_ID}
```
