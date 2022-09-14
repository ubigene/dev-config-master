{
  "apiVersion": "v1",
  "kind": "Service",
  "metadata": esm.ref('./deployment.jsonnet#metadata'),
  "spec": {
    "ports": [
      {
        "name": "%s-%s" % [self.port, std.asciiLower(self.protocol)],
        "port": self.targetPort,
        "protocol": esm.ref('./deployment.jsonnet#spec.template.spec.containers[0].ports[0].protocol'),
        "targetPort": esm.ref('./deployment.jsonnet#spec.template.spec.containers[0].ports[0].containerPort')
      },
    ],
    "selector": esm.ref('./deployment.jsonnet#spec.template.metadata.labels'),
    "sessionAffinity": "None",
    "type": "ClusterIP"
  }
}