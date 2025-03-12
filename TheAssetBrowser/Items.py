class Asset:
    def __init__(self, path, name, mesh, textures, icon, tags):
        self.path = path
        self.name = name
        self.mesh = mesh
        self.textures = textures
        self.icon = icon
        self.tags = tags

    def __str__(self):
        return f"<[ASSET={self.path}MESH={self.mesh}TEXTURES={self.textures}ICON={self.icon}TAGS={self.tags}]>"

    def __repr__(self):
        return f"<[ASSET={self.path}MESH={self.mesh}TEXTURES={self.textures}ICON={self.icon}TAGS={self.tags}]>"


class Category:
    def __init__(self, path, name,parent=None):
        self.path = path
        self.name = name
        self.assets = []
        self.sub_categories = []
        self.parent = parent

    def add_asset(self,asset):
        self.assets.append(asset)

    def add_sub_category(self, category):
        self.sub_categories.append(category)

    def __str__(self):
        return f"\nCATEGORY={self.name} ASSETS={len(self.assets)} SUBCATEGORIES={len(self.sub_categories)}"
    def __repr__(self):
        return f"\nCATEGORY={self.name} ASSETS={len(self.assets)} SUBCATEGORIES={len(self.sub_categories)}"

class AssetManager:
    def __init__(self):
        self.assets = []
        self.categories = []

    def add_asset(self, asset):
        self.assets.append(asset)

    def add_category(self, category):
        self.categories.append(category)

    def __str__(self):
        return f"\nCATEGORIES:{self.categories}ASSETS:{self.assets}"

    def __repr__(self):
        return f"\nCATEGORIES:{self.categories}ASSETS:{self.assets}"