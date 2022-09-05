[
    {
        "name": "MYSQL_ROOT_PASSWORD",
        "valueFrom": {
            "secretKeyRef": {
                "name": esm.ref('./secret.jsonnet#metadata.name'), 
                "key": esm.ref("./secret.jsonnet#data.password~")
            }
        }
    },
]