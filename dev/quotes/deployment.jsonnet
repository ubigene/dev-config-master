{
  "kind": "Deployment",
  "apiVersion": "apps/v1",
  "metadata": {
    name: "quotes",
    "labels": {
      // "tier": "backend",
      "app": $.metadata.name,
    }
  },
  "spec": {
    "replicas": 1,
    "selector": {
      "matchLabels": $.spec.template.metadata.labels
    },
    "template": {
      "metadata": {
        "labels": $.metadata.labels
      },
      "spec": {
        "containers": [
          {
            "name": $.metadata.name,
            "env": esm.ref('./config.jsonnet'),
            image: esm.ref('./version.json#image'),
            "resources": {
              "limits": {
                "cpu": "1",
                "memory": "750Mi"
              },
              "requests": {
                "cpu": "10m",
                "memory": "64Mi"
              }
            },
            "imagePullPolicy": "Always",
            "ports": [
              {
                "containerPort": 10000,
                "protocol": "TCP"
              }
            ]
          }
        ]
      }
    }
  }
}