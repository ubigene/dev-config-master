
{
    cat(x)::
        local uri = std.stripChars(x, " ");
        std.native('ref')(uri, std.thisFile),
    ref(base)::
        function(rel) std.native('ref')(rel, base),
    esm(base)::
        {
            ref(rel): std.native('ref')(rel, base),
        },
    closure_object(base)::
        {
            dash(x): base + '/' + x,
            slash(x): base + '-' + x,
        },

}

