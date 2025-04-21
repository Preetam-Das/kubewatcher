import requests as req

def get_image_depo_dict(api, namespace):
    """
    Get a map of image vs deployment

    TODO:
    Now its checking for only the default namespace.
    Later maybe check all namespaces that are not the
    internal system namespaces

    """
    depos = api.list_namespaced_deployment("default")

    image_depo_dict = dict()

    for depo in depos.items:
        deponame = depo.metadata.name
        containers = depo.spec.template.spec.containers
        for container in containers:
            image = container.image
            if image not in image_depo_dict:
                image_depo_dict[container.image] = deponame

    return image_depo_dict

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
