"""Provide the target filename that Make passes separately for normal diffs."""

def _klish_patch_inputs(ctx):
    for path, patch in ctx.attr.patches.items():
        source = ctx.path(patch)
        contents = ctx.read(source)
        if contents.startswith("diff --git "):
            ctx.symlink(source, path)
        else:
            # GNU patch strips the same first component from both patch formats.
            ctx.file(path, "Index: a/" + path.removesuffix(".diff") + "\n" + contents, executable = False)
    ctx.file("BUILD.bazel", "exports_files(" + repr(ctx.attr.patches.keys()) + ")\n")

klish_patch_inputs = repository_rule(
    implementation = _klish_patch_inputs,
    attrs = {"patches": attr.string_keyed_label_dict(allow_files = [".diff"], mandatory = True)},
)
