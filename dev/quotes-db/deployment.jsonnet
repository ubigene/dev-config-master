{
  "apiVersion": "apps/v1",
  "kind": "Deployment",
  "metadata": {
    "name": "mysql"
  },
  "spec": {
    "replicas": 1,
    "selector": {
      "matchLabels": $.spec.template.metadata.labels,
    },
    "template": {
      "metadata": {
        "labels": {
          "app": "mysql",
          "tier": "database"
        }
      },
      "spec": {
        "containers": [
          {
            "name": self.image,
            env: esm.ref('./config.jsonnet'),
            image: esm.ref('./version.json#image'),
            "resources": {
              "limits": {
                "memory": "256Mi",
                "cpu": "500m",
              }
            },
            "ports": [
              {
                "containerPort": 3306
              }
            ],
            "volumeMounts": [
              {
                "name": $.spec.template.spec.volumes[0].name,
                "mountPath": "/var/lib/mysql"
              }
            ]
          }
        ],
        "volumes": [
          {
            "name": "mysqlvolume",
            "persistentVolumeClaim": {
              "claimName": esm.ref('./volume.jsonnet#metadata.name')
            }
          }
        ]
      }
    }
  }
}
