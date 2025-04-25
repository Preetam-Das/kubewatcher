import requests as req

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

def poll_udpate(objapi, image_list, image_digest_dict, updepo_list):
    """
    Poll registry for image digest change
    """

    for image in image_list:

        # print(image)
        new_digest = get_image_digest(image)

        # if digest map is empty
        if not image_digest_dict:
            # add digest and key to map
            image_digest_dict[image] = new_digest
            # update CR
            update_image_digest_dict_cr(objapi, image_digest_dict)
            # need to fix logic of polling resgistry here too
        # digest map not empty
        else:
            # digest map has image key
            if image in image_digest_dict:
                # same digest
                if (new_digest == image_digest_dict[image]):
                    # print(f'digest: {new_digest}')
                    pass
                else:
                    # new digest mark for update
                    # print(f'old: {image_digest_dict[image]}\nnew: {new_digest}')
                    print(f"to update {image}")
                    image_digest_dict[image] = new_digest
                    updepo_list.append(image)

                    # update CR
                    update_image_digest_dict_cr(objapi, image_digest_dict)
                    update_updepo_list_cr(objapi, updepo_list)
            # digest map doesn't have image key
            else:
                # add digest and key to map
                image_digest_dict[image] = new_digest
                # update CR
                update_image_digest_dict_cr(objapi, image_digest_dict)


def get_image_list(objapi):
    image_list_cr = objapi.get_namespaced_custom_object(
            "kubewatcher.internal",
            "v1alpha1",
            "default",
            "imagelists",
            "image-list"
            )

    image_list = image_list_cr["spec"]["images"]
    return image_list

def get_image_depo_dict(objapi):
    image_depo_dict_cr = objapi.get_namespaced_custom_object(
            "kubewatcher.internal",
            "v1alpha1",
            "default",
            "imagedepomaps",
            "image-depo-map"
            )
    image_depo_dict = image_depo_dict_cr["spec"]["mappings"]
    return image_depo_dict

def update_updepo_list_cr(objapi, updepo_list):
    # update
    # getting cr object more than once might have high overhead
    updepo_list_cr = get_updepo_list_cr(objapi)
    updepo_list_cr["spec"]["depos"] = updepo_list
    print(updepo_list)
    objapi.replace_namespaced_custom_object(
            "kubewatcher.internal",
            "v1alpha1",
            "default",
            "updepolists",
            "updepo-list",
            updepo_list_cr
            )

def update_image_digest_dict_cr(objapi, image_digest_dict):
    # update
    # getting cr object more than once might have high overhead
    cr = get_image_digest_dict_cr(objapi)
    # print(cr["spec"]["mappings"])
    cr["spec"]["mappings"] = image_digest_dict
    # print(cr["spec"]["mappings"])
    objapi.replace_namespaced_custom_object(
            "kubewatcher.internal",
            "v1alpha1",
            "default",
            "imagedigestmaps",
            "image-digest-map",
            cr
            )
    # print(cr["spec"]["mappings"])

def get_updepo_list_cr(objapi):
    updepo_list_cr = objapi.get_namespaced_custom_object(
            "kubewatcher.internal",
            "v1alpha1",
            "default",
            "updepolists",
            "updepo-list"
            )
    return updepo_list_cr

def get_image_digest_dict_cr(objapi):
    image_digest_dict_cr = objapi.get_namespaced_custom_object(
            "kubewatcher.internal",
            "v1alpha1",
            "default",
            "imagedigestmaps",
            "image-digest-map"
            )
    return image_digest_dict_cr

def get_updepo_list(objapi):
    cr = get_updepo_list_cr(objapi)
    updepo_list = cr["spec"]["depos"]
    return updepo_list

def get_image_digest_dict(objapi):
    cr = get_image_digest_dict_cr(objapi)
    image_digest_dict = cr["spec"]["mappings"]
    return image_digest_dict
