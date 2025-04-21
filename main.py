from kubernetes import client, config
from mylib import *

if __name__ == "__main__":
    config.load_kube_config()
    api = client.AppsV1Api()
    image_depo_dict = get_image_depo_dict(api, "default")
    image_digest_dict = get_image_digest_dict(image_depo_dict)
    poll_registry(image_digest_dict)
