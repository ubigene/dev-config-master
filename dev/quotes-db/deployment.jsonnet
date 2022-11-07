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
              "limits": esm.ref('../__env__/k8s_resource_limits_db.json#service_limits'),
              "requests": esm.ref('../__env__/k8s_resource_limits_db.json#service_requests')
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
