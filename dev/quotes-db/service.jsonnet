{
  "apiVersion": "v1",
  "kind": "Service",
  "metadata": {
    "name": esm.ref('./deployment.jsonnet#metadata.name'),
  },
  "spec": {
    "selector": esm.ref('./deployment.jsonnet#spec.template.metadata.labels'),
    "ports": [
      {
        "protocol": "TCP",
        "port": self.targetPort,
        "targetPort": esm.ref('./deployment.jsonnet#spec.template.spec.containers[0].ports[0].containerPort'),
      }
    ]
  }
}
