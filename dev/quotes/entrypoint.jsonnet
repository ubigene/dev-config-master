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
            esm.ref('./route.jsonnet'),
            esm.ref('./service.jsonnet'),
        ]
    }
}