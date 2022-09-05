{
  'array indexing': esm.ref('./parts.jsonnet#parts.columns[0].length'),
  'JSONPath filter': esm.ref('./parts.jsonnet#parts.columns[?(@.name == "quantity")].description'),
  'Another JSONPath filter': esm.ref('./parts.jsonnet#parts.columns[?(@.name == \'name\')]'),
}