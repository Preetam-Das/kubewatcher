import requests as req
from kubernetes import watch

res_ver = 0

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
            if image not in image_depo_dict:
                image_list.append(image)
                image_depo_dict[container.image] = deponame

    return (image_list, image_depo_dict)

def get_image_digest_dict(image_depo_dict):
    """
    Get a map of image vs digest
    """
    image_digest_dict = dict()

    for image in image_depo_dict:

        digest = get_image_digest(image)

        if image not in image_digest_dict:
            image_digest_dict[image] = digest # anyway to avoid storing whole 72 bytes here?

        return image_digest_dict

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

def watch_depo(api, image_list, image_depo_dict):
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
                        image_depo_dict[container.image] = deponame

                # call to update CRs
                # call to one shot poll job

            case "DELETED":
                print("DELETED %s" % deponame)
                for container in containers:
                    image = container.image
                    if image in image_depo_dict:
                        del image_depo_dict[container.image]
                    if image in image_list:
                        image_list.remove(image)

                # call to update CRs

            # TODO: Handle MODIFIED

def watch_redepo_req(image_list):
    print("Watching for reqdeploy requests. - dummy implementation")
    while True:
        pass

def getimage_list_cr(objapi):
    image_list_cr = objapi.get_namespaced_custom_object(
            "kubewatcher.internal",
            "v1alpha1",
            "default",
            "imagelists",
            "image-list"
            )
    return image_list_cr

def update_image_list_cr(objapi, imagelist, image_list_cr):
    # update
    image_list_cr["spec"]["images"] = imagelist
    objapi.replace_namespaced_custom_object(
            "kubewatcher.internal",
            "v1alpha1",
            "default",
            "imagelists",
            "image-list",
            image_list_cr
            )

def populate_imagelist(objapi, imagelist):
    """
    Populate empty imagelist instance
    """
    # get
    image_list_cr = getimage_list_cr(objapi)
    update_image_list_cr(objapi, imagelist, image_list_cr)
