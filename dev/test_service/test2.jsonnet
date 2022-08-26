local esm = import '../../lib/esm.libsonnet';

{
  'dict value expansion int': esm.ref('./lib/parts.jsonnet#parts.columns[0].length'),
  'dict value expansion string': esm.ref('./lib/parts.jsonnet#parts.columns[1].name'),
  'dict value expansion dict': esm.ref('./lib/parts.jsonnet#parts'),
  'dict value expansion file': esm.ref('./lib/simple.jsonnet'),
  'JSONPath filter': esm.ref('./lib/parts.jsonnet#parts.columns[?(@.name == "quantity")].description'),
  'test': esm.ref('./lib/parts.jsonnet#parts.columns[?(@.name == \'quantity\')].description'),
  'test2': std.merge(esm.ref('./lib/parts.jsonnet#parts.columns[?(@.name == \'quantity\')]'), {name: "(meow)"}),
}