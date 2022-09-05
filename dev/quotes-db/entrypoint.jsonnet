{
    payload: {
        "apiVersion": "v1",
        "kind": "List",
        "metadata": {
            "resourceVersion": "",
            "selfLink": ""
        },
        "items": [
            esm.ref('./deployment.jsonnet'),
            esm.ref('./secret.jsonnet'),
            esm.ref('./service.jsonnet'),
            esm.ref('./volume.jsonnet'),
        ]
    }
}
