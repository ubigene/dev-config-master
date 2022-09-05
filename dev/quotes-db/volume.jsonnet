{
  "apiVersion": "v1",
  "kind": "PersistentVolumeClaim",
  "metadata": {
    "name": "mysqlvolume"
  },
  "spec": {
    "resources": {
      "requests": {
        "storage": "5Gi"
      }
    },
    "volumeMode": "Filesystem",
    "accessModes": [
      "ReadWriteOnce"
    ]
  }
}
