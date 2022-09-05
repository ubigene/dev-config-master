
{
    concat(str, times)::
        local stripped = std.stripChars(str, " ");
        std.join('', [stripped for _ in std.range(1, times)]),
    fn_closure(bound_attr)::
        function(attr) bound_attr + attr,
    obj_closure(base)::
        {
            dash(x): base + '/' + x,
            slash(x): base + '-' + x,
        },
}

