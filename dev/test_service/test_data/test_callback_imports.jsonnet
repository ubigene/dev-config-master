local esmlib = import './esm.libsonnet';
local ref = esmlib.ref(std.thisFile);
local esm = esmlib.esm(std.thisFile);
local closure_ns = esmlib.closure_object(42);

{
  // 'dict value expansion int': esm.ref('./parts.jsonnet#parts.columns[0].length'),
  'array indexing': ref('./parts.jsonnet#parts.columns[0].length'),
  'full file reference': ref('./simple.jsonnet#'),
  'key3': closure_ns.dash('meow'),
  'key4': closure_ns.slash('meow'),
  'JSONPath filter': esm.ref('./parts.jsonnet#parts.columns[?(@.name == "quantity")].description'),
  'Another JSONPath filter': esm.ref('./parts.jsonnet#parts.columns[?(@.name == \'name\')]'),
}