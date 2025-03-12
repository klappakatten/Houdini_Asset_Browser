import hou, math
from . import utility

def create_import_nodes(asset):
    # CTRL-Z WHOLE METHOD
    with hou.undos.group("Create_Import_Nodes"):
        textures = asset.textures
        mesh = asset.mesh
        name = asset.name
        name = name.strip().lower().replace(" ","_")

        # Create Nodes
        obj = hou.node("/obj")
        pane_tab_path = obj.path()

        #Find network pane & get path
        for pane in hou.ui.paneTabs():
            if pane.type() == hou.paneTabType.NetworkEditor:
                pane_tab_path = pane.pwd().path()
                break

        if pane_tab_path == obj.path():
            geo_node = obj.createNode("geo", name)
        else:
            geo_node = hou.node(pane_tab_path)

        # OTLS
        otl_files = [
            utility.get_dir(__file__) + "/otls/sop_TheAssetBrowserMaterial.otl",
            utility.get_dir(__file__) + "/otls/sop_TheAssetBrowserModel.otl"]
        installed_hda = hou.hda.loadedFiles()
        for otl in otl_files:
            if otl not in installed_hda:
                hou.hda.installFile(otl)

        tab_node = geo_node.createNode("TheAssetBrowserModel")
        tab_node.allowEditingOfContents(True)
        tab_node.cook()

        transform_node = hou.node(tab_node.path() + "/transform1")
        material_node = hou.node(tab_node.path() + "/material1")
        normal_node = hou.node(tab_node.path() + "/normal1")
        mat_net = hou.node(tab_node.path() + "/matnet1")
        shader_node = hou.node(mat_net.path() + "/principledshader1")
        output_node = hou.node(tab_node.path() + "/output0")
        file_node = hou.node(tab_node.path() + "/filemerge1")

        file_node.parm("filelist1").set(mesh)

        if asset.mesh == "default" or asset.mesh == "":
            file_node.destroy()
            file_node = tab_node.createNode("testgeometry_shaderball::2.0")
            file_node.parm("ry").set(-90)
            transform_node.parm("scale").set(1)

        # Set Inputs
        transform_node.setInput(0, file_node)
        normal_node.setInput(0,transform_node)
        material_node.setInput(0, normal_node)
        output_node.setInput(0, material_node)

        # Set Materials
        material_node.parm("shop_materialpath1").set(shader_node.path())

        set_textures(textures, shader_node)

        tab_node.layoutChildren()
        obj.layoutChildren()
        geo_node.layoutChildren()

        hou.clearAllSelected()

        output_node.setDisplayFlag(True)
        output_node.setRenderFlag(True)
        tab_node.setDisplayFlag(True)
        tab_node.setRenderFlag(True)
        return tab_node


def set_textures(textures, shader_node):
    for texture in textures:
        texture = texture.lower()
        file_ending_removed = texture.replace(".jpg", "")
        file_ending_removed = file_ending_removed.replace(".png", "")
        if "color" in texture.lower() or file_ending_removed.endswith("_c"):
            shader_node.parm("basecolor_useTexture").set(True)
            shader_node.parm("basecolor_texture").set(texture)
            shader_node.setParms({
                "basecolorr": 1,
                "basecolorg": 1,
                "basecolorb": 1
            })
        if "rough" in texture.lower() or file_ending_removed.endswith("_r"):
            shader_node.parm("rough").set(1)
            shader_node.parm("ior").set(1)
            shader_node.parm("rough_useTexture").set(True)
            shader_node.parm("rough_texture").set(texture)
        if "metallic" in texture.lower() or file_ending_removed.endswith("_m"):
            shader_node.parm("metallic_useTexture").set(True)
            shader_node.parm("metallic_texture").set(texture)
        if "transparency" in texture.lower() or file_ending_removed.endswith("_t"):
            shader_node.parm("transcolor_useTexture").set(True)
            shader_node.parm("transcolor_texture").set(texture)
        if "normal" in texture.lower() or file_ending_removed.endswith("_n"):
            shader_node.parm("baseBumpAndNormal_enable").set(True)
            shader_node.parm("baseNormal_texture").set(texture)
        if "ao" in texture.lower() or file_ending_removed.endswith("_ao"):
            shader_node.parm("occlusion_useTexture").set(True)
            shader_node.parm("occlusion_texture").set(texture)


def switch_asset(asset_item):
    with hou.undos.group("Switch_Asset"):
        selected_nodes = hou.selectedNodes()
        for node in selected_nodes:
            if node.type().name() == "filemerge::2.0" and asset_item.mesh != "default":
                node.parm("filelist1").set(asset_item.mesh)
            if node.type().name() == "principledshader::2.0":
                set_textures(asset_item.textures, node)


def switch_material():
    pass
def frame_object_with_camera(camera, target, margin=3):
    fov = math.radians(camera.parm("focal").eval())

    bbox = target.geometry().boundingBox()
    center = bbox.center()
    size = bbox.sizevec()

    average_size = (size.x() + size.y() + size.z()) / 3
    distance = (average_size * margin) / math.tan(fov)

    # Camera transform
    camera_y_offset = average_size
    camera_x_offset = -average_size
    camera_z_offset = 0

    if size.y() == max(size.x(), size.y(), size.z()):
        camera_z_offset = size.y()
        camera_y_offset = size.y()

    cam_position = (center.x() + camera_x_offset, center.y() + camera_y_offset, center.z() + distance + camera_z_offset)

    camera.parmTuple("t").set(cam_position)

    # Camera direction
    cam_position = hou.Vector3(cam_position)
    target_position = hou.Vector3(center)
    direction = (target_position - cam_position).normalized()

    pitch = math.degrees(math.asin(direction.y()))
    yaw = math.degrees(math.atan2(-direction.x(), -direction.z()))

    # Rotation
    camera.parm("rx").set(pitch)
    camera.parm("ry").set(yaw)
    camera.parm("rz").set(0)

def generate_missing_thumbnails(assets):
    # Prevent undo actions
    with hou.undos.disabler():
        obj = hou.node("/obj")
        ropnet = obj.createNode("ropnet")
        light_source = obj.createNode("hlight::2.0")
        camera = obj.createNode("cam")
        opengl = ropnet.createNode("opengl")

        opengl.parm("camera").set(camera.path())
        opengl.parm("gamma").set(1.7)
        opengl.parm("usehdr").set(0)

        light_source.parm("light_type").set("distant")
        light_source.parm("rx").set(-25)
        light_source.parm("ry").set(-45)
        light_source.parm("light_intensity").set(2.5)
        light_source.parm("shadow_intensity").set(.5)

        render_thumbnails(assets,opengl,light_source,camera,2)

        ropnet.destroy()
        light_source.destroy()
        camera.destroy()

# DO SEVERAL PASSES TO FIX GREY RENDER ISSUES WITH OPENGL
def render_thumbnails(assets, opengl, light_source, camera, passes):
    for i in range(passes):
        for asset in assets:
            if "thumbnail" not in str(asset.textures):
                subnet = create_import_nodes(asset)

                opengl.parm("vobjects").set(subnet.parent().path())
                opengl.parm("alights").set(light_source.path())
                render = opengl.parm("execute")

                frame_object_with_camera(camera, subnet)

                dir_name = utility.get_dir(asset.mesh)
                if dir_name in ["", "default", None]:
                    dir_name = utility.get_dir(asset.textures[0])

                file_path = f"{dir_name}/{asset.name}_thumbnail.png"
                file_path = file_path.replace(" ", "_")
                output_file = file_path
                opengl.parm("picture").set(output_file)

                render.pressButton()

                subnet.parent().destroy()

                print(f"{asset.name} thumbnail render pass {i+1}/{passes}")

