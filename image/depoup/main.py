from kubernetes import client, config
from lib import *
from threading import Thread

if __name__ == "__main__":

    # load config
    config.load_kube_config()
    # config.load_incluster_config()
    api = client.AppsV1Api()
    objapi = client.CustomObjectsApi()
    batchapi = client.BatchV1Api()

    # Get required list and map
    image_list, image_depo_dict = do1(api, "default")
    # print(image_list)
    # print(image_depo_dict)

    # Put into CR
    populate_image_list(objapi, image_list)
    populate_image_depo_dict(objapi, image_depo_dict)

    # get poller cronjob
    cronjob = get_cron_job(batchapi)
    if cronjob:
        print(cronjob.metadata.name)

    # watch & update CRs for new depo
    # in seperate thread
    nd_watcher = Thread(target=watch_depo, args=(api, objapi, image_list, image_depo_dict), daemon=True)
    nd_watcher.start()

    # Get other list and map
    # updepo_list = get_updepo_list(objapi)
    # image_digest_dict = get_image_digest_dict(objapi)
    # print(updepo_list)
    # print(image_digest_dict)

    # watch for redeploy request
    appapi = api
    watch_redepo_req(objapi, appapi, image_depo_dict)
