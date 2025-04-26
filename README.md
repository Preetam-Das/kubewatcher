# Kubewatcher (WIP)

Watches deployments and container images for change in tags and auto re-deploys
them.

#### Install with kubectl
```bash
kubectl apply -f https://github.com/Preetam-Das/kubewatcher/releases/download/v0.0.1/kubewatcher-install.yaml
```

#### Uninstall with kubectl:
```bash
kubectl delete -f https://github.com/Preetam-Das/kubewatcher/releases/download/v0.0.1/kubewatcher-uninstall.yaml
```

## How it works

The whole application (calling it `kubewatcher` for now) is designed to work
with the k8s environment as k8s pods. So the application that updates other
deployments is itself a deployment if it makes sense. This way it should be
possible that `kubewatcher` can *update itself* (not tested yet).

There are two parts to it :
- a cronjob which polls dokcer registry
- a deployment that watches for other deployment, images & patches them for
  update

The communication between the two is done using several `Custom Resources` which
are basically lists and maps for storing container image, deployment, digest
data. Once the cronjob finds that an image got updated (see notes) it notifies
the deployment using a to-update-images CR list and the deployment
re-deploys all the deployments where the image is present.

## NOTES

*Todo*
