{
  "apiVersion": "route.openshift.io/v1",
  "kind": "Route",
  "metadata": esm.ref('./deployment.jsonnet#metadata'),
  "spec": {
    "port": {
      "targetPort": esm.ref('./service.jsonnet#spec.ports[0].name'),
    },
    "to": {
      "kind": esm.ref('./service.jsonnet#kind'),
      "name": esm.ref('./service.jsonnet#metadata.name'),
    }
  }
}