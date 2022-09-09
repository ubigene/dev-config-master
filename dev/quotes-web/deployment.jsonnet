{
  "kind": "Deployment",
  "apiVersion": "apps/v1",
  "metadata": {
    name: "quotesweb",
    "labels": {
      "app": $.metadata.name,
    }
  },
  "spec": {
    "replicas": 1,
    "selector": {
      "matchLabels": $.spec.template.metadata.labels,
    },
    "template": {
      "metadata": {
        "labels": {
          "app": $.metadata.labels
        }
      },
      "spec": {
        "containers": [
          {
            "name": $.metadata.name,
            image: esm.ref('./version.json#image'),
            "resources": {
              "limits": esm.ref('../__env__/k8s_resource_limits.json#service_limits'),
              "requests": esm.ref('../__env__/k8s_resource_limits.json#service_requests')
            },
            "imagePullPolicy": "Always",
            "ports": [
              {
                "containerPort": 3000,
                "protocol": "TCP"
              }
            ]
          }
        ]
      }
    }
  }
}