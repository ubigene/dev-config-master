local esm = import '../../lib/esm_test.libsonnet';

{
  'dict value expansion int': esm.ref('./lib/parts.jsonnet#parts.columns[0].length'),
}