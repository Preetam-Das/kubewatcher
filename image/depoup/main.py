from kubernetes import client, config
from lib import *
from threading import Thread

if __name__ == "__main__":

    # load config
    config.load_incluster_config()
    api = client.AppsV1Api()
    objapi = client.CustomObjectsApi()

    # Get required list and map
    image_list, image_depo_dict = do1(api, "default")
    print(image_list)
    print(image_depo_dict)

    # Put into CR
    populate_imagelist(objapi, image_list)
    print(image_list)

    # Create & start poller cronjob

    # watch & update CRs for new depo
    # in seperate thread
    nd_watcher = Thread(target=watch_depo, args=(api, image_list, image_depo_dict), daemon=True)
    nd_watcher.start()

    # watch for redeploy request
    watch_redepo_req(image_list)
