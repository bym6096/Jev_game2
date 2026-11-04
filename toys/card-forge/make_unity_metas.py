"""Write Unity .meta files (stable GUIDs derived from the file path) for everything under unity/JevOrbs/Assets that has none.

Without committed .meta files, every machine would invent its own GUIDs and scene / ScriptableObject references to the scripts would break.
Existing .meta files are never touched. Run it after adding files:   python3 make_unity_metas.py
"""
import hashlib, os

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.normpath(os.path.join(HERE, "..", "..", "unity", "JevOrbs", "Assets"))

TAIL = "  externalObjects: {}\n  userData: \n  assetBundleName: \n  assetBundleVariant: \n"
IMPORTERS = {
    ".cs": "MonoImporter:\n  externalObjects: {}\n  serializedVersion: 2\n  defaultReferences: []\n  executionOrder: 0\n  icon: {instanceID: 0}\n  userData: \n  assetBundleName: \n  assetBundleVariant: \n",
    ".asmdef": "AssemblyDefinitionImporter:\n" + TAIL,
    ".json": "TextScriptImporter:\n" + TAIL, ".md": "TextScriptImporter:\n" + TAIL, ".txt": "TextScriptImporter:\n" + TAIL,
}


def guid(rel):
    return hashlib.md5(("jevorbs-unity:" + rel.replace(os.sep, "/")).encode()).hexdigest()


def meta_for(rel, is_dir):
    if is_dir:
        body = "folderAsset: yes\nDefaultImporter:\n" + TAIL
    else:
        ext = os.path.splitext(rel)[1].lower()
        body = IMPORTERS.get(ext, "DefaultImporter:\n" + TAIL)
    return "fileFormatVersion: 2\nguid: %s\n%s" % (guid(rel), body)


def main():
    made = 0
    for root, dirs, files in os.walk(ASSETS):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        entries = [(d, True) for d in dirs] + [(f, False) for f in files if not f.endswith(".meta") and not f.startswith(".")]
        for name, is_dir in entries:
            path = os.path.join(root, name)
            if os.path.exists(path + ".meta"):
                continue
            with open(path + ".meta", "w", newline="\n") as f:
                f.write(meta_for(os.path.relpath(path, ASSETS), is_dir))
            made += 1
    print("wrote", made, "meta files")


if __name__ == "__main__":
    main()
