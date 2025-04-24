from kubernetes import client, config
from lib import *

if __name__ == "__main__":

    # load config
    config.load_kube_config()
    objapi = client.CustomObjectsApi()

    # Get required list and map
    image_list = get_image_list(objapi)
    image_depo_dict = get_image_depo_dict(objapi)
    # print(image_list)
    # print(image_depo_dict)

    # Get list map
    # getting cr object more than once might have high overhead
    image_digest_dict = get_image_digest_dict(objapi)
    updepo_list = get_updepo_list(objapi)
    # print(image_digest_dict)
    # print(updepo_list)

    # Iterate through image list to update digests & updepo
    poll_udpate(objapi, image_list, image_digest_dict, updepo_list)

    pass
