
{
  ref(x)::
        local uri = std.stripChars(x, " ");
        local parts = std.split(uri, "#");
        // std.extVar(parts[0]).cat.paws[0].kind;
        local imp = import parts[0];
        std.extVar(uri),
}

