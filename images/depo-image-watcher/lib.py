import requests as req
from kubernetes import watch, client
from time import sleep
import datetime

res_ver = 0

def get_cron_job(batchapi):
    name = "registry-watcher"
    namespace = "default"

    cronjob_list = batchapi.list_namespaced_cron_job(namespace = namespace, \
            field_selector = f"metadata.name={name}")

    if cronjob_list.items:
        cronjob = cronjob_list.items[0]
        return cronjob

def do1(api, namespace):
    """
    Get a list of images & a map of image vs deployment

    TODO:
    Now its checking for only the default namespace.
    Later maybe check all namespaces that are not the
    internal system namespaces

    """
    depos = api.list_namespaced_deployment("default")
    global res_ver
    res_ver = depos.metadata.resource_version

    image_depo_dict = dict()
    image_list = list()

    for depo in depos.items:
        deponame = depo.metadata.name
        containers = depo.spec.template.spec.containers
        for container in containers:
            image = container.image

            if image not in image_list:
                image_list.append(image)

            if image not in image_depo_dict:
                image_depo_dict[image] = [deponame]
            elif deponame not in image_depo_dict[container.image]:
                image_depo_dict[image].append(deponame)

    return (image_list, image_depo_dict)

def get_apiep(image):
    """
    Construct docker hub api endpoint url from image name
    """
    apiep = "https://hub.docker.com/v2/namespaces/{}/repositories/{}/tags/{}"

    try: [namerepo, tag] = image.split(':')
    except:
        tag = "latest"
        namerepo = image

    try: [namespace, repository] = namerepo.split('/')
    except:
        namespace = "library"
        repository = namerepo

    return apiep.format(namespace, repository, tag)

def get_image_digest(image):
    """
    Get the digest of the image from docker registry
    """
    apiep = get_apiep(image)

    # error check needed
    respo = req.get(apiep).json()

    imagedata = respo['images'][0] # need to check for multiarch images too
    digest = imagedata['digest']

    return digest

def poll_registry(image_digest_dict):
    """
    Poll registry for image digest change
    """

    for image in image_digest_dict:

        new_digest = get_image_digest(image)

        if (new_digest == image_digest_dict[image]):
            print(f'digest: {new_digest}')
        else:
            # mark for update
            print(f'old: {image_digest_dict[image]}\nnew: {new_digest}')

def watch_depo(api, objapi, image_list, image_depo_dict):
    """
    Watch new deployment events and trigger CR and poller update
    """
    w = watch.Watch()
    for event in w.stream(api.list_namespaced_deployment, namespace="default", \
            watch=True, resource_version=res_ver):

        containers = event['object'].spec.template.spec.containers
        deponame = event['object'].metadata.name

        match event["type"]:

            case "ADDED":
                print("ADDED %s" % deponame)
                for container in containers:
                    image = container.image

                    if image not in image_list:
                        image_list.append(image)

                    if image not in image_depo_dict:
                        image_depo_dict[image] = [deponame]
                    elif deponame not in image_depo_dict[container.image]:
                        image_depo_dict[image].append(deponame)

                # call to update CRs
                populate_image_list(objapi, image_list)
                populate_image_depo_dict(objapi, image_depo_dict)
                # call to one shot poll job

            case "DELETED":
                print("DELETED %s" % deponame)
                for container in containers:
                    image = container.image

                    if image in image_depo_dict:
                        if deponame in image_depo_dict[image]:
                            image_depo_dict[image].remove(deponame)

                            # if the image has no assoicated depos
                            if not image_depo_dict[image]:
                                # delete the image
                                del image_depo_dict[image]
                                if image in image_list:
                                    image_list.remove(image)

                # call to update CRs
                populate_image_list(objapi, image_list)
                populate_image_depo_dict(objapi, image_depo_dict)

            # TODO: Handle MODIFIED

def get_image_list_cr(objapi):
    image_list_cr = objapi.get_namespaced_custom_object(
            "kubewatcher.internal",
            "v1alpha1",
            "default",
            "imagelists",
            "image-list"
            )
    return image_list_cr

def get_image_depo_dict_cr(objapi):
    image_depo_dict_cr = objapi.get_namespaced_custom_object(
            "kubewatcher.internal",
            "v1alpha1",
            "default",
            "imagedepomaps",
            "image-depo-map"
            )
    return image_depo_dict_cr

def update_image_list_cr(objapi, image_list, image_list_cr):
    # update
    image_list_cr["spec"]["images"] = image_list
    objapi.replace_namespaced_custom_object(
            "kubewatcher.internal",
            "v1alpha1",
            "default",
            "imagelists",
            "image-list",
            image_list_cr
            )

def update_image_depo_dict_cr(objapi, image_depo_dict, image_depo_dict_cr):
    # update
    image_depo_dict_cr["spec"]["mappings"] = image_depo_dict
    objapi.replace_namespaced_custom_object(
            "kubewatcher.internal",
            "v1alpha1",
            "default",
            "imagedepomaps",
            "image-depo-map",
            image_depo_dict_cr
            )

def populate_image_list(objapi, image_list):
    """
    Populate image-list instance
    """
    # get
    image_list_cr = get_image_list_cr(objapi)
    update_image_list_cr(objapi, image_list, image_list_cr)


def populate_image_depo_dict(objapi, image_depo_dict):
    """
    Populate image-depo-map instance
    """
    # get
    image_depo_dict_cr = get_image_depo_dict_cr(objapi)
    update_image_depo_dict_cr(objapi, image_depo_dict, image_depo_dict_cr)

def get_updepo_list(objapi):
    updepo_list_cr = objapi.get_namespaced_custom_object(
            "kubewatcher.internal",
            "v1alpha1",
            "default",
            "updepolists",
            "updepo-list"
            )

    updepo_list = updepo_list_cr["spec"]["depos"]
    return updepo_list

def get_image_digest_dict(objapi):
    image_digest_dict_cr = objapi.get_namespaced_custom_object(
            "kubewatcher.internal",
            "v1alpha1",
            "default",
            "imagedigestmaps",
            "image-digest-map"
            )
    image_digest_dict = image_digest_dict_cr["spec"]["mappings"]
    return image_digest_dict


def restart_depo(appapi, deponame):
    # update here
    depoobjlist = appapi.list_namespaced_deployment(namespace="default", \
            field_selector = f"metadata.name={deponame}")

    if depoobjlist.items:
        depoobj = depoobjlist.items[0]

        if (depoobj.metadata.name == deponame):
            ts = int(datetime.datetime.now().timestamp())
            print(f"updating {deponame} at {ts}")

            # Update Label
            depoobj.spec.template.metadata.labels["redeploy_timestamp"] = \
                     str(ts)
            # Patch
            appapi.patch_namespaced_deployment(
                    depoobj.metadata.name,
                    depoobj.metadata.namespace,
                    depoobj)

def get_updepo_list_cr(objapi):
    updepo_list_cr = objapi.get_namespaced_custom_object(
            "kubewatcher.internal",
            "v1alpha1",
            "default",
            "updepolists",
            "updepo-list"
            )
    return updepo_list_cr

def update_updepo_list_cr(objapi, updepo_list):
    # update
    # getting cr object more than once might have high overhead
    updepo_list_cr = get_updepo_list_cr(objapi)
    updepo_list_cr["spec"]["depos"] = updepo_list
    # print(updepo_list)
    objapi.replace_namespaced_custom_object(
            "kubewatcher.internal",
            "v1alpha1",
            "default",
            "updepolists",
            "updepo-list",
            updepo_list_cr
            )

def watch_redepo_req(objapi, appapi, image_depo_dict):

    print("Watching for reqdeploy requests. - dummy implementation")

    # loop forever
    while True:
        newimagelist = get_updepo_list(objapi)
        # while there is image to update
        while newimagelist:
            image = newimagelist.pop()
            # update the cr
            update_updepo_list_cr(objapi, newimagelist)
            print(f"got {image} to update")
            if (image in image_depo_dict):
                # for all depos where newimage
                for deponame in image_depo_dict[image]:
                    print(f"got {deponame} to update")
                    # update depo
                    restart_depo(appapi, deponame)

        sleep(1)


# depos = appapi.list_namespaced_deployment("default")
# for depo in depos.items:
#     for container in depo.spec.template.spec.containers:
#         print(container.image)
#         container.image = newimage
#         print(f'changing to {container.image}')
#         print('wait to reapply')
#         appapi.replace_namespaced_deployment(depo.metadata.name, depo.metadata.namespace, depo)
