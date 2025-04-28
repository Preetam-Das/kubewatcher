# Kubewatcher (WIP)

Watches deployments and container images for change in tag digest and auto
re-deploys them. Tested in a 3 cluster VM setup and minikube.

#### Install with kubectl
```bash
kubectl apply -f https://github.com/Preetam-Das/kubewatcher/releases/download/v0.0.1/kubewatcher-install.yaml
```

#### Uninstall with kubectl
```bash
kubectl delete -f https://github.com/Preetam-Das/kubewatcher/releases/download/v0.0.1/kubewatcher-uninstall.yaml
```

#### To test

- Have a deployment running with a public container image.
- Install `kubewatcher`. It will auto detect the deployement.
- Make some visible changes in the deployment's image and push it to the registry.
- Wait for about a minute (see [note](#notes) 3) and it will auto deploy the
  deployment with the new updated image.

## How it works

The whole application (calling it `kubewatcher` for now) is designed to work
with the k8s environment as k8s pods. So the application that updates other
deployments is itself a deployment if it makes sense. This way it should be
possible that `kubewatcher` can *update itself* (not tested yet .. update it
seems to work).

There are two parts to it :
- a deployment that watches for other deployment, images & patches them for
  update
- a cronjob which polls dokcer registry

The communication between the two is done using several `Custom Resources` which
are basically lists and maps for storing container image, deployment, digest
data. Once the cronjob finds that an image got updated (see [note](#notes) 1) it notifies
the deployment using a to-update-images (names are all mangled up need to fix)
CR list and the deployment re-deploys all the deployments where the image is
present.

## NOTES

1. The current implementation checks for changes container image of the same
   tag, by comparing the digest values. It doesn't updates on every new tag
   pushed as tags don't directly relate to version numbers.

2. Currently `kubewatcher` only works for public repositories in the docker
   registry.

3. Rate limit for personal account is 200 per 6 hours, which is about 1 request
   per 2 minute. The current implementation polls the api 1 time in a minute. So
   if you keep this running for 6 hours you might get rate limited (NEED TO FIX
   THIS).

## TODO

Several improvements are possible. I am limited by time so anyone wishes to
work on these, please do and send a PR.

- Provide user customization like chosing what sepcific deployments or container
  images to watch for. Use config maps for this and read them in using the k8s
  api.

- Remove the cronjob component. I only did it because i was told to do so but
  this seems unnecessary so probably best to remove this and do the polling in
  the kubewatcher script only in a separate thread.

- Better documentation.

- Support for private images using secrets.

- Support for Kustomize and Helm.

- Error handling. Currently there is none.

- Async I/O. Cuz why not.

- Write this in Go. Everything in the cloud seems to be written in Go.

    .. and lot more.
