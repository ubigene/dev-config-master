[
    {
        "name": "DB_USER",
        "value": "root"
    },
    {
        "name": "DB_PASSWORD",
        "valueFrom": esm.ref('../quotes-db/config.jsonnet#[?(@.name == "MYSQL_ROOT_PASSWORD")].valueFrom'),
    },
    {
        "name": "DB_NAME",
        "value": "quotesdb"
    },
    {
        "name": "DB_SERVICE_NAME",
        "value": esm.ref('../quotes-db/service.jsonnet#metadata.name')
    },
    {
        "name": "DB_PORT",
        "value": std.toString(esm.ref('../quotes-db/service.jsonnet#spec.ports[0].port'))
    },
    {
        "name": "MISSION",
        "value": "New mission"
    }
]