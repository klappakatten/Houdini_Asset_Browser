# Houdini Asset Browser

To install assetbrowser in houdini:

1. Add files to documents/houdini20.5/packages
2. Make sure TheAssetBrowser.json is outside of TheAssetBrowsr folder
3. set default path in TheAssetBrowser/settings.json (optional)
4. In houdini open new Pane Tab Type --> click The Asset Browser

<h3>Folder structure</h3>
Folder structure is based on the quixel bridge for seamless support
<pre>
root
  |
  |--Category
  |      |
  |      |-----asset
  |               |
  |               |-----asset.fbx
  |               |
  |               |-----asset_albedo.png
  |               |
  |               |-----asset_normal.png
  |               |
  |               |-----asset_.._.png                 
  |               |
  |               |-----thumbnail.png
  |               |
  |               |-----asset_metadata.json
  |
  |--Category
         |
         |-----asset
                  |
                  |-----asset.fbx
                  |
                  |-----asset_albedo.png
                  |
                  |-----asset_normal.png
                  |
                  |-----asset_.._.png                 
                  |
                  |-----thumbnail.png
                  |
                  |-----asset_metadata.json
</pre>
