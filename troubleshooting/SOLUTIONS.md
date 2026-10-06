# Kubernetes Troubleshooting Lab: Solutions & Post-Mortem Guide

This manual covers the structured 6-step troubleshooting methodology required by the final DevOps project evaluation.

---

## Troubleshooting Methodology Overview
When encountering an incident in Kubernetes, always follow this systematic workflow:
```text
1. Identify Issue   --->   2. Investigate Logs   --->   3. Find Root Cause
         |                                                       |
         v                                                       v
6. Document Post-Mortem <--   5. Verify Fix        <---   4. Apply Remediation
```

---

## Scenario 1: `ImagePullBackOff` / `ErrImagePull`
- **Manifest:** `troubleshooting/scenario1-broken-image.yaml`
- **Deployment:** `scenario1-broken-image`

### 1. Identify the Issue
Run `kubectl get pods -n taskboard`:
```text
NAME                                     READY   STATUS             RESTARTS   AGE
scenario1-broken-image-79f9798cf8-2xkl5   0/1     ImagePullBackOff   0          42s
```
The pod cannot start because the container runtime cannot pull the image.

### 2. Investigate Logs and Resources
Check Pod events:
```bash
kubectl describe pod -l troubleshooting=scenario1 -n taskboard
```
**Output snippet:**
```text
Events:
  Type     Reason     Age                From               Message
  ----     ------     ----               ----               -------
  Normal   Scheduled  45s                default-scheduler  Successfully assigned taskboard/scenario1-broken-image to node-1
  Normal   Pulling    12s (x3 over 44s)  kubelet            Pulling image "ghcr.io/devops-capstone/taskboard-backend:v99.9.9-nonexistent"
  Warning  Failed     11s (x3 over 43s)  kubelet            Failed to pull image "ghcr.io/devops-capstone/taskboard-backend:v99.9.9-nonexistent": rpc error: code = NotFound
  Warning  Failed     11s (x3 over 43s)  kubelet            Error: ErrImagePull
  Normal   BackOff    1s (x4 over 42s)   kubelet            Back-off pulling image "ghcr.io/devops-capstone/taskboard-backend:v99.9.9-nonexistent"
```

### 3. Find Root Cause
The image tag `v99.9.9-nonexistent` does not exist in the registry (or image pull secrets are missing for private repositories).

### 4. Fix the Issue
Patch the deployment to use a valid, existing image tag:
```bash
kubectl set image deployment/scenario1-broken-image app=python:3.12-slim -n taskboard
```

### 5. Verify the Solution
```bash
kubectl get pods -l troubleshooting=scenario1 -n taskboard
```
Status changes to `Running` (1/1).

---

## Scenario 2: `CrashLoopBackOff` (Database Connectivity Failure)
- **Manifest:** `troubleshooting/scenario2-crashloop-db.yaml`

### 1. Identify the Issue
```bash
kubectl get pods -l troubleshooting=scenario2 -n taskboard
```
Status shows `CrashLoopBackOff`, and restart count increments every few seconds.

### 2. Investigate Logs and Resources
Inspect container stdout/stderr logs:
```bash
kubectl logs -l troubleshooting=scenario2 -n taskboard --tail=50
```
**Output snippet:**
```text
Connecting to DB at postgres-broken-host:5432...
CRITICAL: Host postgres-broken-host not found!
```

### 3. Find Root Cause
The container is trying to connect to a non-existent DNS hostname `postgres-broken-host`. In Kubernetes, services must be reached using the valid in-cluster CoreDNS name (e.g. `taskboard-postgres.taskboard.svc.cluster.local` or `taskboard-postgres`).

### 4. Fix the Issue
Update the container command or environment variables to point to the correct PostgreSQL service:
```bash
kubectl set env deployment/scenario2-crashloop-db DATABASE_URL="postgresql+psycopg://taskboard:taskboard@taskboard-postgres:5432/taskboard" -n taskboard
```

### 5. Verify the Solution
Check logs and status:
```bash
kubectl get pods -l troubleshooting=scenario2 -n taskboard
```
Pod maintains `Running` state without restarts.

---

## Scenario 3: `Service Selector Mismatch` (Empty Endpoints / No Traffic)
- **Manifest:** `troubleshooting/scenario3-service-selector-mismatch.yaml`

### 1. Identify the Issue
Clients attempting to reach `scenario3-broken-service:8080` receive connection timeout or refused, even though the backend pod is `Running`.

### 2. Investigate Logs and Resources
Check service details and endpoints:
```bash
kubectl get svc scenario3-broken-service -n taskboard
kubectl get endpoints scenario3-broken-service -n taskboard
```
**Output snippet:**
```text
NAME                       ENDPOINTS   AGE
scenario3-broken-service   <none>      2m
```
Endpoints list is `<none>`!

Check pod labels:
```bash
kubectl get pods --show-labels -n taskboard
```
Pod label is `app=taskboard-backend-actual`, while Service selector is:
```bash
kubectl get svc scenario3-broken-service -n taskboard -o jsonpath="{.spec.selector}"
# Output: {"app":"taskboard-backend-typo-label"}
```

### 3. Find Root Cause
Label selector mismatch between the Kubernetes Service and the Pods. The Service is selecting `taskboard-backend-typo-label`, but the pods are labeled `taskboard-backend-actual`.

### 4. Fix the Issue
Patch the service selector:
```bash
kubectl patch svc scenario3-broken-service -n taskboard -p '{"spec":{"selector":{"app":"taskboard-backend-actual"}}}'
```

### 5. Verify the Solution
Check endpoints again:
```bash
kubectl get endpoints scenario3-broken-service -n taskboard
```
Now shows the Pod's private IP (e.g., `10.244.0.15:8080`). Traffic routes successfully.

---

## Scenario 4: `PersistentVolumeClaim Unbound / Pod Pending`
- **Manifest:** `troubleshooting/scenario4-unbound-pvc.yaml`

### 1. Identify the Issue
```bash
kubectl get pods -l app=scenario4-pending -n taskboard
```
Pod is stuck in `Pending` state indefinitely.

### 2. Investigate Logs and Resources
```bash
kubectl describe pod -l app=scenario4-pending -n taskboard
```
**Output snippet:**
```text
Events:
  Type     Reason            Age   From               Message
  ----     ------            ----  ----               -------
  Warning  FailedScheduling  30s   default-scheduler  0/1 nodes available: persistentvolumeclaim "scenario4-unbound-pvc" not found / unbound.
```

Inspect the PVC:
```bash
kubectl describe pvc scenario4-unbound-pvc -n taskboard
```
**Output snippet:**
```text
Events:
  Type     Reason               Age   From                         Message
  ----     ------               ----  ----                         -------
  Warning  ProvisioningFailed   40s   persistentvolume-controller  storageclass.storage.k8s.io "non-existent-aws-ebs-storageclass" not found
```

### 3. Find Root Cause
The PVC specified `storageClassName: non-existent-aws-ebs-storageclass`, which does not exist in the cluster.

### 4. Fix the Issue
Delete the bad PVC and recreate it using standard storage class or omitting `storageClassName` to use the cluster's default StorageClass (e.g. `standard` or `gp2` or `local-path`):
```bash
kubectl delete -f troubleshooting/scenario4-unbound-pvc.yaml
# Update storageClassName to default StorageClass
kubectl apply -f kubernetes/03-storage-pvc.yaml
```

### 5. Verify the Solution
```bash
kubectl get pvc -n taskboard
kubectl get pods -n taskboard
```
PVC becomes `Bound` and the Pod transitions from `Pending` to `Running`.

---

## Scenario 5: `Ingress 502 Bad Gateway` (Upstream Port Mismatch)
- **Manifest:** `troubleshooting/scenario5-ingress-port-mismatch.yaml`

### 1. Identify the Issue
Making a request through Ingress returns `502 Bad Gateway`:
```bash
curl -I -H "Host: taskboard.local" http://localhost/api/tasks
# HTTP/1.1 502 Bad Gateway
```

### 2. Investigate Logs and Resources
Check Ingress Controller logs:
```bash
kubectl logs -n ingress-nginx -l app.kubernetes.io/name=ingress-nginx --tail=50
```
**Output snippet:**
```text
[error] connect() failed (111: Connection refused) while connecting to upstream, client: 10.244.0.1, server: taskboard.local, request: "GET /api/tasks HTTP/1.1", upstream: "http://10.244.0.8:8080/api/tasks"
```
The Ingress is attempting to route to upstream port 8080!

Check backend service:
```bash
kubectl get svc taskboard-backend -n taskboard
```
The backend service port is 8000, not 8080!

### 3. Find Root Cause
Ingress resource has target port configured as `8080` instead of `8000`.

### 4. Fix the Issue
Edit the Ingress resource:
```bash
kubectl patch ingress taskboard-ingress -n taskboard --type='json' -p='[{"op": "replace", "path": "/spec/rules/0/http/paths/0/backend/service/port/number", "value": 8000}]'
```

### 5. Verify the Solution
```bash
curl -i -H "Host: taskboard.local" http://localhost/health
# HTTP/1.1 200 OK
# {"status":"UP"}
```
Ingress routes traffic cleanly with HTTP 200 OK.
