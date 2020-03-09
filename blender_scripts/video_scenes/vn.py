'''
When using draw_scenes.py to play this, clear should be set to false, and
inner_ear.blend should be open.
'''

import bpy
import collections
import math
from copy import deepcopy
#import imp

from constants import *
from helpers import *
#import scene
#imp.reload(scene)
from scene import Scene
import bobject
import svg_bobject
import tex_bobject
import tex_complex
import gesture

class TextScene(Scene):
    def __init__(self):
        self.subscenes = collections.OrderedDict([
            ('zoom', {'duration': 1000}),
            #('post_transplant', {'duration': 10}),\
        ])
        super().__init__()

    def play(self):
        super().play()
        #self.subscenes
        #self.duration
        #bpy.ops.wm.revert_mainfile()

        #These don't really need to be object methods ¯\_(ツ)_/¯
        #self.intro_card()
        #self.outline()
        #self.inner_ear_intro()
        #self.asymmetrical_inputs()
        self.long_term_symptoms()
        #self.transition_card()
        #self.end_card()

    def intro_card(self):
        logo = svg_bobject.SVGBobject(
            "UCSF_logo_signature",
            #location = (-5, 3.75, 0), #Centered position
            #scale = 0.26, #Centered scale
            location = [-10.675, -6.3, 0],
            scale = 0.128,
            color = 'color2',
            centered = True
        )
        baf = svg_bobject.SVGBobject(
            'BaFC_Arial',
            location = [4.325, -5.2, 0],
            scale = 1.85,
            color = 'color2',
            centered = True
        )
        vest = tex_bobject.TexBobject(
            '\\text{Vestibular Videos:}',
            location = [0, 4.5, 0],
            scale = 2,
            color = 'color2',
            centered = True,
            typeface = 'garamond'
        )
        title = tex_bobject.TexBobject(
            '\\text{Vestibular Neuritis}',
            location = [0, 1.5, 0],
            scale = 3.14,
            color = 'color2',
            centered = True,
            typeface = 'garamond'
        )
        vert = tex_bobject.TexBobject(
            '|',
            location = [-6.35, -4.74, 0],
            scale = [2, 5.32, 4],
            centered = True,
            color = 'color2',
        )

        logo.add_to_blender(appear_time = -1, animate = False)
        baf.add_to_blender(appear_time = -1, animate = False)
        vest.add_to_blender(appear_time = -1, animate = False)
        title.add_to_blender(appear_time = -1, animate = False)
        vert.add_to_blender(appear_time = -1, animate = False)

        for bobj in [logo, baf, vest, vert]:
            for handle in bobj.ref_obj.children:
                print(handle.name)
                print(handle.children[0].name)
                #For some reason, some handles have extra children
                try:
                    fade(
                        object = handle.children[0],
                        start_time = 0,
                        duration_time = 1,
                        fade_out = False
                    )
                except:
                    pass
        for bobj in [title]:
            for handle in bobj.ref_obj.children:
                print(handle.name)
                print(handle.children[0].name)
                #For some reason, some handles have extra children
                try:
                    fade(
                        object = handle.children[0],
                        start_time = 2,
                        duration_time = 1,
                        fade_out = False
                    )
                except:
                    pass

    def outline(self):
        vn = tex_bobject.TexBobject(
            "\\text{Vestibular Neuritis}",
            location = [0, 0, 0],
            centered = True,
            typeface = 'arial',
            scale = 3
        )
        vn.add_to_blender(
            appear_time = 0,
            subbobject_timing = [30] * 10 + [75] * 8
        )
        vn.move_to(
            new_location = [0, 3.5, 0],
            start_time = 2.5
        )

        acronym = tex_bobject.TexBobject(
            '\\bullet\\text{Vestibular system overview}',
            color = 'color2',
            typeface = 'arial'
        )
        cause = tex_bobject.TexBobject(
            '\\bullet\\text{Symptoms}',
            color = 'color2',
            typeface = 'arial'
        )
        treat = tex_bobject.TexBobject(
            '\\bullet\\text{Treatments}',
            color = 'color2',
            typeface = 'arial'
        )
        contents = tex_complex.TexComplex(
            acronym, cause, treat,
            location = [-9, 0.5, 0],
            scale = 1.5,
            multiline = True
        )
        contents.add_to_blender(
            appear_time = 4,
            subbobject_timing = [0, 35, 70]
        )
        contents.disappear(disappear_time = 7)
        #vn.disappear(disappear_time = 7)

        vn.move_to(
            new_location = [0, 5.5, 0],
            start_time = 6.5
        )

        itis = []
        for i in range(14, 18):
            itis.append(vn.lookup_table[0][i])
        for char in itis:
            char.color_shift(
                color = COLORS_SCALED[2],
                start_time = 8,
                duration_time = 2,
            )

        neur = []
        for i in range(10, 14):
            neur.append(vn.lookup_table[0][i])
        for char in neur:
            char.color_shift(
                color = COLORS_SCALED[2],
                start_time = 10.5,
                duration_time = 2,
            )

        vest = []
        for i in range(0, 10):
            vest.append(vn.lookup_table[0][i])
        for char in vest:
            char.color_shift(
                color = COLORS_SCALED[2],
                start_time = 13,
                duration_time = 2,
            )

        vn.disappear(disappear_time = 16)

    def inner_ear_intro(self):
        cam_bobj, cam_swivel = cam_and_swivel(
            cam_location = [0, 0, 5],
            cam_rotation_euler = [0, 0, 0],
            cam_name = "Camera Bobject",
            swivel_location = [0, 0, 0.25],
            swivel_rotation_euler = [math.pi / 2, 0, 0],
            swivel_name = 'Cam swivel',
            #control_sun = True
        )
        cam_swivel.add_to_blender(appear_time = -1)
        cam_bobj.ref_obj.children[0].data.clip_end = 200

        turn_green_time = 16.5

        zoom_out_time = 20.5

        turn_red_time = 22.5

        r_inner_ear = bpy.data.objects['inner ear_from microCT']
        brain = bpy.data.objects['Brain']
        v_nerve = bpy.data.objects['Vestibular nerve origin']
        to_keep = [r_inner_ear]
        for obj in bpy.data.objects:
            if obj not in to_keep:
                obj.hide = True
                obj.hide_render = True

        slots = r_inner_ear.material_slots
        v_sys_mats = [
            slots[1].material,
            slots[2].material,
            slots[3].material,
            slots[4].material
        ]
        coch_mat = slots[0].material

        for mat in v_sys_mats + [coch_mat]:
            print(mat)
            nodes = mat.node_tree.nodes
            mix = nodes['Mix Shader']
            mix.inputs[0].default_value = 0
            princ = nodes['Principled BSDF']
            color = princ.inputs[0]

            if mat != coch_mat:
                color.keyframe_insert(
                    data_path = 'default_value',
                    frame = turn_green_time * FRAME_RATE
                )
                color.default_value = [0, 1, 0, 1]
                color.keyframe_insert(
                    data_path = 'default_value',
                    frame = turn_green_time * FRAME_RATE + OBJECT_APPEARANCE_TIME
                )

        #Zoom out
        for thing in [brain, v_nerve]:
            thing.hide = True
            thing.hide_render = True
            thing.keyframe_insert(
                data_path = 'hide',
                frame = zoom_out_time * FRAME_RATE - 1
            )
            thing.hide = False
            thing.hide_render = False
            thing.keyframe_insert(
                data_path = 'hide',
                frame = zoom_out_time * FRAME_RATE
            )

            full_scale = list(thing.scale)
            thing.scale = [0, 0, 0]
            thing.keyframe_insert(
                data_path = 'scale',
                frame = zoom_out_time * FRAME_RATE - 1
            )
            thing.scale = full_scale
            thing.keyframe_insert(
                data_path = 'scale',
                frame = zoom_out_time * FRAME_RATE
            )

            nodes = thing.material_slots[0].material.node_tree.nodes
            mix = nodes['Mix Shader'].inputs[0]
            mix.default_value = 1
            mix.keyframe_insert(
                data_path = 'default_value',
                frame = (zoom_out_time + 1) * FRAME_RATE
            )
            mix.default_value = 0
            mix.keyframe_insert(
                data_path = 'default_value',
                frame = (zoom_out_time + 1) * FRAME_RATE + 2 * OBJECT_APPEARANCE_TIME
            )
            if thing == v_nerve:
                mix2 = nodes['Mix Shader.001'].inputs[0]
                mix2.default_value = 0
                mix2.keyframe_insert(
                    data_path = 'default_value',
                    frame = turn_red_time * FRAME_RATE
                )
                mix2.default_value = 1
                mix2.keyframe_insert(
                    data_path = 'default_value',
                    frame = turn_red_time * FRAME_RATE + 2 * OBJECT_APPEARANCE_TIME
                )

                em = nodes['Emission']
                color = em.inputs[0]
                color.default_value = [1, 1, 1, 1]
                color.keyframe_insert(
                    data_path = 'default_value',
                    frame = turn_red_time * FRAME_RATE
                )
                color.default_value = [1, 0, 0, 1]
                color.keyframe_insert(
                    data_path = 'default_value',
                    frame = turn_red_time * FRAME_RATE + 2 * OBJECT_APPEARANCE_TIME
                )


        cam_swivel.move_to(
            new_location = [0, 5.1, 4.5],
            start_time = zoom_out_time,
            end_time = zoom_out_time + 2 * OBJECT_APPEARANCE_TIME / FRAME_RATE
        )

        cam_swivel.move_to(
            new_angle = [math.pi / 2, 0, 70 * math.pi / 180],
            start_time = 14,
            end_time = 25
        )
        '''cam_swivel.move_to(
            new_angle = [math.pi / 2, 0, 0],
            start_time = turn_red_time,
            end_time = turn_red_time + turn_red_time - turn_green_time
        )'''
        cam_bobj.move_to(
            new_location = [0, 0, 35],
            start_time = zoom_out_time,
            end_time = zoom_out_time + 2 * OBJECT_APPEARANCE_TIME / FRAME_RATE
        )

    def asymmetrical_inputs(self):
        cam_bobj, cam_swivel = cam_and_swivel(
            cam_location = [0, 0, 100],
            cam_rotation_euler = [0, 0, 0],
            cam_name = "Camera Bobject",
            swivel_location = [0, 5.1, -2],
            swivel_rotation_euler = [75 * math.pi / 180, 0, 135 * math.pi / 180],
            swivel_name = 'Cam swivel',
            #control_sun = True
        )
        cam_swivel.add_to_blender(appear_time = -1)
        cam_bobj.ref_obj.children[0].data.clip_end = 200

        rot_start = 78

        l_green_time = 80.5
        l_back_time = 85.5
        spin_time_1 = 83
        spins_1 = 5
        spin_duration_1 = 3

        r_red_time = 90.5
        r_back_time = 102.5
        spin_time_2 = 100
        spins_2 = 5
        spin_duration_2 = 3


        skin = bpy.data.objects['robertot']
        r_inner_ear = bpy.data.objects['inner ear_from microCT']
        l_inner_ear = bpy.data.objects['inner ear_from microCT.001']
        to_keep = [skin, r_inner_ear, l_inner_ear]
        for obj in bpy.data.objects:
            if obj not in to_keep:
                obj.hide = True
                obj.hide_render = True

        mix = skin.material_slots[0].material.node_tree.nodes['Mix Shader'].inputs[0]
        mix.default_value = 0.9


        #Prep inner ear materials
        slots = r_inner_ear.material_slots
        v_sys_mats = [
            slots[0].material,
            slots[1].material,
            slots[2].material,
            slots[3].material,
            slots[4].material
        ]
        #Set initial state for inner ear materials
        for mat in v_sys_mats:
            nodes = mat.node_tree.nodes
            mix = nodes['Mix Shader']
            mix.inputs[0].default_value = 0
            #princ = nodes['Principled BSDF']
            #color = princ.inputs[0]
            #color.default_value = [0, 1, 0, 1]

        #Make separate materials for left inner ear to animate separately
        for slot in l_inner_ear.material_slots:
            mat_copy = slot.material.copy()
            slot.material = mat_copy

        #Turn left inner ear green and back
        for slot in l_inner_ear.material_slots:
            nodes = slot.material.node_tree.nodes
            color = nodes['Principled BSDF'].inputs[0]
            initial_color = list(color.default_value)

            color.keyframe_insert(
                data_path = 'default_value',
                frame = l_green_time * FRAME_RATE
            )
            color.default_value = [0, 1, 0, 1]
            color.keyframe_insert(
                data_path = 'default_value',
                frame = l_green_time * FRAME_RATE + 2 * OBJECT_APPEARANCE_TIME
            )
            color.keyframe_insert(
                data_path = 'default_value',
                frame = l_back_time * FRAME_RATE
            )
            color.default_value = initial_color
            color.keyframe_insert(
                data_path = 'default_value',
                frame = l_back_time * FRAME_RATE + 2 * OBJECT_APPEARANCE_TIME
            )



        #Turn right inner ear red and back
        for mat in v_sys_mats:
            nodes = mat.node_tree.nodes
            color = nodes['Principled BSDF'].inputs[0]
            initial_color = list(color.default_value)

            color.keyframe_insert(
                data_path = 'default_value',
                frame = r_red_time * FRAME_RATE
            )
            color.default_value = [1, 0, 0, 1]
            color.keyframe_insert(
                data_path = 'default_value',
                frame = r_red_time * FRAME_RATE + 2 * OBJECT_APPEARANCE_TIME
            )
            color.keyframe_insert(
                data_path = 'default_value',
                frame = r_back_time * FRAME_RATE
            )
            color.default_value = initial_color
            color.keyframe_insert(
                data_path = 'default_value',
                frame = r_back_time * FRAME_RATE + 2 * OBJECT_APPEARANCE_TIME
            )

        #Spins
        skull = bpy.data.objects['Skull_Top']
        skull_bobj = bobject.Bobject(objects = [skull])
        skull_bobj.add_to_blender(appear_time = 0, unhide = False)
        skull_bobj.move_to(
            new_angle = [0, 0, spins_1 * 2 * math.pi],
            start_time = spin_time_1,
            end_time = spin_time_1 + spin_duration_1
        )

        skull_bobj.move_to(
            new_angle = [
                skull_bobj.ref_obj.rotation_euler[0],
                skull_bobj.ref_obj.rotation_euler[1],
                skull_bobj.ref_obj.rotation_euler[2] + spins_2 * 2 * math.pi,
            ],
            start_time = spin_time_2,
            end_time = spin_time_2 + spin_duration_2
        )



        cam_swivel.move_to(
            new_angle = [75 * math.pi / 180, 0, 45 * math.pi / 180],
            start_time = rot_start,
            end_time = r_red_time
        )
        cam_swivel.move_to(
            new_angle = [75 * math.pi / 180, 0, 135 * math.pi / 180],
            start_time = r_red_time,
            end_time = spin_time_2 + spin_duration_2
        )

        '''rate = 0.025
        cam_swivel.spin(
            axis = 2,
            spin_rate = rate,
            start_time = zoom_out_time - 1 / rate * 0.125
        )'''

    def long_term_symptoms(self):
        lt = tex_bobject.TexBobject(
            "\\text{Long-term effects}",
            location = [-12.5, 5.5, 0],
            #centered = True,
            typeface = 'arial',
            scale = 3
        )
        lt.add_to_blender(appear_time = 0)

        vnga = tex_bobject.TexBobject(
            "\\bullet\\text{Vertigo and nystagmus go away}",
            typeface = 'arial',
        )
        rb = tex_bobject.TexBobject(
            "\\bullet\\text{Reduced balance}",
            typeface = 'arial',
        )
        d = tex_bobject.TexBobject(
            "\\bullet\\text{Dizziness}",
            typeface = 'arial',
        )
        bv = tex_bobject.TexBobject(
            "\\bullet\\text{Blurred vision}",
            typeface = 'arial',
        )
        nhl = tex_bobject.TexBobject(
            "\\bullet\\text{Not hearing loss}",
            typeface = 'arial',
        )
        n = []
        for i in range(1, 4):
            n.append(nhl.lookup_table[0][i])
        for char in n:
            char.color_shift(
                color = COLORS_SCALED[2],
                start_time = 4,
                duration_time = 200,
            )


        contents = tex_complex.TexComplex(
            vnga, rb, d, bv, nhl,
            location = [-11.5, 2, 0],
            scale = 1.5,
            multiline = True
        )
        contents.add_to_blender(
            appear_time = 1,
            subbobject_timing = [0, 35, 70, 105, 140]
        )

    def transition_card(self):
        text = tex_bobject.TexBobject(
            #'\\text{The Cause of BPPV}',
            '\\text{Diagnosis and Treatment}',
            location = [0, 0, 0],
            scale = 2.5,
            color = 'color2',
            centered = True,
            typeface = 'arial'
        )
        text.add_to_blender(appear_time = -1, animate = False)

        for bobj in [text]:
            for handle in bobj.ref_obj.children:
                print(handle.name)
                print(handle.children[0].name)
                #For some reason, some handles have extra children
                try:
                    fade(
                        object = handle.children[0],
                        start_time = 0,
                        duration_time = 1,
                        fade_out = False
                    )
                except:
                    pass

    def end_card(self):
        logo = svg_bobject.SVGBobject(
            "UCSF_logo",
            #location = (-5, 3.75, 0), #Centered position
            #scale = 0.26, #Centered scale
            location = [0, 0, 0],
            scale = 0.121,
            color = 'color2',
            #centered = True,
        )
        baf = svg_bobject.SVGBobject(
            'BaFC_Arial',
            location = [5.2257280349731445, -0.26257357001304626, 0.0],
            scale = 2.23,
            color = 'color2',
            #centered = True,
        )
        logobaf = bobject.Bobject(
            logo, baf,
            location = [-11.57, 2.5, 0],
            #location = [0, 1.5, Z0],
            scale = 0.852,
            #centered = True
        )
        logobaf.add_to_blender(
            appear_time = 0,
            animate = False,
        )
        url = tex_bobject.TexBobject(
            '\\text{ohns.ucsf.edu/otology-neurotology/balance-and-falls}',
            location = [0, 0.8, 0],
            color = 'color2',
            name = 'url',
            typeface = 'arial',
            scale = 0.8,
            centered = True
        )
        url.add_to_blender(appear_time = 0)

        mpb_loc = [1, -4.25, 0]
        mpb = tex_bobject.TexBobject(
            '\\text{Made possible by:}',
            location = mpb_loc,
            color = 'color2',
            name = 'mpb',
            typeface = 'arial'
        )
        mzhf = tex_bobject.TexBobject(
            '\\text{Mount Zion Health Fund}',
            color = 'color2',
            scale = 1.2,
            location = [
                mpb_loc[0] + 0.5,
                mpb_loc[1] - 1.4,
                mpb_loc[2]
            ],
            name = 'mzhf',
            typeface = 'arial'
        )
        vpb_loc = [-13, -4.25, 0]
        vpb = tex_bobject.TexBobject(
            '\\text{Video produced by:}',
            color = 'color2',
            location = vpb_loc,
            name = 'vpb',
            typeface = 'arial'
        )
        jh = tex_bobject.TexBobject(
            '\\text{Justin Helps}',
            location = [
                vpb_loc[0] + 0.5,
                vpb_loc[1] - 1.4,
                vpb_loc[2]
            ],
            scale = 1.2,
            color = 'color2',
            name = 'jh',
            typeface = 'arial'
        )
        jds = tex_bobject.TexBobject(
            '\\text{Jeffrey D. Sharon, MD}',
            location = [
                vpb_loc[0] + 0.5,
                vpb_loc[1] - 2.8,
                vpb_loc[2]
            ],
            scale = 1.2,
            color = 'color2',
            name = 'jds',
            typeface = 'arial'
        )

        for bobj in [mpb, mzhf, vpb, jh, jds]:
            bobj.add_to_blender(
                appear_time = 0,
                animate = False
            )
